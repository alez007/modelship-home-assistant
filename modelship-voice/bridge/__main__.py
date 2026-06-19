"""Bridge entrypoint: wait for modelship, discover models, serve Wyoming."""

from __future__ import annotations

import asyncio
import logging
import time
from functools import partial

import httpx
from wyoming.server import AsyncServer

from .client import ModelshipClient
from .discovery import discover_models
from .handler import BridgeHandler
from .settings import Settings
from .wyoming_info import build_info

_LOGGER = logging.getLogger(__name__)


async def _wait_for_ready(settings: Settings) -> None:
    """Block until modelship's /readyz reports ready (or time out)."""
    deadline = time.monotonic() + settings.ready_timeout_s
    async with httpx.AsyncClient(timeout=10.0) as http:
        while True:
            try:
                resp = await http.get(f"{settings.base_url}/readyz")
                if resp.status_code == 200 and resp.json().get("ready"):
                    return
            except Exception:  # modelship not up yet — keep polling
                pass
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"modelship at {settings.base_url} not ready after {settings.ready_timeout_s:.0f}s"
                )
            await asyncio.sleep(3.0)


async def main() -> None:
    settings = Settings.from_env()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    _LOGGER.info("Waiting for modelship at %s ...", settings.base_url)
    await _wait_for_ready(settings)

    usecases = discover_models(settings.models_config_path)
    if "transcription" not in usecases and "tts" not in usecases:
        raise SystemExit(
            "modelship serves neither a 'transcription' nor a 'tts' model — "
            "nothing for the Wyoming bridge to expose. Use a voice profile "
            "(assistant/everything)."
        )

    client = ModelshipClient(settings, usecases)
    info = build_info(usecases)

    server = AsyncServer.from_uri(settings.uri)
    _LOGGER.info(
        "Wyoming bridge listening on %s (stt=%s, tts=%s)",
        settings.uri,
        usecases.get("transcription", "—"),
        usecases.get("tts", "—"),
    )
    try:
        await server.run(partial(BridgeHandler, info, client, settings))
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
