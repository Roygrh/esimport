SHELL := /bin/bash

all:

fixwindows:
	# If you are on Windows cmd or powershell, make sure you run these commands first
	# set COMPOSE_CONVERT_WINDOWS_PATHS=1
	# chcp 850


shell:
	docker-compose build esimport
	docker-compose run --rm --service-ports esimport

start-environment:
	# add -d to make these run in the background
	docker-compose up redis mssql elasticsearch


stop-environment:
	docker-compose stop
