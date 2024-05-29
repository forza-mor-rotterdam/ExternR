#!/usr/bin/env bash
set -euo pipefail   # crash on missing env variables, stop on any error, and exit if a pipe fails
set -x   # Enable verbose output for debugging

# Initialize celery worker
celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach
celery -A config worker -l info
