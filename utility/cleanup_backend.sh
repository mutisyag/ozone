#!/usr/bin/env bash

# Script call for cleanup after e2e tests.

python manage.py flush --noinput
