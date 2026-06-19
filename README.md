# Modelship — Home Assistant add-on

Run a fully local voice assistant in Home Assistant, powered by
[modelship](https://github.com/alez007/modelship). One add-on bundles modelship's
CPU `assistant` profile (whisper STT + Kokoro TTS + a chat LLM) with a small
**Wyoming bridge**, so Home Assistant's Assist pipeline can use it end to end —
no cloud, no API keys.

## What's inside

| Capability | How HA connects | modelship endpoint |
|---|---|---|
| Speech-to-text | Wyoming (this add-on, port `10300`) | `/v1/audio/transcriptions` |
| Text-to-speech | Wyoming (this add-on, port `10300`) | `/v1/audio/speech` |
| Conversation LLM | *OpenAI Conversation* integration (port `8000`) | `/v1/chat/completions` |

STT and TTS speak the Wyoming protocol; the bridge translates those to
modelship's OpenAI-compatible HTTP endpoints. The conversation LLM is **not**
Wyoming — you wire it with Home Assistant's built-in *OpenAI Conversation*
integration pointed at this add-on's port `8000`.

## Install

1. In Home Assistant: **Settings → Add-ons → Add-on store → ⋮ → Repositories**,
   add `https://github.com/alez007/modelship-home-assistant`.
2. Install **Modelship Voice**, then start it. First boot downloads models, so
   give it a few minutes (watch the add-on log).
3. See the add-on's **Documentation** tab for wiring Assist. (`modelship-voice/DOCS.md`.)

## Supported architectures

`amd64` and `aarch64` (Raspberry Pi 4/5 and similar). On low-RAM boards the
add-on automatically selects the small model tier.

## Repository layout

- [`modelship-voice/`](modelship-voice/) — the add-on (Dockerfile, config, bridge, docs).
- The Wyoming bridge source lives in [`modelship-voice/bridge/`](modelship-voice/bridge/).
