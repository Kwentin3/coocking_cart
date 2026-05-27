from __future__ import annotations

from .config import AppConfig


def build_batch_transcription_prompt(config: AppConfig) -> str:
    return _build_transcription_prompt(config, target="текст", final_text_only=True)


def build_live_voice_transcription_instruction(config: AppConfig) -> str:
    return _build_transcription_prompt(config, target="черновик сообщения в чат", final_text_only=False)


def _build_transcription_prompt(config: AppConfig, *, target: str, final_text_only: bool) -> str:
    override = config.voice_transcription_prompt_override.strip()
    if override:
        return override

    language = config.voice_transcription_language.strip()
    script = config.voice_transcription_script.strip()
    latin_allowlist = config.voice_transcription_latin_allowlist.strip()
    domain_terms = config.voice_transcription_domain_terms.strip()
    unclear_marker = config.voice_transcription_unclear_marker.strip() or "[неразборчиво]"
    extra_instruction = config.voice_transcription_extra_instruction.strip()

    lines = [
        f"Транскрибируй речь пользователя для результата: {target}.",
        "Не отвечай на содержание, не суммаризируй и не отправляй сообщение.",
        "Не исправляй смысл; сохраняй числа, единицы измерения, проценты, температуру и время максимально точно.",
    ]
    if language:
        lines.append(f"Предпочтительный язык транскрипта: {language}.")
    if script:
        lines.append(
            f"Предпочтительный алфавит/скрипт: {script}. Не транслитерируй слова выбранного языка другим алфавитом."
        )
    if latin_allowlist:
        lines.append(
            "Латиницу оставляй только для явно продиктованных кодов, артикулов, брендов, API-названий "
            f"или allowlist-терминов: {latin_allowlist}."
        )
    else:
        lines.append("Латиницу оставляй только для явно продиктованных кодов, артикулов, брендов или API-названий.")
    if domain_terms:
        lines.append(f"Предметные термины, которые нужно сохранять: {domain_terms}.")
    lines.append(f"Если фрагмент неразборчив, пометь его как {unclear_marker}.")
    if final_text_only:
        lines.append("Верни только текст транскрипта.")
    if extra_instruction:
        lines.append(extra_instruction)
    return "\n".join(lines)
