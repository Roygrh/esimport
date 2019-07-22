#!/usr/bin/env bash

export LOOK_BACK_FOR_X_MINUTES=1
export ES_URL="https://fake-will-not-be-used.us-west-2.es.amazonaws.com/"

python -m pytest \
	-x \
	--cov=esimport_datadog \
	--cov-report=term-missing \
 	tests/units
