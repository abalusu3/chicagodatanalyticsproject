"""DAG structure tests. Skipped automatically if Airflow isn't installed locally (it runs inside
the docker image; you may add an `airflow` extra + CI job later)."""

import pytest

pytestmark = pytest.mark.todo


def test_dag_imports_without_errors():
    pytest.importorskip("airflow")
    pytest.skip("TODO: DagBag(dag_folder='dags', include_examples=False).import_errors == {}")


def test_task_order_is_extract_transform_quality_load_reconcile():
    pytest.importorskip("airflow")
    pytest.skip("TODO")


def test_max_active_runs_is_one_and_retries_configured():
    pytest.importorskip("airflow")
    pytest.skip("TODO")


def test_quality_and_reconcile_tasks_do_not_retry():
    pytest.importorskip("airflow")
    pytest.skip("TODO")


def test_dag_module_does_not_import_pyspark_at_top_level():
    """Parse the source with `ast` and assert no top-level pyspark/boto3 imports (scheduler
    parse-time cost). This one needs no Airflow."""
    pytest.skip("TODO")
