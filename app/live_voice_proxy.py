from __future__ import annotations

import base64
import hashlib
import ipaddress
import os
import socket
import ssl
import struct
import threading
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from .config import AppConfig


WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
MAX_WEBSOCKET_PAYLOAD_BYTES = 16_777_216


class LiveVoiceProxyError(RuntimeError):
    pass


@dataclass(frozen=True)
class WebSocketFrame:
    fin: bool
    opcode: int
    payload: bytes
    masked: bool


@dataclass(frozen=True)
class ConnectedWebSocket:
    sock: socket.socket
    reader: "SocketReader"


class SocketReader:
    def __init__(self, sock: socket.socket, initial: bytes = b""):
        self.sock = sock
        self._buffer = bytearray(initial)

    def read(self, size: int) -> bytes:
        while len(self._buffer) < size:
            chunk = self.sock.recv(max(4096, size - len(self._buffer)))
            if not chunk:
                break
            self._buffer.extend(chunk)
        data = bytes(self._buffer[:size])
        del self._buffer[:size]
        return data

    def read_until(self, marker: bytes, limit: int) -> bytes:
        while marker not in self._buffer:
            if len(self._buffer) > limit:
                raise LiveVoiceProxyError("Upstream WebSocket handshake response is too large.")
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            self._buffer.extend(chunk)
        index = self._buffer.find(marker)
        if index < 0:
            raise LiveVoiceProxyError("Upstream WebSocket handshake response was incomplete.")
        end = index + len(marker)
        data = bytes(self._buffer[:end])
        del self._buffer[:end]
        return data


def is_websocket_upgrade(headers: Any) -> bool:
    connection = str(headers.get("Connection", "")).lower()
    upgrade = str(headers.get("Upgrade", "")).lower()
    return (
        upgrade == "websocket"
        and "upgrade" in {part.strip() for part in connection.split(",")}
        and bool(str(headers.get("Sec-WebSocket-Key", "")).strip())
    )


def websocket_accept_value(sec_websocket_key: str) -> str:
    raw = (sec_websocket_key.strip() + WEBSOCKET_GUID).encode("ascii")
    return base64.b64encode(hashlib.sha1(raw).digest()).decode("ascii")


def build_websocket_frame(payload: bytes, *, opcode: int, mask: bool, fin: bool = True, mask_key: bytes | None = None) -> bytes:
    first = (0x80 if fin else 0) | (opcode & 0x0F)
    length = len(payload)
    if length <= 125:
        header = bytearray([first, length])
    elif length <= 0xFFFF:
        header = bytearray([first, 126])
        header.extend(struct.pack("!H", length))
    else:
        header = bytearray([first, 127])
        header.extend(struct.pack("!Q", length))

    if not mask:
        return bytes(header) + payload

    key = mask_key or os.urandom(4)
    if len(key) != 4:
        raise ValueError("WebSocket mask key must be exactly 4 bytes.")
    header[1] |= 0x80
    return bytes(header) + key + _xor_mask(payload, key)


