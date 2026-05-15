# syntax=docker/dockerfile:1
# AutoIncome v3.0 - Production Dockerfile
# Multi-stage build for minimal attack surface and image size

# ─── Stage 1: Builder ─────────────────────────────────────────────
FROM python:3.13-slim-bookworm AS builder

# Security: Run as non-root during build
RUN groupadd -r builder && useradd -r -g builder builder

WORKDIR /build

# Install build dependencies only (no runtime deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definitions
COPY pyproject.toml ./
COPY src/ ./src/

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# ─── Stage 2: Production ─────────────────────────────────────────
FROM python:3.13-slim-bookworm AS production

LABEL org.opencontainers.image.title="AutoIncome"
LABEL org.opencontainers.image.description="AI-powered passive income opportunity aggregator"
LABEL org.opencontainers.image.source="https://github.com/dfhhvc/auto92811"
LABEL org.opencontainers.image.licenses="MIT"

# Security: Minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Security: Create dedicated non-root user
RUN groupadd -r -g 1000 autoincome \
    && useradd -r -u 1000 -g autoincome -s /sbin/nologin -d /app autoincome

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code (as root first, then chown)
COPY --chown=autoincome:autoincome src/ ./src/
COPY --chown=autoincome:autoincome docker/entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Security: Set restrictive permissions
RUN chmod -R 550 /app/src \
    && chmod 500 /app/entrypoint.sh

# Create data directory with proper permissions
RUN mkdir -p /app/data && chown -R autoincome:autoincome /app/data \
    && chmod 750 /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Switch to non-root user
USER autoincome

# Expose port
EXPOSE 8080

# Use entrypoint script for initialization
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "autoincome.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
