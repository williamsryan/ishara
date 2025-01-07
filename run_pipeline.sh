#!/usr/bin/env bash

echo "Starting Docker services..."
docker-compose up -d

echo "Running setup script..."
python scripts/setup_pipeline.py

echo "Data pipeline setup complete!"
