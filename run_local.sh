#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

HOST=${1:-127.0.0.1}
PORT=${2:-8000}

VENV_DIR=""
if [ -d ".venv" ]; then
  VENV_DIR=".venv"
elif [ -d "venv" ]; then
  VENV_DIR="venv"
fi

if [ -n "$VENV_DIR" ]; then
  if [ -f "$VENV_DIR/bin/activate" ]; then
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
  elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # shellcheck source=/dev/null
    source "$VENV_DIR/Scripts/activate"
  fi
fi

if command -v pipenv >/dev/null 2>&1 && [ -f "Pipfile" ]; then
  echo "Using pipenv to run the server..."
  exec pipenv run python manage.py runserver "$HOST:$PORT"
fi

VENV_PY=""
if [ -n "$VENV_DIR" ]; then
  if [ -x "$VENV_DIR/bin/python" ]; then
    VENV_PY="$VENV_DIR/bin/python"
  elif [ -x "$VENV_DIR/Scripts/python.exe" ]; then
    VENV_PY="$VENV_DIR/Scripts/python.exe"
  fi
fi

export DJANGO_SETTINGS_MODULE=web_project.settings
if [ -n "$VENV_PY" ]; then
  exec "$VENV_PY" manage.py runserver "$HOST:$PORT"
else
  exec python manage.py runserver "$HOST:$PORT"
fi
