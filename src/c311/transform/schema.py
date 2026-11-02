"""Raw and curated schemas + schema-drift detection.

RESPONSIBILITY
    The explicit, versioned definition of (a) what we expect to read from raw JSON and
    (b) what the curated Delta table looks like. Also detects drift between an incoming
    batch and the expected schema, classifying it per docs/schema-policy.md.

WHY EXPLICIT SCHEMAS (not inferSchema)
    Inference over a small/odd batch gives different types on different days (a batch where
    every `zip_code` is numeric-looking infers a number and breaks on the next batch).
    Read raw as STRINGS with an explicit schema; cast deliberately in raw_to_curated.py, so
    a bad value becomes a quarantined row, not a failed job.

RAW READ SCHEMA (all StringType except where JSON structure forces otherwise)
    Source fields (39, verified): sr_number, sr_type, sr_short_code, created_department,
    owner_department, status, origin, created_date, last_modified_date, closed_date,
    street_address, city, state, zip_code, street_number, street_direction, street_name,
    street_type, duplicate, legacy_record, legacy_sr_number, parent_sr_number, community_area,
    ward, electrical_district, electricity_grid, police_sector, police_district, police_beat,
    precinct, sanitation_division_days, created_hour, created_day_of_week, created_month,
    x_coordinate, y_coordinate, latitude, longitude, location{latitude,longitude,...}.
    Observed in a sample: `duplicate` / `legacy_record` are JSON booleans, `location` is an
    object, and missing values are omitted rather than null. Decide how your read schema
    treats each (reading a boolean into StringType works in Spark; check it).

CURATED SCHEMA (suggested; challenge it)
    key               sr_number STRING (primary key, NOT NULL)
    descriptive       sr_type, sr_short_code, created_department, owner_department, status,
                      origin, parent_sr_number, legacy_sr_number
    timestamps        created_ts, last_modified_ts, closed_ts   (TIMESTAMP_NTZ)
    address/geo       street_address, zip_code(STRING!), ward(INT), community_area(INT),
                      police_district(STRING - leading zeros "06"), police_beat(STRING),
                      latitude/longitude(DOUBLE), x_coordinate/y_coordinate(DOUBLE)
    flags             is_duplicate(BOOLEAN), is_legacy_record(BOOLEAN)
    derived           created_date (DATE, partition candidate - think about cardinality!)
    lineage           _run_id, _manifest_key, _source_file, _ingested_at_utc, _row_hash

    Why STRING for zip/police_district: identifiers, not quantities; casting loses leading
    zeros and invites arithmetic nobody wants.

TODOs (in order)
    1. Build RAW_SCHEMA (pyspark StructType) from the field list above.
    2. Build CURATED_SCHEMA and EXPECTED_RAW_FIELDS (a frozenset used by drift detection).
    3. `detect_drift(incoming_fields) -> DriftReport`: classify
         - new field not in EXPECTED (ADDITIVE)
         - expected field absent from the WHOLE batch (possible BREAKING: removed/renamed)
         - Caveat: a field absent from a small batch is normal (nulls are omitted!). Think
           about how many runs/rows must lack it before you call it removed.
       Type drift can't show up on all-string reads; it shows up as cast failures. Where do
       you detect "100% of ward values suddenly fail to cast"? (quality checks, thresholds.)
    4. `DriftReport.raise_if_breaking()` -> SchemaDriftError with hint pointing to the policy doc.

DONE WHEN: tests/unit/test_schema.py passes; the 12-row sample fixture reads with zero drift.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DriftReport:
    additive: list[str] = field(default_factory=list)  # new fields
    missing: list[str] = field(default_factory=list)  # expected-but-absent fields
    breaking: bool = False

    def raise_if_breaking(self) -> None:
        raise NotImplementedError


EXPECTED_RAW_FIELDS: frozenset[str] = frozenset()  # TODO(2): fill from the field list above

RAW_SCHEMA = None  # TODO(1): pyspark.sql.types.StructType
CURATED_SCHEMA = None  # TODO(2): pyspark.sql.types.StructType


def detect_drift(incoming_fields: set[str]) -> DriftReport:
    raise NotImplementedError
