# Build stage
FROM golang:1.22 as builder
WORKDIR /app
COPY . .
RUN go mod tidy && go build -o ishara ./cmd/ishara

# Runtime stage
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/ishara .
EXPOSE 8080
CMD ["./ishara"]
