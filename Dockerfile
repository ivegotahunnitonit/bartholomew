# Multi-stage Go build for Bartholomew Security Daemon v3.1
# Fully compatible with Google Cloud Run & GCP Artifact Registry

FROM golang:alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o bartholomew_daemon main.go

# Production stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates tzdata
WORKDIR /app

ENV PORT=8080
EXPOSE 8080

# Copy compiled Go binary and web assets
COPY --from=builder /app/bartholomew_daemon ./
COPY --from=builder /app/index.html ./
COPY --from=builder /app/PITCH_DECK.html ./
COPY --from=builder /app/founder_avatar.jpg ./
COPY --from=builder /app/dashboard/ ./dashboard/
COPY --from=builder /app/demo_trajectory_inspector.html ./

CMD ["./bartholomew_daemon"]
