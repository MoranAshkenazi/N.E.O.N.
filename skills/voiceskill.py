import asyncio
import base64
import re
import edge_tts


def _clean_markdown_for_speech(text: str) -> str:
    """Cleans markdown formatting so TTS reads clean, natural spoken text."""
    # הסרת קישורים [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # הסרת כוכביות הדגשה ורשימות (**bold**, *bullet*, etc.)
    text = re.sub(r"[\*\_~`#>]+", " ", text)
    # הסרת מקפים של רשימות בתחילת שורה
    text = re.sub(r"^\s*-\s+", "", text, flags=re.MULTILINE)
    # צמצום רווחים כפולים
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def _generate_audio_bytes(text: str) -> bytes:
    """Generates high-quality neural voice audio data."""
    # מנקים את הטקסט מקוד וסימני עיצוב לפני ההקראה
    spoken_text = _clean_markdown_for_speech(text)
    if not spoken_text:
        return b""

    is_hebrew = any("\u0590" <= c <= "\u05ea" for c in spoken_text[:100])

    hebrew_voice = "he-IL-AvriNeural"
    english_voice = "en-GB-RyanNeural"

    voice = hebrew_voice if is_hebrew else english_voice

    communicate = edge_tts.Communicate(
        text=spoken_text, voice=voice, pitch="-18Hz", rate="+0%"
    )

    audio_data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
    return bytes(audio_data)


def get_audio_bytes(text: str) -> bytes:
    """Synchronous helper that returns raw audio bytes."""
    try:
        return asyncio.run(_generate_audio_bytes(text))
    except Exception as e:
        print(f"[VOICE SYNTH ERROR]: {e}")
        return b""


def generate_audio_b64(text: str) -> str:
    """Synchronous helper that returns base64 encoded audio string."""
    data = get_audio_bytes(text)
    return base64.b64encode(data).decode("utf-8") if data else ""