def read_websocket_frame(
    reader: Any,
    *,
    expect_masked: bool | None = None,
    max_payload_bytes: int = MAX_WEBSOCKET_PAYLOAD_BYTES,
) -> WebSocketFrame:
    header = _read_exact(reader, 2)
    first, second = header[0], header[1]
    fin = bool(first & 0x80)
    opcode = first & 0x0F
    masked = bool(second & 0x80)
    length = second & 0x7F

    if expect_masked is not None and masked != expect_masked:
        side = "masked" if expect_masked else "unmasked"
        raise LiveVoiceProxyError(f"Expected {side} WebSocket frame.")
    if length == 126:
        length = struct.unpack("!H", _read_exact(reader, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _read_exact(reader, 8))[0]
    if length > max_payload_bytes:
        raise LiveVoiceProxyError("WebSocket frame is too large.")

    mask_key = _read_exact(reader, 4) if masked else b""
    payload = _read_exact(reader, length) if length else b""
    if masked:
        payload = _xor_mask(payload, mask_key)
    return WebSocketFrame(fin=fin, opcode=opcode, payload=payload, masked=masked)


def connect_gemini_live_websocket(websocket_url: str, config: AppConfig) -> ConnectedWebSocket:
    parsed = urlparse(websocket_url)
    if parsed.scheme not in {"ws", "wss"}:
        raise LiveVoiceProxyError("Live Voice upstream URL must be ws:// or wss://.")
    if not parsed.hostname:
        raise LiveVoiceProxyError("Live Voice upstream URL is missing a host.")

    use_tls = parsed.scheme == "wss"
    port = parsed.port or (443 if use_tls else 80)
    timeout = max(1, config.live_voice_timeout_seconds)
    raw_sock = _open_tcp_connection(parsed.hostname, port, config, timeout)
    sock: socket.socket = raw_sock

    try:
        if use_tls:
            context = ssl.create_default_context()
            sock = context.wrap_socket(raw_sock, server_hostname=parsed.hostname)
        sock.settimeout(timeout)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        sec_key = base64.b64encode(os.urandom(16)).decode("ascii")
        host_header = _host_header(parsed.hostname, port, use_tls)
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host_header}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {sec_key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "User-Agent: coocking-cart-live-voice-proxy/1.0\r\n"
            "\r\n"
        )
        sock.sendall(request.encode("ascii"))
        reader = SocketReader(sock)
        response = reader.read_until(b"\r\n\r\n", 65_536)
        status_code, headers = _parse_http_upgrade_response(response)
        if status_code != 101:
            raise LiveVoiceProxyError(f"Gemini Live WebSocket upgrade failed with HTTP {status_code}.")
        expected_accept = websocket_accept_value(sec_key)
        if headers.get("sec-websocket-accept", "") != expected_accept:
            raise LiveVoiceProxyError("Gemini Live WebSocket upgrade returned an invalid accept key.")
        sock.settimeout(None)
        return ConnectedWebSocket(sock=sock, reader=reader)
    except Exception:
        _close_socket(sock)
        raise


