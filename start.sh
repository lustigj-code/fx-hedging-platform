#!/bin/bash

# FX Hedging Platform - Quick Start Script

echo "================================"
echo "FX Hedging Platform"
echo "================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
fi

# Start the platform
echo "Starting FX Hedging Platform..."
echo ""
docker-compose up -d

echo ""
echo "================================"
echo "Platform Starting..."
echo "================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:3000"
echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check if backend is up
echo ""
echo "Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend API is running"
else
    echo "⚠ Backend API is starting (may take 30-60 seconds on first run)"
fi

echo ""
echo "================================"
echo "Next Steps:"
echo "================================"
echo ""
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Demo' tab and generate demo data"
echo "3. Try the Calculator to price FX options"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
