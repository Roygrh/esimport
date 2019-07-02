#!/usr/bin/env bash
set -x
docker-compose up -d
sleep 10
python -m pytest --cov=esimport_retention --cov-report=term-missing
docker-compose down
