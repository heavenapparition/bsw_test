#!/bin/bash

# Wait for the database to be ready (you might want to add a proper wait script here)
# sleep 5

# Run migrations
alembic upgrade head

# Start the application
exec uvicorn app:app --host 0.0.0.0 --port 8800
