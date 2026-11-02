# Test fixtures

| File | Origin | Use |
|---|---|---|
| `sample_311_page1.json` | **REAL sample data**: 12 records fetched unmodified from `https://data.cityofchicago.org/resource/v6vf-nfxy.json` on 2026-11-02 (`last_modified_date > 2026-11-02T06:00:00`, ordered by `last_modified_date, sr_number`). Public City of Chicago open data. Do not edit by hand; it is also your byte-faithful "raw page" example. | happy-path parsing, schema, raw-file layout |
| `messy_rows.json` | **SYNTHETIC**, hand-written for this project. Not real service requests. | quality/quarantine/dedupe edge cases |

`messy_rows.json` contains (by `sr_number`):

| sr_number | what's wrong / why it exists |
|---|---|
| `SR-TEST-001` | clean row (control) |
| `SR-TEST-002` | same key as 003 but older `last_modified_date`: dedupe must keep 003 |
| `SR-TEST-002` (second copy, newer) | winner of the dedupe above |
| `SR-TEST-004` | `created_date` after `last_modified_date` |
| `SR-TEST-005` | `closed_date` before `created_date` |
| `SR-TEST-006` | unparseable `created_date` -> quarantine |
| `SR-TEST-007` | latitude/longitude outside Chicago box |
| `SR-TEST-008` | `ward` = "0" and `community_area` = "99" (out of range) |
| (no sr_number) | missing key -> quarantine |
| `SR-TEST-010` | timestamp in the far future |
| `SR-TEST-011` | `zip_code` with leading zero ("06010"), `police_district` "06": must stay strings |
| `SR-TEST-012` | new unexpected field `brand_new_field` (additive schema drift) |

If you add a case, add a row to this table.
