#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Starting Postgres..."
docker compose -f "$ROOT_DIR/backend/docker-compose.yml" --env-file /dev/null up -d

echo "Waiting for Postgres to accept connections..."
until docker compose -f "$ROOT_DIR/backend/docker-compose.yml" --env-file /dev/null exec db pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done

echo "Running migrations..."
cd "$ROOT_DIR/backend"
uv run python manage.py migrate

echo "Starting Django backend..."
uv run python manage.py runserver &
BACKEND_PID=$!

echo "Starting Vite frontend..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Dev stack is up:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
