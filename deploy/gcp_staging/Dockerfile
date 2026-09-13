# Production Dockerfile for Autonomous Circularity Network (ACN) API & Orchestrator
# Compatible with Google Cloud Run, Cloud Build, and Container Registry

FROM node:22-alpine AS builder
WORKDIR /app

# Copy package manifests and source files
COPY package*.json ./
COPY tsconfig*.json ./
COPY src/ ./src/
COPY dashboard/ ./dashboard/

# Install dependencies
RUN npm ci --quiet

# Production stage
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8080

# Copy node_modules and built sources
COPY --from=builder /app ./

EXPOSE 8080

# Launch server with TS experimental strip types
CMD ["node", "--experimental-strip-types", "src/api/server.ts"]
