SHELL := /bin/bash

all:

fixwindows:
	# If you are on Windows cmd or powershell, make sure you run these commands first
	# set COMPOSE_CONVERT_WINDOWS_PATHS=1
	# chcp 850

build:
	docker-compose build esimport

shell: build
	docker-compose run --rm --service-ports esimport

start-environment:
	docker-compose up -d redis mssql localstack

stop-environment:
	docker-compose stop

init-data:
	./init_mssql_db.sh

test: start-environment build init-data
	docker-compose run --rm --service-ports --entrypoint="" esimport pytest --cov-config=.coveragerc --cov=. esimport
