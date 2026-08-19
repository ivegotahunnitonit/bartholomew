FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bartholomew_eval package
COPY bartholomew_eval/ ./bartholomew_eval/

# Copy application source code
COPY app/ ./app/

# Copy frontend assets served by serve_dashboard() and routes
COPY *.html ./
COPY dashboard/ ./dashboard/
COPY web/dist/ ./web/dist/
COPY bartholomew_dashboard_visual.png ./bartholomew_dashboard_visual.png
COPY bartholomew_vulnerability_scanner.png ./bartholomew_vulnerability_scanner.png
COPY founder_avatar.jpg ./founder_avatar.jpg


EXPOSE 8080

# Run Uvicorn server targeting PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
