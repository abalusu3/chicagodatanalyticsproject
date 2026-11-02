"""Behavior spec for c311.config. Fill in each body, then delete the skip."""

import pytest

pytestmark = pytest.mark.todo


def test_loads_repo_pipeline_yaml():
    """ARRANGE: path to config/pipeline.yaml. ACT: load_pipeline_config(path).
    ASSERT: dataset_id == "v6vf-nfxy", page_size == 10000, retry_on_status contains 429."""
    pytest.skip("TODO: implement after load_pipeline_config")


def test_unknown_key_is_rejected(tmp_path):
    """Write a YAML with a typo'd key (e.g. `page_sise`). Expect a validation error that
    mentions the file path and the bad key."""
    pytest.skip("TODO")


def test_page_size_above_soda_max_is_rejected(tmp_path):
    """page_size: 50001 -> error; 50000 -> ok."""
    pytest.skip("TODO")


def test_empty_yaml_gives_clear_error(tmp_path):
    pytest.skip("TODO")


def test_missing_required_env_var_names_the_variable(monkeypatch):
    """Unset S3_RAW_BUCKET. Error text includes 'S3_RAW_BUCKET' and NO secret values."""
    pytest.skip("TODO")


def test_secrets_not_in_repr(monkeypatch):
    """repr(Secrets(...)) must not contain the password / secret key / app token."""
    pytest.skip("TODO")
