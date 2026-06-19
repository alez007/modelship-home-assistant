"""Wyoming event handler: one instance per client connection."""

from __future__ import annotations

import logging

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from .client import ModelshipClient
from .settings import Settings
from .voices import DEFAULT_VOICE

_LOGGER = logging.getLogger(__name__)


class BridgeHandler(AsyncEventHandler):
    def __init__(
        self,
        info: Info,
        client: ModelshipClient,
        settings: Settings,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._info_event = info.event()
        self._client = client
        self._settings = settings
        # STT accumulation state for the current utterance.
        self._buffer = bytearray()
        self._rate = 16000
        self._width = 2
        self._channels = 1
        self._language = settings.default_language

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self._info_event)
            return True

        # --- STT: Transcribe → AudioStart → AudioChunk* → AudioStop ---
        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
            return True

        if AudioStart.is_type(event.type):
            start = AudioStart.from_event(event)
            self._rate, self._width, self._channels = start.rate, start.width, start.channels
            self._buffer = bytearray()
            return True

        if AudioChunk.is_type(event.type):
            self._buffer += AudioChunk.from_event(event).audio
            return True

        if AudioStop.is_type(event.type):
            text = await self._client.transcribe(
                bytes(self._buffer), self._rate, self._width, self._channels, self._language
            )
            _LOGGER.debug("STT → %r", text)
            await self.write_event(Transcript(text=text).event())
            self._buffer = bytearray()
            # One transcription per connection (Home Assistant reconnects).
            return False

        # --- TTS: Synthesize → AudioStart → AudioChunk* → AudioStop ---
        if Synthesize.is_type(event.type):
            await self._synthesize(Synthesize.from_event(event))
            return True

        return True

    async def _synthesize(self, synthesize: Synthesize) -> None:
        voice = synthesize.voice.name if synthesize.voice else (self._settings.default_voice or DEFAULT_VOICE)
        _LOGGER.debug("TTS voice=%s text=%r", voice, synthesize.text)
        pcm, rate, width, channels = await self._client.synthesize(synthesize.text, voice)

        await self.write_event(AudioStart(rate=rate, width=width, channels=channels).event())
        step = max(1, self._settings.chunk_frames) * width * channels
        for offset in range(0, len(pcm), step):
            await self.write_event(
                AudioChunk(
                    audio=pcm[offset : offset + step],
                    rate=rate,
                    width=width,
                    channels=channels,
                ).event()
            )
        await self.write_event(AudioStop().event())
