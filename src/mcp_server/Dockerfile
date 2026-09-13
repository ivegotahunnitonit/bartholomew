# Bartholomew MCP Server Container
FROM python:3.11-slim

WORKDIR /app

# Copy repository source files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run MCP stdio server
ENTRYPOINT ["python", "-m", "mcp_server.server"]
