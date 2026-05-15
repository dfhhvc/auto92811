#!/bin/bash
set -euo pipefail

# AutoIncome v3.0 - Container Entrypoint
# Security: Fail on error, undefined vars, pipe failures

echo "🔧 AutoIncome v3.0 Starting..."

# Validate required environment variables
if [[ -z "${AUTOINCOME_SECRET_KEY:-}" ]]; then
    echo "❌ FATAL: AUTOINCOME_SECRET_KEY is required" >&2
    exit 1
fi

# Ensure data directory exists and is writable
mkdir -p /app/data
touch /app/data/.write_test && rm -f /app/data/.write_test || {
    echo "❌ FATAL: Cannot write to /app/data" >&2
    exit 1
}

# Run database migrations (if any)
# python -m autoincome.db.migrate

echo "✅ Initialization complete. Starting server..."

# Execute the main command
exec "$@"
