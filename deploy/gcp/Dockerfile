# Bartholomew Cloud — Cloud Run Container Manifest
# ===================================================
# Optimized for Google Cloud Run scale-to-zero and high concurrency (--concurrency 80).

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml requirements.txt* ./
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic cryptography

# Copy source application
COPY src/ ./src/
COPY btp_guard.py ./
COPY framework_adapters/ ./framework_adapters/

EXPOSE 8080

# Run Uvicorn listening on the Cloud Run injected PORT
CMD exec uvicorn src.api.cloud_engine_server:app --host 0.0.0.0 --port ${PORT} --workers 2
