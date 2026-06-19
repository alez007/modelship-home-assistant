"""Runtime configuration, read once from the environment.

The add-on's `run.sh` translates Home Assistant add-on options into these env
vars before starting the bridge.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str
    """Base URL of the bundled modelship gateway (no trailing slash)."""

    models_config_path: str
    """Path to the modelship `models.yaml` the bridge reads usecase→name from."""

    uri: str
    """Wyoming server bind URI, e.g. ``tcp://0.0.0.0:10300``."""

    default_voice: str | None
    """Voice used for TTS when Home Assistant doesn't specify one."""

    default_language: str
    """Language passed to STT when Home Assistant doesn't specify one."""

    log_level: str
    ready_timeout_s: float
    """How long to wait for modelship `/readyz` before giving up at startup."""

    request_timeout_s: float
    """Per-request HTTP timeout against modelship (CPU inference is slow)."""

    chunk_frames: int
    """Frames per Wyoming AudioChunk when streaming synthesized speech back."""

    @classmethod
    def from_env(cls) -> "Settings":
        port = os.environ.get("WYOMING_PORT", "10300")
        return cls(
            base_url=os.environ.get("MSHIP_BASE_URL", "http://127.0.0.1:8000").rstrip("/"),
            models_config_path=os.environ.get("MSHIP_MODELS_CONFIG", "/modelship/config/models.yaml"),
            uri=os.environ.get("WYOMING_URI", f"tcp://0.0.0.0:{port}"),
            default_voice=os.environ.get("BRIDGE_DEFAULT_VOICE") or None,
            default_language=os.environ.get("BRIDGE_DEFAULT_LANGUAGE") or "en",
            log_level=os.environ.get("BRIDGE_LOG_LEVEL", os.environ.get("MSHIP_LOG_LEVEL", "INFO")).upper(),
            ready_timeout_s=float(os.environ.get("BRIDGE_READY_TIMEOUT_S", "1800")),
            request_timeout_s=float(os.environ.get("BRIDGE_REQUEST_TIMEOUT_S", "300")),
            chunk_frames=int(os.environ.get("BRIDGE_CHUNK_FRAMES", "1024")),
        )
