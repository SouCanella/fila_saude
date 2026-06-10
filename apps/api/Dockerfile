FROM golang:1.22-alpine AS builder
WORKDIR /src
RUN apk add --no-cache git
COPY apps/api/go.mod apps/api/go.sum* ./
RUN go mod download
COPY apps/api/ ./
RUN CGO_ENABLED=0 go build -o /server ./cmd/server

FROM alpine:3.19
RUN apk add --no-cache ca-certificates
WORKDIR /app
COPY --from=builder /server .
COPY apps/api/migrations ./migrations
ENV MIGRATIONS_DIR=/app/migrations
EXPOSE 8000
CMD ["./server"]
