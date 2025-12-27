#!/bin/bash
# Helper script to start the NVDA stock agent in the background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/nvda_agent.log"
PID_FILE="$SCRIPT_DIR/nvda_agent.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Agent is already running (PID: $PID)"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# Start the agent
cd "$SCRIPT_DIR"
nohup python3 nvda_stock_agent.py > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

echo "Agent started with PID: $PID"
echo "Log file: $LOG_FILE"
echo "To stop: ./stop_agent.sh"
echo "To view logs: tail -f $LOG_FILE"

