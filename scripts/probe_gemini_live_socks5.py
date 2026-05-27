from __future__ import annotations

import argparse
import base64
import json
import socket
import struct
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import is_blank_or_placeholder, load_config
from app.live_voice import live_voice_setup, make_live_voice_adapter
from app.live_voice_proxy import (
    ConnectedWebSocket,
    build_websocket_frame,
    connect_gemini_live_websocket,
    read_websocket_frame,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe Gemini Live streaming WSS through configured SOCKS5 egress.",
    )
    parser.add_argument("--config-only", action="store_true", help="Validate local env/config without network calls.")
    parser.add_argument("--allow-direct", action="store_true", help="Allow running without LIVE_VOICE_SOCKS5_HOST.")
    parser.add_argument(
        "--auth",
        choices=("ephemeral", "api-key"),
        default="ephemeral",
        help="Use ephemeral constrained token or backend-only API key WSS auth.",
    )
    parser.add_argument("--api-version", choices=("v1alpha", "v1beta"), default="v1beta")
    parser.add_argument("--duration-seconds", type=float, default=1.5, help="How much silent PCM16 audio to stream.")
    parser.add_argument("--chunk-ms", type=int, default=100, help="Silent audio chunk size in milliseconds.")
    parser.add_argument("--receive-seconds", type=float, default=8.0, help="How long to wait for server events after audio end.")
    parser.add_argument("--max-events", type=int, default=12, help="Maximum server events to print.")
    parser.add_argument("--print-events", action="store_true", help="Print sanitized Gemini Live event keys.")
    args = parser.parse_args()

    config = load_config()
    print_config_summary(config)
    validation_errors = validate_config(config, allow_direct=args.allow_direct)
    if validation_errors:
        for error in validation_errors:
            print(f"config_error: {error}", file=sys.stderr)
        return 2
    if args.config_only:
        print("config_ok: true")
        return 0

    if args.auth == "ephemeral":
        adapter = make_live_voice_adapter(config)
        token_result = adapter.create_token()
        if not token_result.ok:
            print("token_ok: false", file=sys.stderr)
            print(f"error: {token_result.error or 'unknown token error'}", file=sys.stderr)
            if token_result.admin_hint:
                print(f"admin_hint: {token_result.admin_hint[:500]}", file=sys.stderr)
            return 3
        print("token_ok: true")
        websocket_url = token_result.websocket_url
        setup = token_result.setup or live_voice_setup(config)
    else:
        print("token_ok: skipped")
        websocket_url = api_key_websocket_url(config, api_version=args.api_version)
        setup = live_voice_setup(config)

    websocket: ConnectedWebSocket | None = None
    try:
        websocket = connect_gemini_live_websocket(websocket_url, config)
        print("wss_connect_ok: true")
        send_json(websocket, {"setup": setup})
        wait_for_setup_complete(websocket, timeout_seconds=max(4.0, args.receive_seconds), print_events=args.print_events)
        print("setup_complete: true")
        stream_silence(
            websocket,
            sample_rate=config.live_voice_input_sample_rate,
            duration_seconds=max(0.0, args.duration_seconds),
            chunk_ms=max(20, args.chunk_ms),
        )
        print("audio_stream_end_sent: true")
        event_count = drain_events(
            websocket,
            timeout_seconds=max(0.5, args.receive_seconds),
            max_events=max(1, args.max_events),
            print_events=args.print_events,
        )
        print(f"events_seen: {event_count}")
        send_close(websocket)
    except Exception as exc:
        print(f"probe_failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        hint = socks5_error_hint(str(exc))
        if hint:
            print(f"hint: {hint}", file=sys.stderr)
        return 4
    finally:
        if websocket is not None:
            close_socket(websocket.sock)

    print("probe_ok: true")
    return 0


def print_config_summary(config: Any) -> None:
    socks_enabled = bool(config.live_voice_socks5_host)
    print("config:")
    print(f"  provider: {config.live_voice_provider}")
    print(f"  model: {config.live_voice_model}")
    print(f"  transport: {config.live_voice_transport}")
    print(f"  sample_rate: {config.live_voice_input_sample_rate}")
    print(f"  live_voice_api_key: {'set' if not is_blank_or_placeholder(config.live_voice_api_key) else 'missing'}")
    print(f"  socks5_host: {'set' if socks_enabled else 'missing'}")
    print(f"  socks5_port: {config.live_voice_socks5_port if socks_enabled else 'n/a'}")
    print(f"  socks5_username: {'set' if config.live_voice_socks5_username else 'missing'}")
    print(f"  socks5_password: {'set' if config.live_voice_socks5_password else 'missing'}")


def validate_config(config: Any, *, allow_direct: bool) -> list[str]:
    errors: list[str] = []
    if config.live_voice_provider != "gemini":
        errors.append("LIVE_VOICE_PROVIDER must be gemini.")
    if is_blank_or_placeholder(config.live_voice_model):
        errors.append("LIVE_VOICE_MODEL is missing.")
    if is_blank_or_placeholder(config.live_voice_api_key):
        errors.append("LIVE_VOICE_API_KEY/STT_API_KEY/LLM_API_KEY/GEMINI_API_KEY is missing.")
    if not allow_direct and not config.live_voice_socks5_host:
        errors.append("LIVE_VOICE_SOCKS5_HOST is missing. Pass --allow-direct only for a non-SOCKS control probe.")
    if config.live_voice_socks5_host and config.live_voice_socks5_port <= 0:
        errors.append("LIVE_VOICE_SOCKS5_PORT must be positive.")
    return errors


def api_key_websocket_url(config: Any, *, api_version: str) -> str:
    base = (config.live_voice_base_url or "https://generativelanguage.googleapis.com").rstrip("/")
    if base.startswith("https://"):
        base = "wss://" + base.removeprefix("https://")
    elif base.startswith("http://"):
        base = "ws://" + base.removeprefix("http://")
    else:
        raise ValueError("LIVE_VOICE_BASE_URL must be http(s) when set.")
    encoded_key = quote(config.live_voice_api_key, safe="")
    return f"{base}/ws/google.ai.generativelanguage.{api_version}.GenerativeService.BidiGenerateContent?key={encoded_key}"


def socks5_error_hint(message: str) -> str:
    hints = {
        "1": "SOCKS5 general server failure.",
        "2": "SOCKS5 connection not allowed by ruleset; check proxy ACL, destination allowlist, or egress policy.",
        "3": "SOCKS5 network unreachable.",
        "4": "SOCKS5 host unreachable.",
        "5": "SOCKS5 connection refused by destination.",
        "6": "SOCKS5 TTL expired.",
        "7": "SOCKS5 command not supported.",
        "8": "SOCKS5 address type not supported.",
    }
    marker = "SOCKS5 proxy connect failed with code "
    if marker not in message:
        return ""
    code = message.split(marker, 1)[1].split(".", 1)[0].strip()
    return hints.get(code, "")


def send_json(websocket: ConnectedWebSocket, payload: dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    websocket.sock.sendall(build_websocket_frame(raw, opcode=0x1, mask=True))


def wait_for_setup_complete(websocket: ConnectedWebSocket, *, timeout_seconds: float, print_events: bool) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        payload = receive_json_event(websocket, deadline)
        if payload is None:
            continue
        if print_events:
            print_event_summary(payload)
        if payload.get("setupComplete") is not None:
            return
    raise TimeoutError("Gemini Live setupComplete was not received.")


def stream_silence(websocket: ConnectedWebSocket, *, sample_rate: int, duration_seconds: float, chunk_ms: int) -> None:
    if duration_seconds > 0:
        samples_per_chunk = max(1, int(sample_rate * chunk_ms / 1000))
        chunk = b"\x00\x00" * samples_per_chunk
        encoded = base64.b64encode(chunk).decode("ascii")
        chunks = max(1, int(duration_seconds * 1000 / chunk_ms))
        for _index in range(chunks):
            send_json(
                websocket,
                {
                    "realtimeInput": {
                        "audio": {
                            "data": encoded,
                            "mimeType": f"audio/pcm;rate={sample_rate}",
                        }
                    }
                },
            )
            time.sleep(chunk_ms / 1000)
    send_json(websocket, {"realtimeInput": {"audioStreamEnd": True}})


def drain_events(
    websocket: ConnectedWebSocket,
    *,
    timeout_seconds: float,
    max_events: int,
    print_events: bool,
) -> int:
    deadline = time.monotonic() + timeout_seconds
    seen = 0
    while seen < max_events and time.monotonic() < deadline:
        payload = receive_json_event(websocket, deadline)
        if payload is None:
            continue
        seen += 1
        if print_events:
            print_event_summary(payload)
        if payload.get("goAway") or payload.get("sessionResumptionUpdate"):
            break
    return seen


def receive_json_event(websocket: ConnectedWebSocket, deadline: float) -> dict[str, Any] | None:
    websocket.sock.settimeout(max(0.1, deadline - time.monotonic()))
    try:
        frame = read_websocket_frame(websocket.reader, expect_masked=False)
    except socket.timeout:
        return None
    if frame.opcode == 0x8:
        code = ""
        if len(frame.payload) >= 2:
            code = str(struct.unpack("!H", frame.payload[:2])[0])
        reason = frame.payload[2:].decode("utf-8", errors="replace") if len(frame.payload) > 2 else ""
        raise RuntimeError(f"upstream closed WebSocket code={code} reason={reason}")
    if frame.opcode == 0x9:
        websocket.sock.sendall(build_websocket_frame(frame.payload, opcode=0xA, mask=True))
        return None
    if frame.opcode not in {0x1, 0x2}:
        return None
    text = frame.payload.decode("utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        print(f"non_json_event_bytes: {len(frame.payload)}")
        return None
    return payload if isinstance(payload, dict) else None


def print_event_summary(payload: dict[str, Any]) -> None:
    keys = ",".join(sorted(payload.keys()))
    server_content = payload.get("serverContent") if isinstance(payload.get("serverContent"), dict) else {}
    transcription = server_content.get("inputTranscription") if isinstance(server_content, dict) else None
    transcript_len = 0
    if isinstance(transcription, dict):
        transcript_len = len(str(transcription.get("text") or ""))
    print(f"event_keys: {keys} transcript_len={transcript_len}")


def send_close(websocket: ConnectedWebSocket) -> None:
    payload = struct.pack("!H", 1000) + b"probe complete"
    websocket.sock.sendall(build_websocket_frame(payload, opcode=0x8, mask=True))


def close_socket(sock: socket.socket) -> None:
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass


if __name__ == "__main__":
    raise SystemExit(main())
