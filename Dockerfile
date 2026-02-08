# --- Builder ---
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# --- Runtime ---
FROM python:3.13-alpine

WORKDIR /app
RUN adduser -D appuser
USER appuser

COPY --from=builder /app/.venv /app/.venv

COPY ./src ./src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "src.bootstrap.run_service"]