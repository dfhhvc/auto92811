# AutoIncome v4 — Production Dockerfile
# Multi-stage build for smaller image size

# ── Stage 1: Builder ────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir hatchling && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -e "."

# ── Stage 2: Runtime ────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r autoincome && useradd -r -g autoincome autoincome

# Copy wheels and install
COPY --from=builder /app/wheels /app/wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /app/wheels/* && \
    rm -rf /app/wheels

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY docker/ ./docker/

# Create data directory
RUN mkdir -p /app/data && chown -R autoincome:autoincome /app

# Switch to non-root user
USER autoincome

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Expose port
EXPOSE 8080

# Default command
CMD ["uvicorn", "autoincome.api.main:app", "--host", "0.0.0.0", "--port", "8080"]