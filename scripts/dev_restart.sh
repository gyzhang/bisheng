#!/bin/bash

# BISHENG Local Development Restart Script
# This script restarts all backend and frontend services

set -e

# Parse command line arguments (pass through to dev_start.sh)
SERVICE_TYPE="all"  # Default to restart all services

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
            echo "  --service, -s TYPE   Specify which service to restart (default: all)"
            echo "                       TYPE can be:"
            echo "                         - all:      Restart both backend and frontend"
            echo "                         - backend:  Restart backend only"
            echo "                         - frontend: Restart frontend only"
            echo ""
            echo "Examples:"
            echo "  $0                    # Restart all services"
            echo "  $0 -s backend         # Restart backend only"
            echo "  $0 --service frontend # Restart frontend only"
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

echo "🔄 Restarting BISHENG Local Development Services..."
echo "   Service Type: $SERVICE_TYPE"
echo ""

# Stop all services
echo "⏹️  Stopping services..."
"$(dirname "$0")/dev_stop.sh" --service "$SERVICE_TYPE"

# Wait a moment
echo ""
echo "⏳ Waiting for ports to be released..."
sleep 3

# Start all services
echo ""
"$(dirname "$0")/dev_start.sh" --service "$SERVICE_TYPE"
