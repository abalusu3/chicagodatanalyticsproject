"""ObjectStore interface.

RESPONSIBILITY
    The ONLY storage abstraction ingestion code may depend on. Implementations: S3/MinIO
    (storage/s3.py) now; a local-filesystem fake for tests; GCS/ADLS later if you want.
    (Spark/Delta reads and writes via s3a:// URIs directly; this interface covers the
    non-Spark paths: raw files, manifests.)

DESIGN DECISIONS
    - Tiny surface on purpose. Every method you add is a method you must implement and test
      for each backend.
    - `put_if_absent` is how "raw files are immutable" is *enforced*, not just promised.
      Think about what the semantics are on S3 (conditional writes via If-None-Match are
      supported on current S3; verify for your boto3 version and for MinIO) and what you do
      if a backend can't do atomic create-if-absent (check-then-write has a race; is that
      acceptable when Airflow runs max_active_runs=1? Document your answer in ADR 0003).
    - Keys are plain strings with "/" separators; bucket is bound at construction.

DONE WHEN
    - Protocol is stable and tests/unit/test_storage.py's contract tests pass against the
      S3 implementation (moto) and against an in-memory fake.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol


class ObjectAlreadyExists(Exception):
    """Raised by put_if_absent when the key exists. Callers decide if that's fine (idempotent
    rerun with identical bytes) or a bug (different bytes under the same key)."""


class ObjectStore(Protocol):
    def put_if_absent(self, key: str, data: bytes, *, content_type: str) -> None:
        """Write `data` at `key` only if nothing is there. Raise ObjectAlreadyExists otherwise."""
        ...

    def put(self, key: str, data: bytes, *, content_type: str) -> None:
        """Overwrite allowed. Use ONLY for non-raw artifacts (e.g. latest-pointer files)."""
        ...

    def get(self, key: str) -> bytes: ...

    def exists(self, key: str) -> bool: ...

    def list_keys(self, prefix: str) -> Iterator[str]:
        """Yield all keys under prefix (handle pagination of >1000 keys)."""
        ...

    def uri(self, key: str) -> str:
        """Fully qualified URI (s3://bucket/key) for handing to Spark."""
        ...
