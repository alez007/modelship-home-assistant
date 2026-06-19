"""Async HTTP client for modelship's OpenAI-compatible audio endpoints."""

from __future__ import annotations

import logging

import httpx

from .audio import pcm_to_wav, wav_to_pcm
from .settings import Settings

_LOGGER = logging.getLogger(__name__)


class ModelshipClient:
    def __init__(self, settings: Settings, usecases: dict[str, str]) -> None:
        self._settings = settings
        self._stt_model = usecases.get("transcription")
        self._tts_model = usecases.get("tts")
        self._http = httpx.AsyncClient(
            base_url=settings.base_url,
            timeout=httpx.Timeout(settings.request_timeout_s, connect=10.0),
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def transcribe(
        self, pcm: bytes, rate: int, width: int, channels: int, language: str | None
    ) -> str:
        """POST audio to /v1/audio/transcriptions → recognized text."""
        if not self._stt_model:
            raise RuntimeError("no transcription model is configured")
        wav = pcm_to_wav(pcm, rate, width, channels)
        data: dict[str, str] = {"model": self._stt_model, "response_format": "json"}
        if language:
            data["language"] = language
        files = {"file": ("audio.wav", wav, "audio/wav")}
        resp = await self._http.post("/v1/audio/transcriptions", data=data, files=files)
        resp.raise_for_status()
        return (resp.json().get("text") or "").strip()

    async def synthesize(self, text: str, voice: str) -> tuple[bytes, int, int, int]:
        """POST text to /v1/audio/speech → (pcm, rate, width, channels)."""
        if not self._tts_model:
            raise RuntimeError("no tts model is configured")
        payload = {
            "model": self._tts_model,
            "input": text,
            "voice": voice,
            "response_format": "wav",
        }
        resp = await self._http.post("/v1/audio/speech", json=payload)
        resp.raise_for_status()
        return wav_to_pcm(resp.content)
