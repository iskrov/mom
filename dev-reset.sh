#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

BACKEND_LOG="$ROOT_DIR/.dev-backend.log"
FRONTEND_LOG="$ROOT_DIR/.dev-frontend.log"
BACKEND_PID_FILE="$ROOT_DIR/.dev-backend.pid"
FRONTEND_PID_FILE="$ROOT_DIR/.dev-frontend.pid"

kill_listeners() {
  local port="$1"
  local pids
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "Stopping listeners on :$port -> $pids"
    # shellcheck disable=SC2086
    kill $pids || true
    sleep 1
  fi
}

if [[ ! -f "$ROOT_DIR/venv/bin/activate" ]]; then
  echo "Missing backend venv at: $ROOT_DIR/venv"
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but not installed or not in PATH."
  exit 1
fi

kill_listeners "$BACKEND_PORT"
kill_listeners "$FRONTEND_PORT"

echo "Starting backend on :$BACKEND_PORT"
(
  cd "$ROOT_DIR"
  # shellcheck disable=SC1091
  source venv/bin/activate
  nohup python -m uvicorn server.main:app --reload --port "$BACKEND_PORT" >"$BACKEND_LOG" 2>&1 &
  echo $! >"$BACKEND_PID_FILE"
)

echo "Starting frontend on :$FRONTEND_PORT"
(
  cd "$ROOT_DIR/frontend"
  nohup npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" >"$FRONTEND_LOG" 2>&1 &
  echo $! >"$FRONTEND_PID_FILE"
)

sleep 2

APP_URL="http://localhost:$FRONTEND_PORT"
if command -v open >/dev/null 2>&1; then
  open "$APP_URL" >/dev/null 2>&1 || true
fi

echo "Done."
echo "Frontend: $APP_URL"
echo "Backend:  http://127.0.0.1:$BACKEND_PORT"
echo "Backend log:  $BACKEND_LOG"
echo "Frontend log: $FRONTEND_LOG"
