# Airflow + Java (for PySpark local mode) + the pipeline's Python deps.
# Pinned versions are starting points: if the build fails on a conflict, resolve it and
# record the working combination in docs/setup.md.
FROM apache/airflow:2.10.4-python3.11

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
# NOTE: JAVA_HOME differs on amd64 (…-amd64). TODO(you): make this arch-agnostic
# (e.g. `ln -s` a stable path in the RUN step above) so the image builds on both.

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
