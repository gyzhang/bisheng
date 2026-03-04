#!/bin/bash

# BISHENG Local Development Shutdown Script
# This script stops all backend and frontend services

set -e

# Parse command line arguments
SERVICE_TYPE="all"  # Default to stop all services

while [[ $# -gt 0 ]]; do
    case $1 in
        --service|-s)
            SERVICE_TYPE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--service|--help]"
            echo ""
            echo "Options:"
            echo "  --service, -s TYPE   Specify which service to stop (default: all)"
            echo "                       TYPE can be:"
            echo "                         - all:      Stop both backend and frontend"
            echo "                         - backend:  Stop backend only"
            echo "                         - frontend: Stop frontend only"
            echo ""
            echo "Examples:"
            echo "  $0                    # Stop all services"
            echo "  $0 -s backend         # Stop backend only"
            echo "  $0 --service frontend # Stop frontend only"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Validate service type
if [[ ! "$SERVICE_TYPE" =~ ^(all|backend|frontend)$ ]]; then
    echo "❌ Invalid service type: $SERVICE_TYPE"
    echo "Valid options are: all, backend, frontend"
    echo "Use --help for usage information."
    exit 1
fi

echo "🛑 Stopping BISHENG Local Development Services..."
echo "   Service Type: $SERVICE_TYPE"
echo ""

cd "$(dirname "$0")/../src/backend"

# Stop frontend services first
if [[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "frontend" ]]; then
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
else
    echo "⏭️  Skipping frontend services"
    echo ""
fi

# Stop backend services
if [[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "backend" ]]; then
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
else
    echo "⏭️  Skipping backend services"
fi

echo ""
echo "=========================================="
echo "✅ All services stopped!"
echo "=========================================="
echo ""
echo "Note: Docker services (MySQL, Redis, etc.) are still running."
echo "To stop Docker services, run:"
echo "  docker-compose -p bisheng down"
echo "=========================================="
