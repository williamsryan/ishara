<<<<<<< HEAD
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
=======
FROM python:3.12

# Install required system tools (Netcat and others)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set PYTHONPATH to ensure the app module is discoverable
ENV PYTHONPATH=/app

# Command to run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "1337", "--reload"]
>>>>>>> b3ebafc428b983414fb9552fc810d712fda6a330
