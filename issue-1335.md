## Bug Description (on-prem)

When calling `update_memory()` with an existing `memory_id` (from API `POST /items/batch`), the entire record is overwritten including `original_id`. This breaks the expected logic — if a record was originally created with one ID and later updated, the original ID should be preserved.

## Expected Behavior

- `update_memory()` should only update mutable fields: `data`, `tags`, `description`, `score`, `updated_at`
- `original_id` and `created_at` should remain unchanged
- `data_store.json` should update the specific record by `memory_id` without overwriting the entire structure

## Actual Behavior

The record in `data_store.json` is completely overwritten, including the original ID. On subsequent updates, `original_id` becomes equal to the latest `memory_id`.

## Steps to Reproduce

1. Create a record via API `POST /items/batch` with `memory_id=uuid1`
2. Backup `data_store.json`
3. Update the record via `POST /items/batch` with new `memory_id=uuid2`
4. Compare `data_store.json` — `original_id` has changed to `uuid2`

## Impact

- Loss of metadata on updates
- Incorrect conflict scanner logic
- Difficulties with audit trail (change history)

## Proposed Fix

In `memory_write_service.py`, the `update_memory()` method should:
1. Load the existing record from `data_store.json`
2. Update only the mutable fields
3. Preserve `original_id` and `created_at` unchanged

## Additional Notes

In the current implementation (SDK 0.2.4), there is already a partial fix — the delete-and-recreate block was removed from `update_memory()`, but the `original_id` overwrite problem remains.

## Configuration (on-prem)
- Memanto SDK: 0.2.4
- Python: 3.12
- OS: Ubuntu 24.04
- Deployment: systemd + direct binary (`memanto serve --port 7007`)
- Conflict Scanner: Moorcheh (Docker, port 8080)

---
Russian issue: https://github.com/moorcheh-ai/memanto/issues/1334