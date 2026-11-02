"""Chicago 311 data platform.

Package map (each module's docstring states its single responsibility):

    config          typed settings: YAML (non-secret) + env vars (secrets/endpoints)
    errors          exception hierarchy -> drives retry vs fail decisions in Airflow
    logging_utils   structured logging with run_id context
    metrics         tiny metrics hook (log-based now; swap for StatsD/Prometheus later)
    storage/        ObjectStore interface + S3/MinIO implementation
    ingestion/      SODA client, extraction windows, manifests, raw extraction
    transform/      PySpark: raw JSON -> curated Delta (+ quarantine)
    quality/        data quality checks (pure functions over DataFrames/rows)
    warehouse/      Warehouse interface + Postgres loader + mart builds
    reconcile       source / raw / curated / warehouse count comparison
"""
