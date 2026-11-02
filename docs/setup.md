# Setup

> Verification status (checked when scaffolded): the package installs, `ruff check`, `ruff format --check` and `mypy` pass, every module imports, and `pytest -m "not spark and not integration"` gives 6 passed / 69 skipped. `docker-compose.yml` and `pipeline.yaml` parse as YAML. **The Docker stack has not been built or run** (Docker was not available when this was scaffolded). Expect to fix small things on first `docker compose up`, and record them here.

## Prerequisites
- Python 3.11+
- Docker Desktop (Compose v2)
- Java 17 only if you run Spark tests on the host (the Airflow image brings its own)

## 1. Local Python env (no Spark needed to start)
```bash
make venv
source .venv/bin/activate
```

## 2. Environment file
```bash
cp .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Paste the key into `AIRFLOW__CORE__FERNET_KEY`. Change the `*-change-me` passwords (they only protect your laptop, but build the habit). Optionally add a free Socrata app token.

## 3. Look at the source
```bash
make probe-api
```

## 4. Start the stack
```bash
make up
```
- Airflow UI: <http://localhost:8080>
- MinIO console: <http://localhost:9001>
- Postgres: `localhost:5432`

## 5. Tests
```bash
make test        # fast: no Spark, no Docker
make lint
```
A fresh checkout shows many *skipped* tests: each is a behavior spec waiting for your implementation.

## Known unknowns to resolve (write answers here)
- [ ] Working `JAVA_HOME` for your CPU architecture in `docker/airflow/Dockerfile`
- [ ] Spark/Delta/hadoop-aws version combination that actually works
- [ ] Whether `put_if_absent` can use conditional writes on your MinIO version
- [ ] Airflow `backfill` flags for 2.10
