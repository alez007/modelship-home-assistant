"""Static voice + language catalog for the Wyoming ``Info`` response.

modelship's `models.yaml` doesn't enumerate a TTS engine's voices or an STT
engine's languages, so the bridge advertises a curated set. These are the
Kokoro-82M voices (the default `assistant`-profile TTS) and the languages
whisper handles. Home Assistant populates its STT/TTS dropdowns from this.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_VOICE = "af_heart"


@dataclass(frozen=True)
class Voice:
    name: str
    languages: tuple[str, ...]
    description: str


# Kokoro-82M voices. Prefix legend: a=American, b=British; f=female, m=male.
KOKORO_VOICES: tuple[Voice, ...] = (
    Voice("af_heart", ("en",), "American English, female (Heart)"),
    Voice("af_bella", ("en",), "American English, female (Bella)"),
    Voice("af_nicole", ("en",), "American English, female (Nicole)"),
    Voice("af_sarah", ("en",), "American English, female (Sarah)"),
    Voice("af_sky", ("en",), "American English, female (Sky)"),
    Voice("am_adam", ("en",), "American English, male (Adam)"),
    Voice("am_michael", ("en",), "American English, male (Michael)"),
    Voice("am_eric", ("en",), "American English, male (Eric)"),
    Voice("bf_emma", ("en",), "British English, female (Emma)"),
    Voice("bf_isabella", ("en",), "British English, female (Isabella)"),
    Voice("bm_george", ("en",), "British English, male (George)"),
    Voice("bm_lewis", ("en",), "British English, male (Lewis)"),
)


# whisper's commonly-used languages (ISO 639-1). whisper auto-detects, so this
# list only drives Home Assistant's language picker.
WHISPER_LANGUAGES: tuple[str, ...] = (
    "en", "es", "fr", "de", "it", "pt", "nl", "ca", "pl", "ru",
    "uk", "sv", "no", "da", "fi", "cs", "ro", "hu", "el", "tr",
    "ar", "he", "hi", "id", "ms", "vi", "th", "zh", "ja", "ko",
)
