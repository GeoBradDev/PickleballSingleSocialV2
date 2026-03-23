#!/usr/bin/env bash
set -o errexit

# Install uv if not present (Render does not include it)
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

uv sync
uv run python manage.py collectstatic --noinput
uv run python manage.py migrate
