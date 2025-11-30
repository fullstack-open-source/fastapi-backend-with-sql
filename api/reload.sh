#!/bin/bash

# =============================================
# Purpose: Activate virtual environment and start FastAPI server
# =============================================

set -e

# Colored output
info()    { echo -e "\033[1;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[1;32m[SUCCESS]\033[0m $1"; }
error()   { echo -e "\033[1;31m[ERROR]\033[0m $1"; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables
ENV_FILE="../.env"
if [ -f "$ENV_FILE" ]; then
    info "Loading environment variables..."
    while IFS= read -r line || [ -n "$line" ]; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*=.* ]]; then
            export "$line"
        fi
    done < "$ENV_FILE"
fi

# Activate virtual environment
VENV_ACTIVATE="../env/bin/activate"
if [ ! -f "$VENV_ACTIVATE" ]; then
    error "Virtual environment not found at $VENV_ACTIVATE"
    exit 1
fi

info "Activating virtual environment..."
source "$VENV_ACTIVATE"
success "Virtual environment activated"

# Configure server settings
HOST=${API_HOST:-"0.0.0.0"}
PORT=${API_PORT:-8500}
RELOAD=${API_RELOAD:-"true"}

# Check if port is already in use and kill the process
SUDO_PASSWORD="mrdas"
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    info "Port $PORT is already in use. Finding and killing the process..."
    PID=$(lsof -ti :$PORT)
    if [ -n "$PID" ]; then
        echo "$SUDO_PASSWORD" | sudo -S kill -9 "$PID" 2>/dev/null || {
            error "Failed to kill process $PID on port $PORT"
            exit 1
        }
        success "Killed process $PID using port $PORT"
    fi
fi

# Start server
echo ""
success "🚀 Starting FastAPI server at http://$HOST:$PORT"
echo ""

if [ "$RELOAD" = "true" ]; then
    python3 -m uvicorn server:app --host "$HOST" --port "$PORT" --reload --reload-dir .
else
    python3 -m uvicorn server:app --host "$HOST" --port "$PORT"
fi
