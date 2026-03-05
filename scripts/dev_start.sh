#!/bin/bash

# BISHENG Local Development Startup Script
# This script starts backend and frontend services locally for development

set -e

# Parse command line arguments
SERVICE_TYPE="all"  # Default to start all services

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
            echo "  --service, -s TYPE   Specify which service to start (default: all)"
            echo "                       TYPE can be:"
            echo "                         - all:      Start both backend and frontend"
            echo "                         - backend:  Start backend only"
            echo "                         - frontend: Start frontend only"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start all services"
            echo "  $0 -s backend         # Start backend only"
            echo "  $0 --service frontend # Start frontend only"
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

echo "🚀 Starting BISHENG Local Development Environment..."
echo "   Service Type: $SERVICE_TYPE"
echo ""

# Get the absolute path of project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_ROOT="$PROJECT_ROOT/src/backend"
LOGS_DIR="$PROJECT_ROOT/logs"

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p /tmp/bisheng_data
mkdir -p "$LOGS_DIR"
mkdir -p "$LOGS_DIR/backend"
mkdir -p "$LOGS_DIR/platform"
mkdir -p "$LOGS_DIR/client"
export BS_DATA_DIR="/tmp/bisheng_data"

# Change to backend directory
cd "$BACKEND_ROOT"
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
if [[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "backend" ]]; then
    echo "🌐 Starting Backend API Service on http://localhost:7860"
    echo "   Log file: $LOGS_DIR/backend/backend_api.log"
    nohup python -m uvicorn bisheng.main:app \
        --host 0.0.0.0 \
        --port 7860 \
        --reload \
        > "$LOGS_DIR/backend/backend_api.log" 2>&1 &
    
    API_PID=$!
    echo $API_PID > "$LOGS_DIR/backend/backend_api.pid"
    echo "✅ Backend API started (PID: $API_PID)"
    
    sleep 3
    
    # Start Celery worker
    echo "👷 Starting Celery Worker"
    echo "   Log file: $LOGS_DIR/backend/backend_worker.log"
    nohup python -m celery -A bisheng.worker.main worker \
        --loglevel=info \
        -Q workflow_celery,knowledge_celery \
        > "$LOGS_DIR/backend/backend_worker.log" 2>&1 &
    
    WORKER_PID=$!
    echo $WORKER_PID > "$LOGS_DIR/backend/backend_worker.pid"
    echo "✅ Celery Worker started (PID: $WORKER_PID)"
    
    # Start Celery beat (scheduled tasks)
    echo "⏰ Starting Celery Beat"
    echo "   Log file: $LOGS_DIR/backend/backend_beat.log"
    nohup python -m celery -A bisheng.worker.main beat \
        --loglevel=info \
        > "$LOGS_DIR/backend/backend_beat.log" 2>&1 &
    
    BEAT_PID=$!
    echo $BEAT_PID > "$LOGS_DIR/backend/backend_beat.pid"
    echo "✅ Celery Beat started (PID: $BEAT_PID)"
    
    # Wait for backend to be ready
    echo ""
    echo "⏳ Waiting for backend to be ready..."
    sleep 5
else
    echo "⏭️  Skipping backend services"
fi

# Start frontend services
if [[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "frontend" ]]; then
    echo ""
    echo "🎨 Starting Frontend Services..."
    echo ""
    
    # Start Platform (Admin/Management)
    echo "🖥️  Starting Platform (Admin/Management Portal)..."
    cd "$PROJECT_ROOT/src/frontend/platform"
    nohup npm run start > "$LOGS_DIR/platform/platform.log" 2>&1 &
    PLATFORM_PID=$!
    echo $PLATFORM_PID > "$LOGS_DIR/platform/platform.pid"
    echo "✅ Platform started (PID: $PLATFORM_PID)"
    echo "   Access URL: http://localhost:3001/"
    echo "   Login URL: http://localhost:3001/admin/login"
    echo "   Log file: $LOGS_DIR/platform/platform.log"
    
    sleep 2
    
    # Start Client (User Chat Interface)
    echo ""
    echo "💬 Starting Client (User Chat Interface)..."
    cd "$PROJECT_ROOT/src/frontend/client"
    nohup npm run start > "$LOGS_DIR/client/client.log" 2>&1 &
    CLIENT_PID=$!
    echo $CLIENT_PID > "$LOGS_DIR/client/client.pid"
    echo "✅ Client started (PID: $CLIENT_PID)"
    echo "   Access URL: http://localhost:4001/workspace/"
    echo "   Login URL: http://localhost:4001/workspace/admin/login"
    echo "   Log file: $LOGS_DIR/client/client.log"
else
    echo "⏭️  Skipping frontend services"
fi

# Final status
echo ""
echo "=========================================="
echo "✅ BISHENG Services Started!"
echo "=========================================="
echo ""
if [[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "backend" ]]; then
    echo "Backend Services:"
    echo "  🌐 Backend API:    http://localhost:7860"
    echo "  📊 Swagger UI:     http://localhost:7860/docs"
    echo "  🔧 ReDoc:          http://localhost:7860/redoc"
    echo ""
fi
if [[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "frontend" ]]; then
    echo "Frontend Services:"
    echo "  🖥️  Platform:        http://localhost:3001/ (Admin Portal)"
    echo "  💬 Client:          http://localhost:4001/workspace/ (User Interface)"
    echo ""
fi
if [[ "$SERVICE_TYPE" == "all" ]]; then
    echo "Docker Dependencies:"
    echo "  📊 MySQL:          localhost:3306"
    echo "  💾 Redis:          localhost:6379"
    echo "  🔍 Elasticsearch:  localhost:9200"
    echo "  🗄️  Milvus:         localhost:19530"
    echo "  📦 MinIO:          localhost:9100"
    echo ""
fi
echo "Logs:"
[[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "backend" ]] && echo "  API:      tail -f $LOGS_DIR/backend/backend_api.log"
[[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "backend" ]] && echo "  Worker:   tail -f $LOGS_DIR/backend/backend_worker.log"
[[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "backend" ]] && echo "  Beat:     tail -f $LOGS_DIR/backend/backend_beat.log"
[[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "frontend" ]] && echo "  Platform: tail -f $LOGS_DIR/platform/platform.log"
[[ "$SERVICE_TYPE" == "all" || "$SERVICE_TYPE" == "frontend" ]] && echo "  Client:   tail -f $LOGS_DIR/client/client.log"
echo ""
echo "Stop services:"
echo "  ./scripts/dev_stop.sh [-s service_type]"
echo ""
echo "Restart services:"
echo "  ./scripts/dev_restart.sh [-s service_type]"
echo "=========================================="
echo ""
echo "🎯 Quick Start:"
echo "   Admin Login: http://localhost:3001/admin/login"
echo "   User Login:  http://localhost:4001/workspace/admin/login"
echo "   Credentials: xprogrammer@163.com / good@Man2026"
echo "=========================================="
