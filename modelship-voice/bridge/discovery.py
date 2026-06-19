"""Map usecase → model name by reading the bundled modelship `models.yaml`.

The add-on bundles modelship with a profile (default ``assistant``) whose
generator names each model after its usecase, so in practice this yields
``{"transcription": "transcription", "tts": "tts", "generate": "generate"}`` —
but parsing the file keeps us correct even if a user renames models or edits the
generated config by hand.
"""

from __future__ import annotations

import glob
import logging
import os

import yaml

_LOGGER = logging.getLogger(__name__)


def _resolve_path(path: str) -> str:
    """Use ``path`` if it exists, else fall back to the newest generated stack
    file beside it. modelship regenerates ``models_stack_<profile>.yaml`` on every
    boot, so the newest mtime is the active profile — robust even if the profile
    name (and thus the filename) isn't known here."""
    if os.path.exists(path):
        return path
    candidates = glob.glob(os.path.join(os.path.dirname(path) or ".", "models_stack_*.yaml"))
    if candidates:
        return max(candidates, key=os.path.getmtime)
    return path  # let open() raise a clear FileNotFoundError


def discover_models(path: str) -> dict[str, str]:
    """Return ``{usecase: model_name}`` for the first model of each usecase."""
    resolved = _resolve_path(path)
    with open(resolved) as f:
        data = yaml.safe_load(f) or {}

    usecases: dict[str, str] = {}
    for model in data.get("models", []) or []:
        usecase = model.get("usecase")
        name = model.get("name")
        if usecase and name and usecase not in usecases:
            usecases[usecase] = name

    _LOGGER.info("Discovered modelship usecases: %s", usecases)
    return usecases
