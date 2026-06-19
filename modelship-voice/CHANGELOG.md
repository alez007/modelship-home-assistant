# Changelog

## 0.1.0

- Initial release.
- Bundles modelship (CPU `assistant` profile) with a Wyoming bridge exposing
  speech-to-text (whisper) and text-to-speech (Kokoro) to Home Assistant Assist.
- Auto-discovers the STT/TTS model names from the bundled `models.yaml`.
- Exposes modelship's OpenAI API on port 8000 for the conversation LLM.
- Supports `amd64` and `aarch64`.
