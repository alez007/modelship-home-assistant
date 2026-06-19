from bridge.wyoming_info import build_info


def test_advertises_only_available_capabilities():
    info = build_info({"transcription": "whisper", "tts": "kokoro"})
    assert len(info.asr) == 1
    assert len(info.tts) == 1
    assert info.asr[0].models[0].name == "whisper"
    assert info.tts[0].voices, "expected at least one voice"


def test_no_tts_means_no_tts_program():
    info = build_info({"transcription": "whisper"})
    assert len(info.asr) == 1
    assert info.tts == []


def test_no_stt_means_no_asr_program():
    info = build_info({"tts": "kokoro"})
    assert info.asr == []
    assert len(info.tts) == 1
