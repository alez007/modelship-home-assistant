# Home Assistant add-on image: modelship (CPU assistant profile) + Wyoming bridge.
#
# BUILD_FROM is supplied per-arch by build.yaml and points at a pinned, multi-arch
# modelship CPU image (ghcr.io/alez007/modelship:<ver>-cpu, built for amd64 + arm64).
# We only layer a small, pure-Python bridge on top, so the build stays light even
# on arm64 hardware.
ARG BUILD_FROM
FROM ${BUILD_FROM}

USER root

# The bridge gets its own venv so we never touch modelship's locked environment.
COPY requirements.txt /opt/bridge/requirements.txt
RUN uv venv /opt/bridge/venv \
    && uv pip install --python /opt/bridge/venv -r /opt/bridge/requirements.txt
COPY bridge /opt/bridge/bridge

COPY run.sh /run.sh
RUN chmod +x /run.sh

# Persist weights/caches on the add-on's /data volume so restarts don't redownload.
ENV HOME=/data \
    MSHIP_CACHE_DIR=/data/cache \
    HF_HOME=/data/hf \
    MSHIP_BASE_URL=http://127.0.0.1:8000 \
    MSHIP_MODELS_CONFIG=/modelship/config/models.yaml \
    BRIDGE_VENV=/opt/bridge/venv \
    BRIDGE_DIR=/opt/bridge

WORKDIR /modelship

# Replace modelship's privilege-dropping entrypoint with our two-process supervisor.
ENTRYPOINT []
CMD ["/run.sh"]
