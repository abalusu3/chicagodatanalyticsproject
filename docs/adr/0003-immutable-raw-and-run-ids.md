# ADR 0003: Immutable raw files, manifest-as-commit, and run-id policy

- **Status:** Proposed. **You must decide the run-id question below.**
- **Date:** 2026-11-02

## Context
Raw data must be trustworthy for replays and audits. Object stores have no multi-file transactions, so "complete run" needs an explicit marker.

## Decision (partly pre-filled)
- Raw page files are written with `put_if_absent` and never modified.
- `_manifest.json` is written last; downstream reads only runs that have one.
- Page files store the exact response bytes; the manifest holds sha256 and counts.

## To decide
**Does a retried Airflow task reuse the run_id or create a new one?**
- Reuse: no orphan accumulation; retry must tolerate existing identical pages and reject differing ones.
- New per attempt: every attempt is auditable; orphans accumulate (lifecycle policy needed).

Also: is check-then-write acceptable for backends without atomic create-if-absent, given `max_active_runs=1`?

## Consequences
- Good: crash-safe; auditable; rebuildable.
- Bad: raw grows with every rerun/backfill; needs a retention policy (later extension).
