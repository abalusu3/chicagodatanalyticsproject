#!/bin/bash
# Runs once, on first start of an empty Postgres volume (docker-entrypoint-initdb.d).
# Creates two isolated databases/roles: Airflow metadata and the analytical warehouse.
# To re-run after changing this file: `docker compose down -v` (DESTROYS local data).
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
  CREATE ROLE ${AIRFLOW_DB_USER} LOGIN PASSWORD '${AIRFLOW_DB_PASSWORD}';
  CREATE DATABASE ${AIRFLOW_DB} OWNER ${AIRFLOW_DB_USER};

  CREATE ROLE ${WAREHOUSE_USER} LOGIN PASSWORD '${WAREHOUSE_PASSWORD}';
  CREATE DATABASE ${WAREHOUSE_DB} OWNER ${WAREHOUSE_USER};
EOSQL

# Schemas are created by the pipeline's DDL (sql/warehouse/001_schemas.sql), not here,
# so the same DDL can target a cloud warehouse later.
