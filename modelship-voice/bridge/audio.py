"""PCM ↔ WAV helpers (stdlib only — no numpy/librosa).

Wyoming streams raw signed-16-bit PCM; modelship's OpenAI audio endpoints speak
WAV files. These two functions are the entire format bridge — no resampling is
needed because each side's rate is carried through untouched (Home Assistant
sends 16 kHz for STT; we advertise the TTS engine's native rate from the WAV it
returns).
"""

from __future__ import annotations

import io
import wave


def pcm_to_wav(pcm: bytes, rate: int, width: int, channels: int) -> bytes:
    """Wrap raw PCM frames in a WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(width)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    return buf.getvalue()


def wav_to_pcm(data: bytes) -> tuple[bytes, int, int, int]:
    """Unwrap a WAV file → (pcm, rate, width, channels)."""
    with wave.open(io.BytesIO(data), "rb") as wf:
        return (
            wf.readframes(wf.getnframes()),
            wf.getframerate(),
            wf.getsampwidth(),
            wf.getnchannels(),
        )
