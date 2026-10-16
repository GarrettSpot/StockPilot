#!/usr/bin/env bash
# Simple CPU load generator for demonstrating the Horizontal Pod Autoscaler.
# Usage: ./scripts/load-test.sh [URL] [REQUESTS] [CONCURRENCY]
set -euo pipefail

URL="${1:-http://localhost:8000/api/products}"
REQUESTS="${2:-20000}"
CONCURRENCY="${3:-50}"

echo "Generating load against ${URL} (${REQUESTS} requests, concurrency ${CONCURRENCY})"

if command -v hey >/dev/null 2>&1; then
  hey -n "${REQUESTS}" -c "${CONCURRENCY}" "${URL}"
elif command -v ab >/dev/null 2>&1; then
  ab -n "${REQUESTS}" -c "${CONCURRENCY}" "${URL}"
else
  echo "Neither 'hey' nor 'ab' is installed. Install one of them to run this script." >&2
  echo "  hey: go install github.com/rakyll/hey@latest" >&2
  echo "  ab : sudo apt install apache2-utils" >&2
  exit 1
fi
