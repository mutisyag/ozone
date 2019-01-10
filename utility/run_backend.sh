#!/usr/bin/env bash

# Script use by e2e tests to start the backend server if it's not already running

set -e

# Check if the backend server is up and running.
nc -z ${BACKEND_HOST} ${BACKEND_PORT} && exit 0

# Start server
python manage.py load_initial_fixtures
python manage.py make_test_users
nohup python manage.py runserver &

# Wait until server is up
while ! nc -z ${BACKEND_HOST} ${BACKEND_PORT}; do
  echo "Waiting for backend server at '${BACKEND_HOST}:${BACKEND_PORT}' to accept connections..."
  sleep 1s
done
