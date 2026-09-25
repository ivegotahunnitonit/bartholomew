# Bartholomew ARP Sidecar Proxy Container
FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/
COPY btp_guard/ ./btp_guard/
COPY packages/sidecar_proxy/ ./packages/sidecar_proxy/

ENV PYTHONUNBUFFERED=1
ENV PROXY_PORT=9090
ENV PROXY_HOST=0.0.0.0
ENV UPSTREAM_URL=http://127.0.0.1:8000

EXPOSE 9090

ENTRYPOINT ["python", "packages/sidecar_proxy/proxy.py"]
