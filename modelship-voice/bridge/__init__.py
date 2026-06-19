"""Wyoming ↔ modelship bridge.

Exposes Home Assistant's Wyoming protocol (STT + TTS) on a TCP port and
translates each request into a call against a modelship instance's
OpenAI-compatible audio endpoints:

    Wyoming ASR  →  POST /v1/audio/transcriptions   (whisper)
    Wyoming TTS  →  POST /v1/audio/speech            (kokoro)

All inference happens in modelship; this package is thin HTTP glue.
"""

__version__ = "0.1.0"
