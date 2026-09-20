FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn httpx cryptography

COPY . /app

ENV PORT=8080
ENV UPSTREAM_TARGET="http://localhost:8000"

EXPOSE 8080

CMD ["uvicorn", "sidecar.main:app", "--host", "0.0.0.0", "--port", "8080"]
