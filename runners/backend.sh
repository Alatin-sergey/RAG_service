#!/bin/bash

echo "Starting backend service..."
uvicorn backend:app --host ${BACKEND_HOST} --port ${BACKEND_PORT}