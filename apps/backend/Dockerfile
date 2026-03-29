FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install production dependencies (without building the project itself for layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen --no-install-project

# Copy application source, alembic config, migrations, and README (referenced by pyproject.toml)
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini README.md ./

# Now install the project itself (source is available)
RUN uv sync --no-dev --frozen

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
