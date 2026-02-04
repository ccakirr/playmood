#!/usr/bin/env bash
set -e

echo "=== Building frontend ==="
cd frontend
npm install
npm run build

echo "=== Preparing static files ==="
rm -rf backend/static
mkdir -p /backend/static
cp -r dist/* /backend/static/

echo "=== Starting FastAPI ==="
cd /backend
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
