# Reconciliation

Four counts, one window. They are *deliberately not equal*; the point is to explain the differences exactly.

| Count | Where it comes from | What it means | Includes duplicates? |
|---|---|---|---|
| **source** | `count(*)` from the API for the window, before paging | What the portal said existed when we started | n/a (one row per record version) |
| **raw** | Sum of page row counts in manifests (re-verified against files) | Rows we actually fetched, across overlapping lookback windows | Yes |
| **curated** | Distinct `sr_number` merged this run, plus rejected rows | Unique business entities after cleaning | No |
| **warehouse** | Fact rows for this run's keys (and `load_audit`) | What analysts can query | No |

## Identities (implemented in `reconcile.compare`)

1. `source ≈ raw` within `source_vs_raw_tolerance_fraction`. Not exact because the source can change while we page (a row modified mid-run can be skipped or double-counted by offset paging).
2. `raw = rejected + duplicates_dropped + curated_distinct`. **Exact.** Every raw row is accounted for. Rejected rows are removed *before* dedupe.
3. `curated_distinct = inserted + updated + skipped_stale` from the MERGE metrics. **Exact.**
4. `warehouse rows for this run's keys = curated_distinct`. **Exact.**

## Reading failures

| Symptom | Likely meaning | Where to look |
|---|---|---|
| `source > raw` by a lot | extraction stopped early / pagination bug / API outage mid-run | extract logs, manifest `pages` |
| `source < raw` | rows added during the run; or lookback double-fetch bug | manifest timestamps |
| identity 2 off by N | rows lost in transform (or counted twice) | transform logs, quarantine table |
| identity 4 off | load partially applied (should be impossible with the txn) or wrong key selection | `load_audit`, ADR 0004 |

## Scope and caveats
- Counts are always **scoped to a run set / window**, never whole tables. Whole-table counts mix history, other windows and the source's own changes.
- A whole-table sanity check (`count(*)` in fact vs curated) is a useful *secondary* check; it must not be the primary one.
- Persist each report (JSON in storage or a warehouse table) so trends are visible: **TODO(you): where?**
