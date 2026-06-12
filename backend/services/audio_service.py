"""
Audio service — converts topic summaries to MP3 using gTTS.
gTTS is blocking, so all calls are wrapped in run_in_executor.
Audio files are cached at AUDIO_CACHE_PATH/{topic_id}.mp3
"""

import os
import asyncio
import logging
from pathlib import Path
from gtts import gTTS

logger = logging.getLogger(__name__)

AUDIO_CACHE_PATH = os.getenv("AUDIO_CACHE_PATH", "./audio_cache")


def _ensure_cache_dir():
    Path(AUDIO_CACHE_PATH).mkdir(parents=True, exist_ok=True)


def _get_audio_path(topic_id: str) -> str:
    return os.path.join(AUDIO_CACHE_PATH, f"{topic_id}.mp3")


def _generate_audio_sync(text: str, topic_id: str) -> str:
    _ensure_cache_dir()
    output_path = _get_audio_path(topic_id)
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)
    logger.info(f"Generated audio for '{topic_id}' at {output_path}")
    return output_path


async def generate_audio(text: str, topic_id: str) -> str:
    """
    Generate MP3 from text using gTTS (async wrapper).
    Returns the file path of the generated MP3.
    """
    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(None, _generate_audio_sync, text, topic_id)
    return path


def audio_exists(topic_id: str) -> bool:
    return os.path.exists(_get_audio_path(topic_id))


def get_audio_file_path(topic_id: str) -> str | None:
    path = _get_audio_path(topic_id)
    return path if os.path.exists(path) else None
