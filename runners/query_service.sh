#!/bin/bash

echo "Starting query service..."
uvicorn query_main:app --host ${QUERY_HOST} --port ${QUERY_PORT} 