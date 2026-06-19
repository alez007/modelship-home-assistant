import struct

import httpx
import pytest

from bridge.audio import pcm_to_wav
from bridge.client import ModelshipClient
from bridge.settings import Settings


def _settings() -> Settings:
    return Settings(
        base_url="http://modelship",
        models_config_path="/x",
        uri="tcp://0.0.0.0:10300",
        default_voice=None,
        default_language="en",
        log_level="INFO",
        ready_timeout_s=1,
        request_timeout_s=5,
        chunk_frames=1024,
    )


def _client(handler, usecases) -> ModelshipClient:
    client = ModelshipClient(_settings(), usecases)
    client._http = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://modelship")
    return client


@pytest.mark.asyncio
async def test_transcribe_posts_wav_and_returns_text():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = request.url.path
        seen["body"] = request.content
        return httpx.Response(200, json={"text": "  hello world  "})

    client = _client(handler, {"transcription": "whisper"})
    pcm = struct.pack("<" + "h" * 80, *([7] * 80))
    text = await client.transcribe(pcm, 16000, 2, 1, "en")

    assert text == "hello world"
    assert seen["url"] == "/v1/audio/transcriptions"
    assert b"whisper" in seen["body"]  # model field in multipart


@pytest.mark.asyncio
async def test_synthesize_unwraps_wav():
    pcm = struct.pack("<" + "h" * 120, *([5] * 120))

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/audio/speech"
        return httpx.Response(200, content=pcm_to_wav(pcm, 24000, 2, 1))

    client = _client(handler, {"tts": "kokoro"})
    out_pcm, rate, width, channels = await client.synthesize("hi", "af_heart")

    assert (rate, width, channels) == (24000, 2, 1)
    assert out_pcm == pcm


@pytest.mark.asyncio
async def test_transcribe_without_model_raises():
    client = _client(lambda r: httpx.Response(200), {})
    with pytest.raises(RuntimeError):
        await client.transcribe(b"", 16000, 2, 1, None)
