"""SparkSession factory (local mode + Delta + S3A).

RESPONSIBILITY
    Build ONE correctly configured SparkSession for both Airflow tasks and tests. Isolating
    this is what lets you later swap to a cluster/EMR/Databricks by changing only this file.

REQUIRED CONFIGURATION (what each piece is for - look each up, don't copy blindly)
    - Delta: `spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension` and
      `spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog`.
      Easiest: `delta.configure_spark_with_delta_pip(builder)` which also resolves the jar.
    - S3A (MinIO): `spark.hadoop.fs.s3a.endpoint`, `.access.key`, `.secret.key`,
      `.path.style.access=true`, `.connection.ssl.enabled=false` for http MinIO.
      Needs `org.apache.hadoop:hadoop-aws` matching Spark's bundled Hadoop (Spark 3.5.1 ships
      Hadoop 3.3.4 -> hadoop-aws:3.3.4 and its aws-java-sdk-bundle). Version mismatches show up
      as NoSuchMethodError / ClassNotFoundException: that is THE classic failure here.
    - Timezone: set `spark.sql.session.timeZone`. Think: source timestamps are Chicago local
      with no offset. Do you store them as TIMESTAMP_NTZ (no zone semantic, faithful to the
      source) or convert to UTC? Decide once; document in docs/schema-policy.md.
    - Local-mode sizing: `local[*]`, modest `spark.sql.shuffle.partitions` (the default 200
      is absurd for one laptop and for daily deltas of ~thousands of rows).

PITFALLS
    - Jars are downloaded at session start via `spark.jars.packages` -> needs internet in the
      container, and is slow the first time. Mention in setup docs; consider baking jars into
      the image as a later optimization.
    - Never put credentials in a log line or in `SparkConf` dumps you print.

TODOs: implement `get_spark(secrets, app_name)`. Keep it idempotent (getOrCreate).
DONE WHEN: `get_spark(...).range(3).write.format("delta").save("s3a://c311-curated/_smoke")`
works against MinIO and you can read it back (do this by hand once; then delete `_smoke`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from c311.config import Secrets

if TYPE_CHECKING:  # keep pyspark an optional import for the fast test job
    from pyspark.sql import SparkSession


def get_spark(secrets: Secrets, app_name: str = "c311") -> SparkSession:
    raise NotImplementedError
