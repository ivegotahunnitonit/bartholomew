# Root Cause Diagnosis - Pytest Parallel Worker Mock Contamination

## Root Cause

`auth_service` fixture was defined with `scope='session'`, causing shared mock state to leak across parallel worker processes under `pytest-xdist`.

## Solution

Refactored fixture scope to `function`, ensuring strict per-test instance isolation.
