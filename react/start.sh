#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIDFILE="$SCRIPT_DIR/.services.pid"
LOGDIR="$SCRIPT_DIR/logs"

mkdir -p "$LOGDIR"

if [[ -f "$PIDFILE" ]]; then
    echo "Services may already be running. Check $PIDFILE or run ./stop.sh first."
    exit 1
fi

echo "Starting Snowcore Reliability Copilot services..."

cd "$SCRIPT_DIR/backend"
PYTHONPATH="$SCRIPT_DIR/backend" nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 > "$LOGDIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

cd "$SCRIPT_DIR/frontend"
nohup npm run dev > "$LOGDIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

sleep 2

cat > "$PIDFILE" << EOF
BACKEND_PID=$BACKEND_PID
BACKEND_URL=http://localhost:8000
FRONTEND_PID=$FRONTEND_PID
FRONTEND_URL=http://localhost:5173
EOF

echo ""
echo "Services started successfully!"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo ""
echo "Logs: $LOGDIR"
echo "PIDs: $PIDFILE"
echo ""
echo "Run ./stop.sh to stop services."
