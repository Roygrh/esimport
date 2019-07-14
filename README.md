# ElasticSearch Import Project

The overall task is to move data from Eleven's T-SQL database into ElasticSearch.

## Setup and contributing

We encourage docker-based development workflow, this project includes a [Dockerfile](Dockerfile) that uses the same Linux distrobution as production. 

Doing so, we make sure all devs have almost the same environment, services and system dependencies versions, and esimport behaves the same to all
of us. 

- Copy `_docker-compose.example.yml` file into `docker-compose.yml`.
- Copy `_local_settings.example.py` file into `local_settings.py` file. 
- In a separate terminal window, run: `make start-environment`, this will start up ElasticSearch, Redis and MS SQL Server.
- Run `make shell`. This will drop you in a bash shell in a separate docker container, with `esimport` CLI available and tests ready to invoke. You can modify the code-base without running `make shell` again, just modify and re-invoke `esimport` or tests within the same shell.


## Usage

esimport syncs (or updates) 05 types of documents to Elasticsearch, accounts, conferences, devices, properties and sessions. This can be done with:

```bash
$ esimport sync [account|device|session|property]
```

and:

```bash
$ esimport update conference
```

e.g. 
- `esimport sync device` (notice device is not in the plural form).
- `esimport update conference` (also not in plural)

All of the above commands accept `--start-date` argument, e.g.

```bash
$ esimport sync session --start-date 2018-01-01
```

You may want to start with `esimport sync property` first, since the rest of document types may rely on the presence of some properties.

## How to run tests?

Just invoke `tox` or `pytest`. 

To run a specific tests, invoke `pytest esimport/tests/test_conferencemapping_es.py`.

Make sure, you're inside a shell with `make shell` and ES, Redis and MSSQL are up with `make start-environment`.

### Using esimport outside Docker

docker-compose can be used to spin up MSSQL Server, Redis or ElasticSearch only, without necessarily the esimport service. You can start any of these services at will with `docker-compose up redis mssql elasticsearch`, drop any service name from the command to NOT spin it (e.g. it's installed on your machine).

Once these services are up, you can access them from your host machine like so:
- ElasticSearch: `localhost:9200`
- MSSQL Server: `localhost:1433`, user: `sa`, password: `DistroDev@11` (You have to create the databases: Eleven_OS, Radius)
- Redis: `localhost:6379`.

### Only esimport inside Docker

You may want to run only `esimport` service inside docker, while instructing it to use the Elasticsearch, Redis and MSSQL Server of your host machine. In this case you have to pass `--net="host"` to your `docker run` command, or add `network_mode: "host"` to your `docker-compose.yml` file.
