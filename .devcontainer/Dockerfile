FROM ghcr.io/astral-sh/uv:0.9.18 AS uv
FROM oven/bun:1.3-debian AS base

FROM base AS builder

ARG USERNAME=bun

# Create the user
RUN usermod --shell=/bin/bash $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

COPY --from=uv /uv /uvx /bin/

RUN apt-get update \
  && apt-get install -y git ffmpeg

USER $USERNAME