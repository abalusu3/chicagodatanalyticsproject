"""S3 / MinIO implementation of ObjectStore.

RESPONSIBILITY
    Translate ObjectStore calls to boto3. Works against MinIO (endpoint_url set, path-style
    addressing) and real AWS S3 (endpoint_url None).

DESIGN DECISIONS
    - Build the boto3 client from `Secrets`; accept an injected client for tests (moto).
    - MinIO needs path-style addressing; AWS doesn't care. Set it via botocore Config.
    - Don't swallow botocore errors: map only "not found" / "already exists" to domain
      behavior; let everything else propagate (and be retried at the Airflow level).

TODOs (in order)
    1. __init__: create client (endpoint_url, credentials from SecretStr.get_secret_value(),
       region, path-style). Accept optional `client` for injection.
    2. put_if_absent: use conditional write (IfNoneMatch="*") if your boto3 + MinIO support
       it; otherwise head_object-then-put and write down the race in a comment. Map the
       precondition-failed error to ObjectAlreadyExists.
    3. get / exists: exists() must return False on 404 but RAISE on 403 (a permissions bug
       that looks like "file missing" is the worst kind of bug).
    4. list_keys: use the paginator; yield lazily.
    5. uri: f"s3://{bucket}/{key}" (Spark will need "s3a://"; convert in transform/, not here,
       and note why).

EDGE CASES: empty bytes; keys with leading "/"; prefix without trailing "/" matching
sibling prefixes ("run_id=1" vs "run_id=10").

DONE WHEN: contract tests in tests/unit/test_storage.py pass.
"""

from __future__ import annotations

from collections.abc import Iterator

from c311.config import Secrets


class S3ObjectStore:
    def __init__(self, secrets: Secrets, bucket: str, *, client: object | None = None) -> None:
        raise NotImplementedError

    def put_if_absent(self, key: str, data: bytes, *, content_type: str) -> None:
        raise NotImplementedError

    def put(self, key: str, data: bytes, *, content_type: str) -> None:
        raise NotImplementedError

    def get(self, key: str) -> bytes:
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        raise NotImplementedError

    def list_keys(self, prefix: str) -> Iterator[str]:
        raise NotImplementedError

    def uri(self, key: str) -> str:
        raise NotImplementedError
