FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install production dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy application source, alembic config, and migrations
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

FROM python:3.13-slim

WORKDIR /app

# Copy everything from builder
COPY --from=builder /app /app

# Add virtualenv and source to PATH/PYTHONPATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Create data directory for volume-mounted SQLite DB
RUN mkdir -p /app/data

EXPOSE 8000

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
