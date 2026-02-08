#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$SCRIPT_DIR/.services.pid"

if [[ ! -f "$PIDFILE" ]]; then
    echo "No pidfile found at $PIDFILE"
    echo "Services may not be running or were started manually."
    exit 1
fi

source "$PIDFILE"

echo "Stopping Snowcore Reliability Copilot services..."

if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null && echo "Backend stopped (PID: $BACKEND_PID)"
else
    echo "Backend not running (PID: $BACKEND_PID)"
fi

if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null && echo "Frontend stopped (PID: $FRONTEND_PID)"
else
    echo "Frontend not running (PID: $FRONTEND_PID)"
fi

rm -f "$PIDFILE"
echo ""
echo "Services stopped. Pidfile removed."
