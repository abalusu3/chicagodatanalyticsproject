"""Typed configuration.

RESPONSIBILITY
    Single place that turns `config/pipeline.yaml` + environment variables into validated,
    immutable objects. Everything else in the project takes these objects as arguments;
    nothing else calls `os.environ`.

DESIGN DECISIONS
    - Secrets/endpoints (S3 keys, DB passwords, app token) come ONLY from env vars, never YAML.
      That is what makes "swap MinIO for AWS S3" a config change: leave S3_ENDPOINT_URL unset.
    - Models are frozen so a task cannot mutate shared config mid-run.
    - Fail at startup with a message naming the missing variable, not 40 minutes in.

SHAPE (what the YAML maps to; fields are sketched, you finish them)
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")  # extra=forbid catches YAML typos


class SourceConfig(_Frozen):
    base_url: str
    dataset_id: str
    page_size: int
    cursor_field: str
    tiebreaker_field: str
    timeout_seconds: int
    # TODO(2): add a validator: 1 <= page_size <= 50_000 (verified SODA 2.0 maximum).
    #   Why: an oversized page_size produces a confusing server-side error far from the cause.


class RetryConfig(_Frozen):
    max_attempts: int
    backoff_base_seconds: float
    backoff_max_seconds: float
    retry_on_status: list[int]
    min_request_interval_seconds: float


class ExtractionConfig(_Frozen):
    lookback_hours: int
    source_timezone: str


class StorageConfig(_Frozen):
    raw_prefix: str
    curated_table_path: str
    quarantine_table_path: str


class QualityConfig(_Frozen):
    max_quarantine_fraction: float
    chicago_bbox: dict[str, float]
    max_future_skew_minutes: int


class ReconciliationConfig(_Frozen):
    source_vs_raw_tolerance_fraction: float


class WarehouseConfig(_Frozen):
    schema_name: str  # YAML key is `schema`; map it (pydantic alias) - `schema` shadows BaseModel.
    staging_schema: str


class PipelineConfig(_Frozen):
    source: SourceConfig
    retry: RetryConfig
    extraction: ExtractionConfig
    storage: StorageConfig
    quality: QualityConfig
    reconciliation: ReconciliationConfig
    warehouse: WarehouseConfig


class Secrets(BaseSettings):
    """Environment-sourced values. SecretStr keeps passwords out of repr()/logs."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    s3_endpoint_url: str | None = None  # None => real AWS S3
    s3_access_key_id: SecretStr
    s3_secret_access_key: SecretStr
    s3_region: str = "us-east-1"
    s3_raw_bucket: str
    s3_curated_bucket: str

    warehouse_host: str
    warehouse_port: int = 5432
    warehouse_db: str
    warehouse_user: str
    warehouse_password: SecretStr

    socrata_app_token: SecretStr | None = None


def load_pipeline_config(path: Path | None = None) -> PipelineConfig:
    """Read YAML (default: $C311_CONFIG_PATH) and validate it.

    TODO(3): implement.
      1. Resolve path: argument > $C311_CONFIG_PATH > "config/pipeline.yaml".
      2. yaml.safe_load (never yaml.load).
      3. Fix the `schema` -> `schema_name` mapping for WarehouseConfig (alias or rename in YAML;
         pick one and note why in a comment).
      4. Return PipelineConfig(**data). Let pydantic's ValidationError propagate but wrap it
         so the message includes the file path.

    EDGE CASES: empty file (safe_load returns None); unknown keys (extra=forbid should reject).
    DONE WHEN: tests/unit/test_config.py passes.
    """
    raise NotImplementedError


def load_secrets() -> Secrets:
    """TODO(4): return Secrets(); on ValidationError, re-raise listing ONLY the missing variable
    names (never values). Done when a missing S3_RAW_BUCKET yields a one-line message naming it."""
    raise NotImplementedError


def warehouse_dsn(secrets: Secrets) -> str:
    """TODO(5): build a libpq-style DSN string from `secrets`.

    Keep this the *only* place that knows it's Postgres-shaped. When you move to a cloud
    warehouse, this and warehouse/postgres.py are what you replace.
    EDGE CASE: passwords with special characters (use keyword/value DSN, not a URL, or quote).
    """
    raise NotImplementedError
