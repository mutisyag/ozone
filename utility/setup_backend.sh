#!/usr/bin/env bash

# Script use by e2e tests to start the backend server if it's not already running
cd ..
set -e

python manage.py load_initial_fixtures
python manage.py make_test_users