# Schema change policy

The source schema can change without notice. Raw is read as **all strings with an explicit schema**, so most drift shows up as *detectable* events instead of job crashes. Curated and warehouse schemas change only through the steps below.

## Classification

| Change | Class | Example |
|---|---|---|
| New field appears in source JSON | **Additive** | `brand_new_field` (see `messy_rows.json`) |
| New nullable column added to curated/warehouse by us | **Additive** | derived `resolution_hours` |
| New value in a categorical column | **Additive** (warn) | a new `status` |
| Field absent from *all* rows in a batch of meaningful size | **Breaking (suspected)** | `sr_number` disappears |
| Field renamed | **Breaking** | `sr_type` → `service_request_type` |
| Type or format change | **Breaking** | timestamps gain a timezone suffix; `ward` becomes text like "Ward 5" |
| Semantic change, same name | **Breaking** | `created_date` becomes UTC |
| Key definition changes | **Breaking** | `sr_number` no longer unique |

Note: a field missing from a *small* batch is normal (the API omits nulls). Define "meaningful size" and "how many consecutive runs" in code and record the numbers here once you've chosen them: **TODO(you)**.

## Handling

**Additive**
1. Raw: nothing to do; page files keep the field verbatim.
2. Transform: log `schema_drift_additive` with the field names; metric `c311.schema.additive_fields`.
3. Curated: the new field is **ignored** until you add it deliberately (explicit schema, no `mergeSchema` auto-evolution). Add it via a small PR: schema.py + curated DDL + warehouse DDL + a test.
4. Backfill the new column from raw if history matters (raw is immutable, so you can).

**Breaking**
1. Transform raises `SchemaDriftError` **before** touching curated. The raw files are already safe.
2. Do not "fix forward" by loosening checks. Triage per the runbook.
3. Fix = code change + (if semantics changed) a new curated table version (`service_requests_v2`) rebuilt from raw; cut warehouse over after reconciliation matches; keep v1 until consumers move.
4. Record the decision in an ADR.

## Timestamps (decision to make once)
Source timestamps are Chicago local time without an offset. Pick TIMESTAMP_NTZ (faithful) or convert to UTC (comparable across systems) and write the choice here: **TODO(you)**. Whatever you pick, DST edge cases (`window.py`) must agree with it.

## Versioning
`manifest.schema_version` versions the manifest format. Curated table changes are tracked by Delta history; keep a changelog table at the bottom of this file.

| Date | Change | Class | PR/ADR |
|---|---|---|---|
| | | | |
