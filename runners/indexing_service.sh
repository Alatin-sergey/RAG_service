#!/bin/bash

echo "Starting indexing service..."
uvicorn indexing_main:app --host ${INDEXING_HOST} --port ${INDEXING_PORT} 