# Modelship Voice

Local STT + TTS + LLM for Home Assistant Assist, powered by
[modelship](https://github.com/alez007/modelship).

## How it works

This add-on runs two processes in one container:

- **modelship** (CPU `assistant` profile) — serves whisper (STT), Kokoro (TTS),
  and a chat LLM behind an OpenAI-compatible API on port `8000`.
- **Wyoming bridge** — exposes STT + TTS to Home Assistant over the Wyoming
  protocol on port `10300`, translating to modelship's HTTP endpoints.

The bridge reads the model names from modelship's generated `models.yaml`, so it
always targets the right STT/TTS models for the profile you chose.

## Configuration

| Option | Default | Description |
|---|---|---|
| `model_stack` | `assistant` | Capability set. `assistant` = chat + STT + TTS. `everything` adds image + embeddings (heavier). |
| `log_level` | `info` | `trace`/`debug` log full detail; `info` is normal. |
| `hf_token` | _(unset)_ | Hugging Face token, only needed if you switch to gated models. |
| `default_voice` | `af_heart` | Kokoro voice used when HA doesn't request a specific one. |
| `default_language` | `en` | Language hint for STT when HA doesn't send one. |

Model weights and caches persist in the add-on's `/data` volume, so restarts and
updates don't re-download them.

## Wiring Home Assistant Assist

### 1. Speech-to-text and text-to-speech (Wyoming)

1. **Settings → Devices & Services → Add Integration → Wyoming Protocol**.
2. Host: the add-on's hostname (e.g. `localhost` / `a0d7b954-modelship-voice`
   depending on your setup), Port: `10300`.
3. Home Assistant discovers both the STT and TTS services from this one Wyoming
   endpoint.

### 2. Conversation LLM (OpenAI Conversation)

The LLM does **not** go through Wyoming.

1. **Settings → Devices & Services → Add Integration → OpenAI Conversation**.
2. Use any non-empty API key (modelship doesn't check it) and set the **base URL**
   to `http://<add-on-host>:8000/v1`.
3. Pick the `generate` model.

### 3. Build the Assist pipeline

**Settings → Voice assistants → Add assistant**, then choose:

- **Conversation agent**: the OpenAI Conversation entry from step 2.
- **Speech-to-text**: the modelship Wyoming STT.
- **Text-to-speech**: the modelship Wyoming TTS (pick a voice).

## Troubleshooting

- **Add-on slow to start / Wyoming unavailable at first**: first boot downloads
  models. The bridge waits for modelship to be ready before it accepts Wyoming
  connections — watch the log for `Wyoming bridge listening on ...`.
- **No STT/TTS offered in Assist**: confirm `model_stack` is `assistant` or
  `everything` (a chat-only stack has no STT/TTS for the bridge to expose).
- **Out-of-memory / killed**: try a smaller `model_stack`, or run on hardware
  with more memory.
