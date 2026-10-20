# ── Stage 1: dependency installer ────────────────────────────────────────────
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first (avoids pulling the massive CUDA build)
RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Copy and install remaining requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PORT=8000

WORKDIR /app

# Install only the minimal runtime libs (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage (multi-stage build = smaller image)
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# ── Security: run as non-root user ───────────────────────────────────────────
RUN groupadd --gid 1001 medai && \
    useradd --uid 1001 --gid medai --shell /bin/bash --create-home medai

# Copy application code
COPY --chown=medai:medai . .

# Create writable directories for model cache
RUN mkdir -p /app/models/weights /app/rag/faiss_medical_index \
    && chown -R medai:medai /app/models /app/rag

USER medai

# Expose API port
EXPOSE $PORT

# Health check — Render/Docker will restart if this fails 3× in a row
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

# Production server: Gunicorn + Uvicorn workers
# --workers 1: single worker because we load large ML models in memory
# --timeout 120: allow up to 2 minutes for analysis requests
CMD gunicorn main:app \
        --bind 0.0.0.0:${PORT} \
        --workers 1 \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --max-requests 500 \
        --max-requests-jitter 50 \
        --log-level info \
        --access-logfile - \
        --error-logfile -
