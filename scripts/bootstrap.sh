#!/bin/bash

echo "Bootstrapping Ishara..."

echo "Installing frontend dependencies..."
cd ../frontend
npm install

echo "Starting containers..."
cd ..
docker compose up --build -d

echo "Visit frontend: http://localhost:3000"
echo "Backend API:    http://localhost:8080"
