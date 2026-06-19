import struct

from bridge.audio import pcm_to_wav, wav_to_pcm


def _pcm(samples: list[int]) -> bytes:
    return struct.pack("<" + "h" * len(samples), *samples)


def test_pcm_wav_roundtrip():
    pcm = _pcm([0, 1000, -1000, 32767, -32768] * 50)
    wav = pcm_to_wav(pcm, rate=16000, width=2, channels=1)
    assert wav[:4] == b"RIFF" and wav[8:12] == b"WAVE"

    out_pcm, rate, width, channels = wav_to_pcm(wav)
    assert (rate, width, channels) == (16000, 2, 1)
    assert out_pcm == pcm


def test_wav_preserves_rate():
    pcm = _pcm([123] * 100)
    wav = pcm_to_wav(pcm, rate=24000, width=2, channels=1)
    _, rate, _, _ = wav_to_pcm(wav)
    assert rate == 24000
