#!/bin/bash

echo "🚀 Starting A2A Strategy Agent - Unified Version"
echo "============================================="

# Determine deployment mode from environment or parameter
DEPLOYMENT_MODE=${1:-${DEPLOYMENT_MODE:-full}}

echo "🔧 Deployment Mode: $DEPLOYMENT_MODE"

# Export the mode for the API to use
export DEPLOYMENT_MODE=$DEPLOYMENT_MODE

# Start the unified API
echo "🌐 Starting unified API..."
python configs/unified_api.py

echo "👋 Shutting down..."
