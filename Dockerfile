# Multi-stage Go build for Bartholomew Security Daemon v3.1
# Fully compatible with Google Cloud Run & GCP Artifact Registry

FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY go.mod ./
COPY main.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o bartholomew_daemon main.go

# Production stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates tzdata
WORKDIR /app

ENV PORT=8080
EXPOSE 8080

# Copy compiled Go binary and web assets
COPY --from=builder /app/bartholomew_daemon ./
COPY index.html ./
COPY PITCH_DECK.html ./
COPY founder_avatar.jpg ./
COPY dashboard/ ./dashboard/
COPY demo_trajectory_inspector.html ./

CMD ["./bartholomew_daemon"]
