#!/bin/bash

# BISHENG Local Development Shutdown Script
# This script stops all backend and frontend services

set -e

echo "🛑 Stopping BISHENG Local Development Services..."
echo ""

cd "$(dirname "$0")/../src/backend"

# Stop frontend services first
echo "⏹️  Stopping Frontend Services..."

# Stop Platform
if [ -f logs/platform.pid ]; then
    PLATFORM_PID=$(cat logs/platform.pid)
    if ps -p $PLATFORM_PID > /dev/null 2>&1; then
        echo "   Stopping Platform (PID: $PLATFORM_PID)"
        kill $PLATFORM_PID 2>/dev/null || true
        rm logs/platform.pid
    fi
fi

# Also kill any remaining processes on port 3001
lsof -ti:3001 | xargs kill -9 2>/dev/null || true

# Stop Client
if [ -f logs/client.pid ]; then
    CLIENT_PID=$(cat logs/client.pid)
    if ps -p $CLIENT_PID > /dev/null 2>&1; then
        echo "   Stopping Client (PID: $CLIENT_PID)"
        kill $CLIENT_PID 2>/dev/null || true
        rm logs/client.pid
    fi
fi

# Also kill any remaining processes on port 4001
lsof -ti:4001 | xargs kill -9 2>/dev/null || true

echo "✅ Frontend services stopped"
echo ""

# Stop backend services
echo "⏹️  Stopping Backend Services..."

# Stop Backend API
if [ -f logs/backend_api.pid ]; then
    API_PID=$(cat logs/backend_api.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        echo "   Stopping Backend API (PID: $API_PID)"
        kill $API_PID 2>/dev/null || true
        rm logs/backend_api.pid
    fi
fi

# Stop Celery Worker
if [ -f logs/backend_worker.pid ]; then
    WORKER_PID=$(cat logs/backend_worker.pid)
    if ps -p $WORKER_PID > /dev/null 2>&1; then
        echo "   Stopping Celery Worker (PID: $WORKER_PID)"
        kill $WORKER_PID 2>/dev/null || true
        rm logs/backend_worker.pid
    fi
fi

# Stop Celery Beat
if [ -f logs/backend_beat.pid ]; then
    BEAT_PID=$(cat logs/backend_beat.pid)
    if ps -p $BEAT_PID > /dev/null 2>&1; then
        echo "   Stopping Celery Beat (PID: $BEAT_PID)"
        kill $BEAT_PID 2>/dev/null || true
        rm logs/backend_beat.pid
    fi
fi

# Also kill any remaining processes on the ports
echo ""
echo "🧹 Cleaning up any remaining processes..."
lsof -ti:7860 | xargs kill -9 2>/dev/null || true

echo ""
echo "=========================================="
echo "✅ All services stopped!"
echo "=========================================="
echo ""
echo "Note: Docker services (MySQL, Redis, etc.) are still running."
echo "To stop Docker services, run:"
echo "  docker-compose -p bisheng down"
echo "=========================================="
