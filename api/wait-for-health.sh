#!/bin/bash
# Wait for /health endpoint to return success
# Usage: wait-for-health.sh [url] [max_attempts] [interval]

set -euo pipefail

URL="${1:-http://localhost:8000/health}"
MAX_ATTEMPTS="${2:-60}"
INTERVAL="${3:-2}"

echo "Waiting for health check at ${URL}..."
echo "Max attempts: ${MAX_ATTEMPTS}, Interval: ${INTERVAL}s"

for i in $(seq 1 ${MAX_ATTEMPTS}); do
    if curl -f -s "${URL}" > /dev/null 2>&1; then
        echo "✓ Health check passed!"
        exit 0
    fi
    echo "Attempt ${i}/${MAX_ATTEMPTS}: Health check failed, retrying in ${INTERVAL}s..."
    sleep ${INTERVAL}
done

echo "✗ Health check failed after ${MAX_ATTEMPTS} attempts"
exit 1

