#!/usr/bin/env bash
# Two-process supervisor for the add-on: run modelship and the Wyoming bridge
# side by side, translate Home Assistant add-on options into env vars, and exit
# (so the supervisor restarts us) if either process dies.
set -euo pipefail

OPTIONS=/data/options.json
MSHIP_PY=/.venv/bin/python          # modelship's interpreter (always present)
BRIDGE_PY="${BRIDGE_VENV:-/opt/bridge/venv}/bin/python"

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

# --- Map add-on options → environment -----------------------------------------
MODEL_STACK="$(read_opt model_stack)"; export MSHIP_MODEL_STACK="${MODEL_STACK:-assistant}"

# With a profile, modelship regenerates config/models_stack_<profile>.yaml on each
# start (not config/models.yaml). Point the bridge's usecase discovery at it.
export MSHIP_MODELS_CONFIG="/modelship/config/models_stack_${MSHIP_MODEL_STACK}.yaml"

LOG_LEVEL="$(read_opt log_level)"; LOG_LEVEL="${LOG_LEVEL:-info}"
export MSHIP_LOG_LEVEL="$(printf '%s' "$LOG_LEVEL" | tr '[:lower:]' '[:upper:]')"
export BRIDGE_LOG_LEVEL="$MSHIP_LOG_LEVEL"

HF_TOKEN_OPT="$(read_opt hf_token)"; [ -n "$HF_TOKEN_OPT" ] && export HF_TOKEN="$HF_TOKEN_OPT"
DEFAULT_VOICE="$(read_opt default_voice)"; [ -n "$DEFAULT_VOICE" ] && export BRIDGE_DEFAULT_VOICE="$DEFAULT_VOICE"
DEFAULT_LANG="$(read_opt default_language)"; export BRIDGE_DEFAULT_LANGUAGE="${DEFAULT_LANG:-en}"

# Persist model weights/caches on /data across restarts and updates.
export HOME=/data MSHIP_CACHE_DIR=/data/cache HF_HOME=/data/hf
mkdir -p /data/cache /data/hf

echo "[run] starting modelship (profile=${MSHIP_MODEL_STACK}, log=${MSHIP_LOG_LEVEL})"
echo "[run] bridge will expose Wyoming on tcp://0.0.0.0:${WYOMING_PORT:-10300}"

# --- Supervise modelship + bridge ---------------------------------------------
mship_pid=""
bridge_pid=""
terminate() {
    trap - TERM INT
    [ -n "$bridge_pid" ] && kill -TERM "$bridge_pid" 2>/dev/null || true
    [ -n "$mship_pid" ] && kill -TERM "$mship_pid" 2>/dev/null || true
}
trap terminate TERM INT

cd /modelship
uv run --no-sync mship_deploy.py &
mship_pid=$!

# The bridge polls /readyz itself, so start it now; it will block until modelship
# is up and the generated models.yaml exists. PYTHONPATH points at the bridge
# package's parent (cwd is /modelship for modelship's sake).
PYTHONPATH="${BRIDGE_DIR:-/opt/bridge}" "$BRIDGE_PY" -m bridge &
bridge_pid=$!

# Exit as soon as either child exits; the supervisor restarts the whole add-on.
wait -n "$mship_pid" "$bridge_pid"
status=$?
echo "[run] a child process exited (status=$status); shutting down"
terminate
wait || true
exit "$status"
