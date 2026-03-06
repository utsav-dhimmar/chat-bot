# Dockerfile using multi stage   build
# why reduce image size

################### BUILDER ##############
FROM astral/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

ENV UV_NO_DEV=1

COPY backend/uv.lock backend/pyproject.toml ./


RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project


COPY . .


RUN uv sync --locked
################### RUN TIME ##############
FROM python:3.13-slim-bookworm

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"


EXPOSE 8000


CMD [ "/app/.venv/bin/fastapi","run","./backend/app/main.py" ]
