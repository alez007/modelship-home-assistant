# Home Assistant add-on image: a vanilla modelship server.
#
# BUILD_FROM is supplied per-arch by build.yaml and points at a pinned, multi-arch
# modelship CPU image (ghcr.io/alez007/modelship:<ver>-cpu, built for amd64 + arm64).
# We only layer a thin launcher that maps add-on options → modelship env vars.
ARG BUILD_FROM
FROM ${BUILD_FROM}

USER root

COPY run.sh /run.sh
RUN chmod +x /run.sh

# Ray scratch lives on /data; the model cache root is configurable (default
# /share/modelship) and set by run.sh from the cache_dir option.
ENV HOME=/data

WORKDIR /modelship

# Replace modelship's privilege-dropping entrypoint with our options launcher.
ENTRYPOINT []
CMD ["/run.sh"]
