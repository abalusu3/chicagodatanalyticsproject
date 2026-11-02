"""Contract tests for ObjectStore. Write them ONCE, parametrize over backends:
InMemoryStore (provided) and S3ObjectStore (moto). If both pass the same tests, the interface
is real.

TODO(you): add a `store` fixture parametrized over the two backends in conftest.py.
"""

import pytest

pytestmark = pytest.mark.todo


def test_put_if_absent_writes_new_key(memory_store):
    pytest.skip("TODO: parametrize over backends")


def test_put_if_absent_raises_when_key_exists_and_does_not_overwrite(memory_store):
    """Second write with DIFFERENT bytes raises ObjectAlreadyExists; original bytes intact."""
    pytest.skip("TODO")


def test_exists_false_for_missing_but_error_for_forbidden():
    """S3 only: 404 -> False; 403 -> raises (don't hide permission bugs)."""
    pytest.skip("TODO (moto can simulate by denying via bucket policy; or mock the client)")


def test_list_keys_handles_more_than_1000_objects():
    pytest.skip("TODO: pagination")


def test_list_keys_prefix_does_not_match_sibling_prefix():
    """Prefix 'run_id=1/' must not return 'run_id=10/...'."""
    pytest.skip("TODO")


def test_uri_format():
    pytest.skip("TODO")
