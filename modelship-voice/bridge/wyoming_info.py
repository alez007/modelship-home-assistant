"""Build the Wyoming ``Info`` advertised to Home Assistant on ``Describe``.

Only the capabilities modelship actually serves are advertised: an ASR program
iff a ``transcription`` model exists, a TTS program iff a ``tts`` model exists.
"""

from __future__ import annotations

from wyoming.info import (
    AsrModel,
    AsrProgram,
    Attribution,
    Info,
    TtsProgram,
    TtsVoice,
)

from . import __version__
from .voices import KOKORO_VOICES, WHISPER_LANGUAGES

_ATTRIBUTION = Attribution(name="modelship", url="https://github.com/alez007/modelship")


def build_info(usecases: dict[str, str]) -> Info:
    asr: list[AsrProgram] = []
    tts: list[TtsProgram] = []

    stt_model = usecases.get("transcription")
    if stt_model:
        asr.append(
            AsrProgram(
                name="modelship-whisper",
                description="modelship speech-to-text (whisper) via the Wyoming bridge",
                attribution=_ATTRIBUTION,
                installed=True,
                version=__version__,
                models=[
                    AsrModel(
                        name=stt_model,
                        description=f"modelship model '{stt_model}'",
                        attribution=_ATTRIBUTION,
                        installed=True,
                        languages=list(WHISPER_LANGUAGES),
                        version=None,
                    )
                ],
            )
        )

    tts_model = usecases.get("tts")
    if tts_model:
        tts.append(
            TtsProgram(
                name="modelship-kokoro",
                description="modelship text-to-speech (Kokoro) via the Wyoming bridge",
                attribution=_ATTRIBUTION,
                installed=True,
                version=__version__,
                voices=[
                    TtsVoice(
                        name=v.name,
                        description=v.description,
                        attribution=_ATTRIBUTION,
                        installed=True,
                        languages=list(v.languages),
                        version=None,
                    )
                    for v in KOKORO_VOICES
                ],
            )
        )

    return Info(asr=asr, tts=tts)
