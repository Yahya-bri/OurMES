#!/usr/bin/env bash
set -euo pipefail

# Local dev launcher: Django (SQLite) + Vite frontend
# Usage: bash run-local.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
DJANGO_PORT="8000"
VITE_PORT="5173"

info() { echo -e "\033[1;34m[INFO]\033[0m $*"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $*"; }
err() { echo -e "\033[1;31m[ERR ]\033[0m $*"; }

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Missing required command: $1"
    exit 1
  fi
}

info "Working directory: $ROOT_DIR"

# Check required tools
require_cmd python3
require_cmd bash
require_cmd npm

# Backend setup
info "Setting up Python virtualenv in $VENV_DIR"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip wheel setuptools >/dev/null

info "Installing backend requirements"
pip install -r "$BACKEND_DIR/requirements.txt"

export DJANGO_SETTINGS_MODULE="ourmes_backend.settings.dev"
export PYTHONUNBUFFERED=1

pushd "$BACKEND_DIR" >/dev/null
info "Applying migrations (SQLite)"
python manage.py migrate --noinput

if [[ -f "$BACKEND_DIR/db.sqlite3" ]]; then
  info "SQLite DB present at backend/db.sqlite3"
else
  info "No SQLite DB found, creating and seeding sample data"
fi

if [[ -f "$BACKEND_DIR/load_sample_data.py" ]]; then
  info "Loading sample data"
  python "$BACKEND_DIR/load_sample_data.py" || warn "Sample data loader exited with non-zero status"
else
  warn "Sample data loader not found at backend/load_sample_data.py"
fi

info "Starting Django dev server on :$DJANGO_PORT"
python manage.py runserver 0.0.0.0:$DJANGO_PORT &
BACKEND_PID=$!
popd >/dev/null

# Frontend setup
pushd "$FRONTEND_DIR" >/dev/null
if [[ ! -d node_modules ]]; then
  info "Installing frontend dependencies (npm install)"
  npm install
fi

info "Starting Vite dev server on :$VITE_PORT"
# --host allows cross-origin from other devices if needed
npm run dev -- --host --port "$VITE_PORT" &
FRONTEND_PID=$!
popd >/dev/null

# Cleanup and wait
cleanup() {
  info "Shutting down dev servers..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" 2>/dev/null || true
  wait "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

info "Backend:  http://localhost:$DJANGO_PORT/"
info "Frontend: http://localhost:$VITE_PORT/"
info "Press Ctrl+C to stop both servers"

# Wait for any process to exit, then cleanup via trap
wait -n "$BACKEND_PID" "$FRONTEND_PID"
