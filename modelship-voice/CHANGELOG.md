# Changelog

## 0.1.7

- Fix the Wyoming bridge crashing on startup with `Unknown level: 'TRACE'`
  when the add-on's log level is set to `trace`. modelship defines a custom
  TRACE level (below DEBUG); the bridge now registers it and falls back to
  DEBUG for any unrecognized level name instead of crashing.
- Don't take the container down when modelship serves no STT/TTS model. A
  generate-only stack still exposes the OpenAI API on `:8000`; the bridge now
  logs a warning and idles instead of exiting (which restarted the whole add-on).
- Remove the `model_stack` option. The add-on ships a single `assistant`
  profile (chat + STT + TTS); the `everything` choice is gone.
- Quiet the startup readiness polling. The bridge's "waiting for modelship"
  line and httpx's per-request logs (the `/readyz` poll) now only show at the
  `debug`/`trace` log level instead of spamming `info`.


## 0.1.6

- Bump bundled modelship to 0.5.3.


## 0.1.5

- Bump bundled modelship to 0.5.2.


## 0.1.4

- Bump bundled modelship to 0.5.1.

## 0.1.3

- Fix usecase discovery: read modelship's generated
  `config/models_stack_<profile>.yaml` (a profile doesn't produce `models.yaml`),
  with a fallback to the newest generated stack file.

## 0.1.2

- Fix the Wyoming bridge failing to start (`No module named bridge`) by putting
  the bridge package on `PYTHONPATH` in the supervisor.

## 0.1.1

- Bump bundled modelship to 0.5.0.


## 0.1.0

- Initial release.
- Bundles modelship (CPU `assistant` profile) with a Wyoming bridge exposing
  speech-to-text (whisper) and text-to-speech (Kokoro) to Home Assistant Assist.
- Auto-discovers the STT/TTS model names from the bundled `models.yaml`.
- Exposes modelship's OpenAI API on port 8000 for the conversation LLM.
- Supports `amd64` and `aarch64`.
