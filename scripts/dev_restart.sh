#!/bin/bash

# BISHENG Local Development Restart Script
# This script restarts all backend and frontend services

set -e

echo "🔄 Restarting BISHENG Local Development Services..."
echo ""

# Stop all services
echo "⏹️  Stopping all services..."
"$(dirname "$0")/dev_stop.sh"

# Wait a moment
echo ""
echo "⏳ Waiting for ports to be released..."
sleep 3

# Start all services
echo ""
"$(dirname "$0")/dev_start.sh"
