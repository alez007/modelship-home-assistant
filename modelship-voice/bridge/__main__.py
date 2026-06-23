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

# modelship defines a custom TRACE level (below DEBUG). The add-on feeds the
# same log level to both processes, so mirror it here — otherwise a shared
# level of "TRACE" makes stdlib logging raise "Unknown level: 'TRACE'".
logging.addLevelName(5, "TRACE")


def _resolve_level(name: str) -> int:
    """Map a level name to its numeric value, falling back to DEBUG.

    Stdlib ``logging`` rejects unknown level *names* outright; we'd rather be
    verbose than crash the bridge on an unexpected value.
    """
    level = logging.getLevelName(name)
    return level if isinstance(level, int) else logging.DEBUG


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
    level = _resolve_level(settings.log_level)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # httpx logs every request at INFO; with the /readyz readiness poll firing
    # every few seconds during startup that floods the log. Keep it quiet unless
    # we're explicitly at DEBUG (or lower).
    if level > logging.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)

    _LOGGER.debug("Waiting for modelship at %s ...", settings.base_url)
    await _wait_for_ready(settings)

    usecases = discover_models(settings.models_config_path)
    if "transcription" not in usecases and "tts" not in usecases:
        # No STT/TTS to expose over Wyoming — e.g. a generate-only stack that
        # only serves the OpenAI API on :8000 for the conversation LLM. Exiting
        # here would take the whole add-on container down with us, killing that
        # API too. Idle instead so modelship keeps serving.
        _LOGGER.warning(
            "modelship serves neither a 'transcription' nor a 'tts' model; the "
            "Wyoming bridge has nothing to expose. Staying alive so modelship's "
            "OpenAI API keeps running. Enable a voice profile to add speech."
        )
        await asyncio.Event().wait()  # block forever; never set
        return

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
