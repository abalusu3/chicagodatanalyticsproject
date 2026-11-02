.PHONY: help venv lint fmt typecheck test test-all up down logs probe-api

help:
	@grep -E '^[a-z-]+:' Makefile | cut -d: -f1

venv:            ## local dev env (no Spark)
	python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

lint:
	ruff check . && ruff format --check .

fmt:
	ruff check --fix . && ruff format .

typecheck:
	mypy

test:            ## fast tests only (no Spark, no docker)
	pytest -m "not spark and not integration"

test-all:        ## needs `pip install -e ".[spark,dev]"` and `make up`
	pytest

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f airflow-scheduler

probe-api:       ## sanity-check the source API (2 rows)
	curl -s "https://data.cityofchicago.org/resource/v6vf-nfxy.json?\$$limit=2&\$$order=:id" | python3 -m json.tool | head -40
