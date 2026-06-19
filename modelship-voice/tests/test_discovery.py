import textwrap

from bridge.discovery import discover_models


def test_discovers_usecase_to_name(tmp_path):
    cfg = tmp_path / "models.yaml"
    cfg.write_text(
        textwrap.dedent(
            """
            models:
              - name: generate
                usecase: generate
                loader: llama_cpp
              - name: transcription
                usecase: transcription
                loader: custom
              - name: tts
                usecase: tts
                loader: custom
            """
        )
    )
    assert discover_models(str(cfg)) == {
        "generate": "generate",
        "transcription": "transcription",
        "tts": "tts",
    }


def test_first_model_per_usecase_wins(tmp_path):
    cfg = tmp_path / "models.yaml"
    cfg.write_text(
        textwrap.dedent(
            """
            models:
              - name: whisper-a
                usecase: transcription
              - name: whisper-b
                usecase: transcription
            """
        )
    )
    assert discover_models(str(cfg)) == {"transcription": "whisper-a"}


def test_empty_config(tmp_path):
    cfg = tmp_path / "models.yaml"
    cfg.write_text("models: []\n")
    assert discover_models(str(cfg)) == {}
