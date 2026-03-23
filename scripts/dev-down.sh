#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Stopping Django and Vite processes..."
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "Stopping Postgres..."
docker compose -f "$ROOT_DIR/backend/docker-compose.yml" --env-file /dev/null down

echo "Dev stack is down."