def relay_websocket(
    *,
    browser_reader: Any,
    browser_writer: Any,
    browser_socket: socket.socket,
    upstream: ConnectedWebSocket,
) -> None:
    stop = threading.Event()

    def close_all() -> None:
        _close_socket(upstream.sock)
        _close_socket(browser_socket)

    def browser_to_upstream() -> None:
        try:
            while not stop.is_set():
                frame = read_websocket_frame(browser_reader, expect_masked=True)
                upstream.sock.sendall(
                    build_websocket_frame(frame.payload, opcode=frame.opcode, mask=True, fin=frame.fin)
                )
                if frame.opcode == 0x8:
                    break
        except Exception:
            pass
        finally:
            stop.set()
            close_all()

    def upstream_to_browser() -> None:
        try:
            while not stop.is_set():
                frame = read_websocket_frame(upstream.reader, expect_masked=False)
                browser_writer.write(
                    build_websocket_frame(frame.payload, opcode=frame.opcode, mask=False, fin=frame.fin)
                )
                flush = getattr(browser_writer, "flush", None)
                if flush:
                    flush()
                if frame.opcode == 0x8:
                    break
        except Exception:
            pass
        finally:
            stop.set()
            close_all()

    threads = [
        threading.Thread(target=browser_to_upstream, daemon=True),
        threading.Thread(target=upstream_to_browser, daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def _open_tcp_connection(host: str, port: int, config: AppConfig, timeout: int) -> socket.socket:
    if config.live_voice_socks5_host:
        return _open_socks5_connection(host, port, config, timeout)
    return socket.create_connection((host, port), timeout=timeout)


def _open_socks5_connection(host: str, port: int, config: AppConfig, timeout: int) -> socket.socket:
    proxy = socket.create_connection((config.live_voice_socks5_host, config.live_voice_socks5_port), timeout=timeout)
    proxy.settimeout(timeout)
    try:
        methods = [0x00]
        if config.live_voice_socks5_username or config.live_voice_socks5_password:
            methods.append(0x02)
        proxy.sendall(bytes([0x05, len(methods), *methods]))
        version, method = _recv_exact(proxy, 2)
        if version != 0x05 or method == 0xFF:
            raise LiveVoiceProxyError("SOCKS5 proxy did not accept an authentication method.")
        if method == 0x02:
            _authenticate_socks5(proxy, config.live_voice_socks5_username, config.live_voice_socks5_password)
        elif method != 0x00:
            raise LiveVoiceProxyError("SOCKS5 proxy selected an unsupported authentication method.")

        address = _socks5_address(host)
        proxy.sendall(b"\x05\x01\x00" + address + struct.pack("!H", port))
        response = _recv_exact(proxy, 4)
        if response[0] != 0x05:
            raise LiveVoiceProxyError("SOCKS5 proxy returned an invalid response.")
        if response[1] != 0x00:
            raise LiveVoiceProxyError(f"SOCKS5 proxy connect failed with code {response[1]}.")
        _read_socks5_bound_address(proxy, response[3])
        _recv_exact(proxy, 2)
        return proxy
    except Exception:
        _close_socket(proxy)
        raise


def _authenticate_socks5(sock: socket.socket, username: str, password: str) -> None:
    username_bytes = username.encode("utf-8")
    password_bytes = password.encode("utf-8")
    if len(username_bytes) > 255 or len(password_bytes) > 255:
        raise LiveVoiceProxyError("SOCKS5 username/password is too long.")
    sock.sendall(b"\x01" + bytes([len(username_bytes)]) + username_bytes + bytes([len(password_bytes)]) + password_bytes)
    version, status = _recv_exact(sock, 2)
    if version != 0x01 or status != 0x00:
        raise LiveVoiceProxyError("SOCKS5 username/password authentication failed.")


def _socks5_address(host: str) -> bytes:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        host_bytes = host.encode("idna")
        if len(host_bytes) > 255:
            raise LiveVoiceProxyError("SOCKS5 destination host is too long.")
        return b"\x03" + bytes([len(host_bytes)]) + host_bytes
    if address.version == 4:
        return b"\x01" + address.packed
    return b"\x04" + address.packed


def _read_socks5_bound_address(sock: socket.socket, address_type: int) -> None:
    if address_type == 0x01:
        _recv_exact(sock, 4)
    elif address_type == 0x03:
        length = _recv_exact(sock, 1)[0]
        _recv_exact(sock, length)
    elif address_type == 0x04:
        _recv_exact(sock, 16)
    else:
        raise LiveVoiceProxyError("SOCKS5 proxy returned an unknown address type.")


def _parse_http_upgrade_response(raw: bytes) -> tuple[int, dict[str, str]]:
    text = raw.decode("iso-8859-1")
    lines = text.split("\r\n")
    parts = lines[0].split(" ", 2)
    if len(parts) < 2 or not parts[1].isdigit():
        raise LiveVoiceProxyError("Upstream WebSocket handshake returned an invalid status line.")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
    return int(parts[1]), headers


def _host_header(host: str, port: int, use_tls: bool) -> str:
    default_port = 443 if use_tls else 80
    if port == default_port:
        return host
    return f"{host}:{port}"


def _read_exact(reader: Any, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = reader.read(size - len(chunks))
        if not chunk:
            raise EOFError("WebSocket stream closed.")
        chunks.extend(chunk)
    return bytes(chunks)


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise LiveVoiceProxyError("Socket closed before response was complete.")
        chunks.extend(chunk)
    return bytes(chunks)


def _xor_mask(payload: bytes, key: bytes) -> bytes:
    return bytes(byte ^ key[index % 4] for index, byte in enumerate(payload))


def _close_socket(sock: socket.socket) -> None:
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass
