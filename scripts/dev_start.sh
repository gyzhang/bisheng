#!/bin/bash

# BISHENG Local Development Startup Script
# This script starts backend and frontend services locally for development

set -e

echo "🚀 Starting BISHENG Local Development Environment..."
echo ""

# Get the absolute path of project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to backend directory
cd "$SCRIPT_DIR/../src/backend"

# Activate conda environment if exists
if command -v conda &> /dev/null; then
    echo "📦 Activating conda environment: bisheng..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate bisheng || { echo "❌ Failed to activate bisheng environment"; exit 1; }
else
    echo "⚠️  Conda not found, using system Python"
fi

# Set environment variables
export TZ="Asia/Shanghai"
export BISHENG_DATABASE_URL="mysql+pymysql://root:1234@localhost:3306/bisheng"
export BISHENG_REDIS_URL="redis://localhost:6379/0"
export BS_MILVUS_CONNECTION_ARGS='{"host":"localhost","port":"19530","user":"","password":"","secure":false}'
export BS_MILVUS_IS_PARTITION='true'
export BS_MILVUS_PARTITION_SUFFIX='1'
export BS_ELASTICSEARCH_URL='http://localhost:9200'
export BS_ELASTICSEARCH_SSL_VERIFY='{}'
export BS_MINIO_SCHEMA='false'
export BS_MINIO_CERT_CHECK='false'
export BS_MINIO_ENDPOINT='localhost:9100'
export BS_MINIO_SHAREPOINT='localhost:9100'
export BS_MINIO_ACCESS_KEY='minioadmin'
export BS_MINIO_SECRET_KEY='minioadmin'

echo "✅ Environment variables configured"

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python -c "import bisheng" 2>/dev/null; then
    echo "❌ Dependencies not fully installed or config missing."
    echo "   Please ensure you're in the conda bisheng environment and all deps are installed."
    echo "   Run: cd src/backend && uv pip install -e . --system"
    exit 1
else
    echo "✅ Dependencies check passed"
fi

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p /tmp/bisheng_data
mkdir -p ../frontend/platform/logs
mkdir -p ../frontend/client/logs
mkdir -p logs
export BS_DATA_DIR="/tmp/bisheng_data"

# Start backend API service
echo "🌐 Starting Backend API Service on http://localhost:7860"
echo "   Log file: logs/backend_api.log"
nohup python -m uvicorn bisheng.main:app \
    --host 0.0.0.0 \
    --port 7860 \
    --reload \
    > logs/backend_api.log 2>&1 &

API_PID=$!
echo $API_PID > logs/backend_api.pid
echo "✅ Backend API started (PID: $API_PID)"

sleep 3

# Start Celery worker
echo "👷 Starting Celery Worker"
echo "   Log file: logs/backend_worker.log"
nohup python -m celery -A bisheng.worker.main worker \
    --loglevel=info \
    -Q workflow_celery,knowledge_celery \
    > logs/backend_worker.log 2>&1 &

WORKER_PID=$!
echo $WORKER_PID > logs/backend_worker.pid
echo "✅ Celery Worker started (PID: $WORKER_PID)"

# Start Celery beat (scheduled tasks)
echo "⏰ Starting Celery Beat"
echo "   Log file: logs/backend_beat.log"
nohup python -m celery -A bisheng.worker.main beat \
    --loglevel=info \
    > logs/backend_beat.log 2>&1 &

BEAT_PID=$!
echo $BEAT_PID > logs/backend_beat.pid
echo "✅ Celery Beat started (PID: $BEAT_PID)"

# Wait for backend to be ready
echo ""
echo "⏳ Waiting for backend to be ready..."
sleep 5

# Start frontend services
echo ""
echo "🎨 Starting Frontend Services..."
echo ""

# Start Platform (Admin/Management)
echo "🖥️  Starting Platform (Admin/Management Portal)..."
cd "$PROJECT_ROOT/src/frontend/platform"
nohup npm run start > logs/platform.log 2>&1 &
PLATFORM_PID=$!
echo $PLATFORM_PID > logs/platform.pid
echo "✅ Platform started (PID: $PLATFORM_PID)"
echo "   Access URL: http://localhost:3001/"
echo "   Login URL: http://localhost:3001/admin/login"
echo "   Log file: logs/platform.log"

sleep 2

# Start Client (User Chat Interface)
echo ""
echo "💬 Starting Client (User Chat Interface)..."
cd "$PROJECT_ROOT/src/frontend/client"
nohup npm run start > logs/client.log 2>&1 &
CLIENT_PID=$!
echo $CLIENT_PID > logs/client.pid
echo "✅ Client started (PID: $CLIENT_PID)"
echo "   Access URL: http://localhost:4001/workspace/"
echo "   Login URL: http://localhost:4001/workspace/admin/login"
echo "   Log file: logs/client.log"

# Final status
echo ""
echo "=========================================="
echo "✅ BISHENG All Services Started!"
echo "=========================================="
echo ""
echo "Backend Services:"
echo "  🌐 Backend API:    http://localhost:7860"
echo "  📊 Swagger UI:     http://localhost:7860/docs"
echo "  🔧 ReDoc:          http://localhost:7860/redoc"
echo ""
echo "Frontend Services:"
echo "  🖥️  Platform:        http://localhost:3001/ (Admin Portal)"
echo "  💬 Client:          http://localhost:4001/workspace/ (User Interface)"
echo ""
echo "Docker Dependencies:"
echo "  📊 MySQL:          localhost:3306"
echo "  💾 Redis:          localhost:6379"
echo "  🔍 Elasticsearch:  localhost:9200"
echo "  🗄️  Milvus:         localhost:19530"
echo "  📦 MinIO:          localhost:9100"
echo ""
echo "Logs:"
echo "  API:      tail -f logs/backend_api.log"
echo "  Worker:   tail -f logs/backend_worker.log"
echo "  Beat:     tail -f logs/backend_beat.log"
echo "  Platform: tail -f logs/platform.log"
echo "  Client:   tail -f logs/client.log"
echo ""
echo "Stop services:"
echo "  ./scripts/dev_stop.sh"
echo ""
echo "Restart services:"
echo "  ./scripts/dev_restart.sh"
echo "=========================================="
echo ""
echo "🎯 Quick Start:"
echo "   Admin Login: http://localhost:3001/admin/login"
echo "   User Login:  http://localhost:4001/workspace/admin/login"
echo "   Credentials: xprogrammer@163.com / good@Man2026"
echo "=========================================="
