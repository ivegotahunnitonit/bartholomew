import fs from 'fs';

const TOKEN = 'YOUR_GITHUB_TOKEN_HERE';

const prBody = `## Summary

Fixes [Issue #1418](https://github.com/moorcheh-ai/memanto/issues/1418) — the "reconciles contradictions" feature documented in [arXiv:2604.22085 Sec. E](https://arxiv.org/abs/2604.22085) was entirely dead code on \`main\` / v0.2.4.

---

## Root Causes & Fixes

### 🔴 1. \`ValidationPolicy\` deleted from \`core.py\`

\`memanto/app/legacy/memory_validation_service.py\` still imports \`ValidationPolicy\` from \`memanto.app.core\`, but the class no longer existed — causing an \`ImportError\` and making the entire legacy validation module unimportable.

**Fix:** Restored a minimal \`ValidationPolicy\` class in \`core.py\`:
- \`validate_memory(memory, context)\` — inspects \`context["repetition_count"]\` and \`context["conflict_detected"]\`; returns \`"store"\` or \`"store_provisional"\` with the updated memory.
- \`make_provisional(memory)\` — returns an immutable copy with \`status = "provisional"\`.

### 🔴 2. \`validate_memory()\` call commented out in both write paths

Both \`store_memory()\` and \`batch_store_memories()\` in \`memory_write_service.py\` had the validation call commented out with a \`# skip validation for speed\` note and a hardcoded \`"MVP direct store"\` bypass. Two contradicting memories (e.g. \`"deadline is April 15"\` then \`"deadline is April 22"\`) would both be stored as \`status="active"\` with unchanged confidence.

**Fix:** Re-enabled the validation call in both write paths. Added a \`validation_service\` lazy property to \`MemoryWriteService\` that instantiates \`MemoryValidationService\` on first access.

### 🟡 3. \`_check_repetition\` disabled in \`MemoryValidationService\`

The repetition check (which queries Moorcheh for high-similarity existing memories before storing) was also commented out, preventing the similarity-based conflict detection from ever running.

**Fix:** Re-enabled \`_check_repetition\` with a graceful \`try/except\` so on-prem deployments without embeddings degrade cleanly.

---

## Behaviour After This Fix

Storing two contradicting memories of the same type now correctly detects the conflict:

\`\`\`python
r1 = svc.store_memory(mem_v1)  # action="store", status="active"
r2 = svc.store_memory(mem_v2)  # action="store_provisional", status="provisional"
assert r2["memory_status"] == "provisional"  # ✅ conflict detected
\`\`\`

---

## Tests

Added **7 unit tests** in \`tests/test_unit.py\`:

| Class | Coverage |
|---|---|
| \`TestValidationPolicyExists\` | 5 tests — importable, no-conflict stores, conflict → provisional, conflict flag, make_provisional immutability |
| \`TestMemoryWriteServiceValidationReconnected\` | 2 tests — validation_service called on store, provisional status preserved in uploaded doc |

**66 tests total, all pass.**`;

const payload = {
  title: 'fix: reconnect conflict-resolution / validation path (issue #1418)',
  head: 'ivegotahunnitonit:fix-conflict-resolution-1418',
  base: 'main',
  body: prBody
};

const res = await fetch('https://api.github.com/repos/moorcheh-ai/memanto/pulls', {
  method: 'POST',
  headers: {
    'User-Agent': 'node',
    'Authorization': `token ${TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
});

const j = await res.json();
if (j.html_url) {
  console.log(`PR created: ${j.html_url}`);
} else {
  console.error('Error:', JSON.stringify(j, null, 2));
}
