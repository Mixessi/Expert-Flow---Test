import asyncio
import base64
import io
import tempfile
from typing import AsyncGenerator

import httpx

from app.config import settings


class AudioBuffer:
    """Buffers audio chunks and yields segments for ASR processing."""

    def __init__(self, segment_duration_ms: int = 3000):
        self.segment_duration_ms = segment_duration_ms
        self.buffer: list[bytes] = []
        self.buffer_duration_ms = 0
        self.chunk_duration_ms = 250

    def add_chunk(self, base64_audio: str) -> bytes | None:
        """Add a chunk and return a segment if buffer is full."""
        audio_data = base64.b64decode(base64_audio)
        self.buffer.append(audio_data)
        self.buffer_duration_ms += self.chunk_duration_ms

        if self.buffer_duration_ms >= self.segment_duration_ms:
            segment = b"".join(self.buffer)
            self.buffer = []
            self.buffer_duration_ms = 0
            return segment
        return None

    def flush(self) -> bytes | None:
        """Flush remaining buffer."""
        if self.buffer:
            segment = b"".join(self.buffer)
            self.buffer = []
            self.buffer_duration_ms = 0
            return segment
        return None


async def transcribe_audio(audio_data: bytes) -> dict:
    """Send audio to OpenAI Whisper API for transcription."""
    if not settings.whisper_api_key:
        # Mock response for development without API key
        return {
            "text": "[Transcription placeholder - configure WHISPER_API_KEY]",
            "confidence": 0.0,
        }

    async with httpx.AsyncClient() as client:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_data)
            f.flush()
            f.seek(0)

            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {settings.whisper_api_key}"},
                files={"file": ("audio.webm", open(f.name, "rb"), "audio/webm")},
                data={"model": "whisper-1", "language": "zh", "response_format": "verbose_json"},
                timeout=10.0,
            )

    if response.status_code == 200:
        result = response.json()
        return {
            "text": result.get("text", ""),
            "confidence": result.get("segments", [{}])[0].get("avg_logprob", 0),
        }
    return {"text": "", "confidence": 0.0}
