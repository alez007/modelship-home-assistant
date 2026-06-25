# Modelship — Home Assistant add-on

Run a fully local [modelship](https://github.com/alez007/modelship) server in Home
Assistant. The add-on exposes modelship's OpenAI-compatible API on port `8000`,
serving whatever models you select via a profile or your own `models.yaml` —
chat/LLM, embeddings, speech-to-text, text-to-speech and image generation.

For a voice assistant (conversation + STT + TTS), pair it with the
[**Modelship Conversation**](https://github.com/alez007/modelship-conversation)
HACS integration, which drives this API directly over HTTP — no cloud, no Wyoming.

## What's inside

| Capability | How HA connects | modelship endpoint |
|---|---|---|
| Conversation LLM | Modelship Conversation integration (port `8000`) | `/v1/chat/completions`, `/v1/responses` |
| Speech-to-text | Modelship Conversation integration (port `8000`) | `/v1/audio/transcriptions` |
| Text-to-speech | Modelship Conversation integration (port `8000`) | `/v1/audio/speech` |

Everything goes over modelship's OpenAI-compatible HTTP API; the Modelship
Conversation integration exposes native HA conversation/STT/TTS entities backed by it.

## Install

1. In Home Assistant: **Settings → Add-ons → Add-on store → ⋮ → Repositories**,
   add `https://github.com/alez007/modelship-home-assistant`.
2. Install **Modelship**, then start it. First boot downloads models, so give it a
   few minutes (watch the add-on log).
3. See the add-on's **Documentation** tab for options and wiring Assist
   (`modelship/DOCS.md`).

## Supported architectures

`amd64` and `aarch64` (Raspberry Pi 4/5 and similar). On low-RAM boards the
profiles automatically select the small model tier.

## Repository layout

- [`modelship/`](modelship/) — the add-on (Dockerfile, config, launcher, docs).
