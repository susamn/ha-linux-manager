#!/usr/bin/with-contenv bashio

echo "Starting Linux Server Power Manager..."

# Run the FastAPI app
# Python path is set to the current directory which is /app
python3 -m uvicorn src.app:app --host 0.0.0.0 --port 8000
