#!/usr/bin/env bash
# Single-process launcher for the add-on: translate Home Assistant add-on options
# into modelship env vars and exec mship_deploy.py. The OpenAI-compatible API is
# served on :8000; STT/TTS/conversation are consumed by the Modelship Conversation
# HACS integration over that HTTP API (no Wyoming).
set -euo pipefail

MSHIP_PY=/.venv/bin/python          # modelship's interpreter (always present)

# Read one key from the add-on options JSON; empty string if unset/missing.
read_opt() {
    "$MSHIP_PY" - "$1" <<'PY'
import json, os, sys
key = sys.argv[1]
path = "/data/options.json"
val = ""
if os.path.exists(path):
    with open(path) as f:
        val = json.load(f).get(key, "")
print("" if val is None else val)
PY
}

# --- Logging ------------------------------------------------------------------
LOG_LEVEL="$(read_opt log_level)"; LOG_LEVEL="${LOG_LEVEL:-info}"
export MSHIP_LOG_LEVEL="$(printf '%s' "$LOG_LEVEL" | tr '[:lower:]' '[:upper:]')"

# --- Cache root (weights + HF cache + default state) --------------------------
# One user-accessible durable root. State nests under it by default (see below).
CACHE_DIR="$(read_opt cache_dir)"; CACHE_DIR="${CACHE_DIR:-/share/modelship}"
export HOME=/data MSHIP_CACHE_DIR="$CACHE_DIR" HF_HOME="$CACHE_DIR/hf"
mkdir -p "$CACHE_DIR" "$CACHE_DIR/hf"

HF_TOKEN_OPT="$(read_opt hf_token)"; [ -n "$HF_TOKEN_OPT" ] && export HF_TOKEN="$HF_TOKEN_OPT"

# --- State store --------------------------------------------------------------
# Default "file://" (no path) → modelship persists durable state at
# $MSHIP_CACHE_DIR/state. Override with memory://, file:///path, or redis://…
STATE_STORE="$(read_opt state_store)"
[ -n "$STATE_STORE" ] && export MSHIP_STATE_STORE="$STATE_STORE"

# --- Config: profile vs custom models.yaml ------------------------------------
# Configs live in the user-visible addon_config mount (/config): generated profile
# YAMLs and a custom models.yaml are read/written there by absolute path.
#
# A custom config_file overrides the profile. Both modes resolve to an explicit
# --config path so the deploy always goes through the same reconcile path below.
# For a profile we PRE-GENERATE the models.yaml ourselves (instead of letting
# MSHIP_MODEL_STACK generate it lazily): passing --config + --reconcile with a
# bare MSHIP_MODEL_STACK would hit mship_deploy's "self-heal" branch (reconcile +
# no --config) and ignore the profile, deploying nothing on first boot.
CONFIG_FILE="$(read_opt config_file)"
if [ -n "$CONFIG_FILE" ]; then
    case "$CONFIG_FILE" in
        /*) CONFIG_PATH="$CONFIG_FILE" ;;          # absolute
        *)  CONFIG_PATH="/config/$CONFIG_FILE" ;;  # relative to addon_config
    esac
    echo "[run] using custom config: $CONFIG_PATH"
else
    PROFILE="$(read_opt profile)"; PROFILE="${PROFILE:-assistant}"
    CONFIG_PATH="/config/models_stack_${PROFILE}.yaml"
    echo "[run] generating profile '$PROFILE' -> $CONFIG_PATH"
    "$MSHIP_PY" -c "from modelship.deploy.profiles.generator import generate_models_yaml as g; g('${PROFILE}', '${CONFIG_PATH}')"
fi

# Reconcile every deploy so the running cluster matches the config exactly: editing
# models.yaml or switching profile removes/replaces dropped deployments instead of
# leaving stale ones behind (additive, the default, would only ever add).
echo "[run] starting modelship (cache=${CACHE_DIR}, log=${MSHIP_LOG_LEVEL}, state=${MSHIP_STATE_STORE:-memory://})"

cd /modelship
exec uv run --no-sync mship_deploy.py --config "$CONFIG_PATH" --reconcile
