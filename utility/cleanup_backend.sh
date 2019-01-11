#!/usr/bin/env bash

# Script call for cleanup after e2e tests.
cd ..
python manage.py flush --noinput
