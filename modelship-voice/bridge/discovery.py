"""Map usecase → model name by reading the bundled modelship `models.yaml`.

The add-on bundles modelship with a profile (default ``assistant``) whose
generator names each model after its usecase, so in practice this yields
``{"transcription": "transcription", "tts": "tts", "generate": "generate"}`` —
but parsing the file keeps us correct even if a user renames models or edits the
generated config by hand.
"""

from __future__ import annotations

import logging

import yaml

_LOGGER = logging.getLogger(__name__)


def discover_models(path: str) -> dict[str, str]:
    """Return ``{usecase: model_name}`` for the first model of each usecase."""
    with open(path) as f:
        data = yaml.safe_load(f) or {}

    usecases: dict[str, str] = {}
    for model in data.get("models", []) or []:
        usecase = model.get("usecase")
        name = model.get("name")
        if usecase and name and usecase not in usecases:
            usecases[usecase] = name

    _LOGGER.info("Discovered modelship usecases: %s", usecases)
    return usecases
