#!/bin/bash
# safe_exec.sh – Sandboxed command executor
# Usage: safe_exec.sh "<quoted command>"

LOG_DIR="$(dirname "$0")/../../logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/bash_exec.log"

CMD="$1"
if [[ -z "$CMD" ]]; then
    echo '{"error":"No command provided"}' 
    exit 1
fi

# Log command with timestamp
echo "$(date -Iseconds) EXEC: $CMD" >> "$LOG_FILE"

# Restrict execution to workspace directory
cd "$(dirname "$0")/../../workspace" || exit 1

# Execute and capture output
output=$(eval "$CMD" 2>&1)
exit_code=$?

# Log result
echo "$(date -Iseconds) EXIT: $exit_code" >> "$LOG_FILE"

printf '{"stdout":"%s","stderr":"%s","returncode":%d}\n' \
    "$(echo "$output" | sed 's/"/\\"/g')" "" $exit_code
