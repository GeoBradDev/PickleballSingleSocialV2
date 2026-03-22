# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack pickleball singles social app. Django backend with a React (Vite) frontend. Early-stage, scaffolded and ready for feature development.

## Commands

### Backend (from `backend/`)

```bash
uv run python manage.py runserver       # Start Django dev server
uv run python manage.py migrate         # Apply migrations
uv run python manage.py makemigrations  # Generate migrations after model changes
uv run python manage.py createsuperuser # Create admin user
uv run python manage.py test            # Run all tests
uv run python manage.py test api        # Run tests for the api app
```

### Frontend (from `frontend/`)

```bash
npm run dev       # Start Vite dev server with HMR
npm run build     # Production build
npm run lint      # ESLint
npm run preview   # Preview production build
```

## Architecture

- **`backend/`** - Django 6.0.3 project using `uv` as the Python package manager
  - `PickleballSinglesSocialV2/` - Django project config (settings, root URLs)
  - `api/` - Main Django app (models, views, admin)
  - Database: SQLite (`db.sqlite3`)
- **`frontend/`** - React 19 SPA built with Vite 8
  - `src/App.jsx` - Root component
  - `src/main.jsx` - Entry point
  - ESLint configured with React hooks and refresh plugins

## Key Details

- Frontend uses JavaScript only, no TypeScript
- Backend virtual environment lives at `backend/.venv/`
- Django is in DEBUG mode with default SQLite for local development
- No API endpoints or models are defined yet; `api/views.py` and `api/models.py` are empty stubs
