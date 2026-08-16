# Issue #1438: [BOUNTY] 🐜 Rate limiter fail-open + 2 validation inconsistencies

## Summary

During a security review of Memanto for the Bug & Exploit Challenge (#770), I identified three issues:

---

## 🔴 Finding 1: Rate Limiter Fail-Open Design (Severity: Medium)

**File:** `memanto/app/utils/rate_limiting.py:52-53`

```python
def check_rate_limit(self, operation: str, agent_id: str):
    if operation not in self.limits:
        return True, None  # FAIL-OPEN: unknown ops always pass
```

When `enforce_rate_limit` is called with an unrecognized operation, the request silently passes. `enforce_namespace_rate_limit(operation, agent_id)` builds keys as `f"namespace_{operation}"` — calling it with `operation="list"` creates `"namespace_list"` which is NOT in the limits dict, bypassing rate limiting entirely.

**Fix:** Fail-closed — raise ValueError or deny by default.

---

## 🟡 Finding 2: Inconsistent is_valid_memory_id

Two diverging implementations in `ids.py` and `safe_deletion.py`:
- `ids.py`: requires `_` in ID, length > 4
- `safe_deletion.py`: regex `^[a-zA-Z0-9_-]+$`, length >= 4

A memory ID like `abc-123` passes deletion validation but fails the general check.

---

## 🟡 Finding 3: SourceType = str (no validation)

`constants.py:21`: `SourceType = str` — unlike MemoryType/ProvenanceType which use `Literal`, SourceType accepts any arbitrary string. The source field in requests becomes searchable metadata with no validation.

---

## PoC

```python
from memanto.app.utils.rate_limiting import rate_limiter
allowed, _ = rate_limiter.check_rate_limit("nonexistent_op", "test")
assert allowed == True  # Bug confirmed
```

All reproducible against HEAD. Happy to submit PRs for any finding.
