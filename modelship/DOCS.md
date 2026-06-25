# Modelship

Run a local [modelship](https://github.com/alez007/modelship) server on your Home
Assistant box. It exposes an OpenAI-compatible API on port `8000` serving the
models you select (chat/LLM, embeddings, speech-to-text, text-to-speech, image
generation).

For Assist (conversation + STT + TTS), pair this add-on with the
[**Modelship Conversation**](https://github.com/alez007/modelship-conversation)
HACS integration, which talks to this API over HTTP — no Wyoming needed.

## How it works

The add-on runs a single modelship server. You pick **what** it serves in one of
two ways:

- a **profile** — modelship auto-generates a `models.yaml` sized to your hardware, or
- a **custom config** — your own `models.yaml`.

## Configuration

| Option | Default | Description |
|---|---|---|
| `log_level` | `info` | `trace`/`debug` log full detail; `info` is normal. |
| `profile` | `assistant` | Model set to auto-generate: `chat` (LLM + embeddings), `assistant` (LLM + STT + TTS), `studio` (LLM + image + embeddings), `everything`. Ignored if `config_file` is set. |
| `config_file` | _(unset)_ | Use your own `models.yaml` instead of a profile. Relative names resolve under the add-on config folder (e.g. `models.yaml`); absolute paths are used as-is. Takes precedence over `profile`. |

The add-on **reconciles** on every start: the running models are made to match your
profile/`models.yaml` exactly, so editing the config or switching profile removes or
replaces the old deployments instead of leaving stale ones running.
| `state_store` | `file://` | Where modelship persists its deployment state. `file://` (default) keeps it under the cache dir (`<cache_dir>/state`). Use `memory://` for none, `file:///some/path`, or `redis://[:password@]host:6379/0`. |
| `cache_dir` | `/share/modelship` | Durable root for model weights, the Hugging Face cache and (by default) state. Lives under `/share` so it's reachable from the Samba/File-editor add-ons and can be cleared. |
| `hf_token` | _(unset)_ | Hugging Face token, only needed for gated models. |

The `assistant` profile is the right default for the Modelship Conversation
integration (it serves an LLM + speech-to-text + text-to-speech).

### Files you can see and edit

- **Configs** live in this add-on's config folder (the `addon_config` mount). The
  selected profile is written there as `models_stack_<profile>.yaml` on each start —
  copy it to `models.yaml`, edit it, and set `config_file: models.yaml` to take full
  control.
- **Weights / cache / state** live under `cache_dir` (default `/share/modelship`),
  accessible via the Samba share or File editor add-ons. Delete the folder to reclaim
  disk; it re-downloads on next start.

## Wiring Home Assistant Assist

1. Install the **Modelship Conversation** integration from HACS (custom repository
   `https://github.com/alez007/modelship-conversation`).
2. Add it (**Settings → Devices & Services → Add Integration → Modelship**), set the
   base URL to `http://<add-on-host>:8000/v1` and any non-empty API key (modelship
   doesn't check it).
3. It provides conversation, STT and TTS entities natively. Build your pipeline under
   **Settings → Voice assistants → Add assistant** using those entities.

## Troubleshooting

- **Slow first start**: the first boot downloads models into `cache_dir`. Watch the
  log; subsequent starts reuse the cache.
- **No models served / startup error**: check the modelship log for the profile that
  couldn't fit your hardware, or a `models.yaml` error. Try a lighter `profile` or a
  custom `config_file`.
- **Out-of-memory / killed**: run on hardware with more memory, or pick a lighter
  profile / smaller models.
