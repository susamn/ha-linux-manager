#!/usr/bin/with-contenv bashio

export SUPERVISOR_TOKEN=$SUPERVISOR_TOKEN
export HOST_IP=$(bashio::config 'host_ip')

echo "Starting Linux Server Power Manager..."

# Run the FastAPI app
python3 -m uvicorn src.app:app --host 0.0.0.0 --port 8000
