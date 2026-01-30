#!/bin/bash
set -e

# Start uvicorn in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 5 &
UVICORN_PID=$!

# Wait for the API to be ready
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        echo "API is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "API failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Call update-capabilities endpoint
echo "Updating capabilities..."
if curl -X GET http://localhost:8000/admin/update-capabilities; then
    echo "Capabilities updated successfully"
else
    echo "Warning: Failed to update capabilities"
fi

# Bring uvicorn to the foreground
wait $UVICORN_PID
