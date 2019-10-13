#!/usr/bin/env bash


export LOOK_BACK_FOR_X_MINUTES=1
export ES_URL="https://fake-will-not-be-used.us-west-2.es.amazonaws.com/"

docker-compose up -d

# to allow ElasticSearch in Docker start
sleep 10
python -m pytest \
	-x \
	--cov=esimport_datadog \
	--cov-report=term-missing \
 	tests

docker-compose down

