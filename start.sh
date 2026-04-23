#!/bin/bash
set -e

echo "Starting TITAN backend on 8010..."
uvicorn app.main:app --host 0.0.0.0 --port 8010 &

sleep 4

echo "Starting TITAN UI on 7860..."
export TITAN_API_BASE_URL="http://127.0.0.1:8010"
streamlit run ui/app.py --server.port 7860 --server.address 0.0.0.0