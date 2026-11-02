"""Shared fixtures.

Provided for you (test infrastructure, not pipeline logic):
    sample_rows / sample_page_bytes   real API sample (tests/fixtures/sample_311_page1.json)
    messy_rows                        synthetic edge cases (see tests/fixtures/README.md)
    InMemoryStore / memory_store      a dict-backed ObjectStore for tests that don't need S3
    spark                             session-scoped local SparkSession (skips if pyspark missing)

Your job: S3-backed and Postgres-backed fixtures for the integration tests (marked TODO below).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from c311.storage.base import ObjectAlreadyExists

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_page_bytes() -> bytes:
    """Exactly the bytes the API returned (this is what a raw page file must contain)."""
    return (FIXTURES / "sample_311_page1.json").read_bytes()


@pytest.fixture(scope="session")
def sample_rows(sample_page_bytes: bytes) -> list[dict]:
    return json.loads(sample_page_bytes)


@pytest.fixture(scope="session")
def messy_rows() -> list[dict]:
    return json.loads((FIXTURES / "messy_rows.json").read_text())


class InMemoryStore:
    """Dict-backed ObjectStore. Mirrors the contract in storage/base.py."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put_if_absent(self, key: str, data: bytes, *, content_type: str) -> None:
        if key in self.objects:
            raise ObjectAlreadyExists(key)
        self.objects[key] = data

    def put(self, key: str, data: bytes, *, content_type: str) -> None:
        self.objects[key] = data

    def get(self, key: str) -> bytes:
        return self.objects[key]

    def exists(self, key: str) -> bool:
        return key in self.objects

    def list_keys(self, prefix: str) -> Iterator[str]:
        yield from sorted(k for k in self.objects if k.startswith(prefix))

    def uri(self, key: str) -> str:
        return f"memory://{key}"


@pytest.fixture
def memory_store() -> InMemoryStore:
    return InMemoryStore()


@pytest.fixture(scope="session")
def spark():
    """Local SparkSession for tests marked @pytest.mark.spark.

    TODO(you): once transform/spark_session.py exists you may reuse it, but unit tests should
    NOT need MinIO: build a plain local session with the Delta extensions and a tmp warehouse
    dir, so Delta merge logic is testable against the local filesystem.
    """
    pytest.importorskip("pyspark")
    pytest.skip("TODO: build a local Delta-enabled SparkSession fixture")


# TODO(you): `s3_store` fixture: moto-backed S3ObjectStore (unit) and a MinIO-backed one
#   (integration, marked). `warehouse` fixture: PostgresWarehouse against the compose DB with
#   a per-test schema or truncation so tests don't leak into each other.
