# Bartholomew Cloud Execution Gateway (BTP v5.4.16)
# Enterprise AST Invariant Gating, Zero-Install Bot Proxy & Cryptographic Attestation
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY policies/ ./policies/

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

CMD ["uvicorn", "src.gateway_server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
