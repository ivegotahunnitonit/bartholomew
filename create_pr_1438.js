import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : 'YOUR_GITHUB_TOKEN_HERE';

const prBody = `## Summary

Fixes three security/correctness issues reported in [Issue #1438](https://github.com/moorcheh-ai/memanto/issues/1438) ([Bug Challenge #770](https://github.com/zhangjiayang6835-cyber/ai-research/issues/770)).

---

## 🔴 Fix 1: Rate Limiter Fail-Open → Fail-Closed (\`rate_limiting.py\`)

**Root cause:** \`check_rate_limit()\` returned \`(True, None)\` for any operation not in \`self.limits\`. The helper \`enforce_namespace_rate_limit(operation, agent_id)\` builds its key as \`f"namespace_{operation}"\` — so calling it with \`operation="list"\` produced \`"namespace_list"\` which is **not** in the limits dict, silently bypassing rate limiting.

**Fix:** Raise \`ValueError\` when an unknown operation is presented. Callers must register the operation in \`RateLimiter.limits\` before use.

\`\`\`python
# Before (fail-open):
if operation not in self.limits:
    return True, None

# After (fail-closed):
if operation not in self.limits:
    raise ValueError(
        f"Unknown rate-limit operation '{operation}'. "
        "Register it in RateLimiter.limits before use."
    )
\`\`\`

---

## 🟡 Fix 2: Inconsistent \`is_valid_memory_id\` (\`ids.py\`)

**Root cause:** \`ids.py\` validated IDs using \`"_" in memory_id\`, requiring an underscore. \`safe_deletion.py\` used \`^[a-zA-Z0-9_-]+$\` — accepting hyphens. An ID like \`abc-123\` therefore passed deletion validation but failed general validation.

**Fix:** Aligned \`ids.is_valid_memory_id\` to use the same \`^[a-zA-Z0-9_-]+$\` regex pattern and length check as \`SafeDeletion._is_valid_memory_id\`.

---

## 🟡 Fix 3: \`SourceType = str\` — No Validation (\`constants.py\`)

**Root cause:** \`SourceType\` was a bare \`str\` alias with no constraint, allowing arbitrary values in the \`source\` field of memory records.

**Fix:** Added \`KNOWN_SOURCE_TYPES: frozenset[str]\` as the authoritative set of built-in values (\`user\`, \`agent\`, \`tool\`, \`system\`). The type annotation remains \`str\` for backwards-compatibility with custom agent names, but routes/services can now validate against this set.

---

## Tests

Added **13 unit tests** in \`tests/test_unit.py\` covering all three fixes. Full suite: **72 tests, all pass**.

| Test class | Tests |
|---|---|
| \`TestRateLimiterFailClosed\` | 5 tests — fail-closed for unknown ops, known ops still work |
| \`TestIsValidMemoryIdAligned\` | 5 tests — underscore + hyphen IDs, edge cases |
| \`TestKnownSourceTypes\` | 3 tests — frozenset exported, canonical values present |`;

const payload = {
  title: 'fix: rate-limiter fail-open + ID validation inconsistency + SourceType (issue #1438)',
  head: 'ivegotahunnitonit:fix-rate-limiter-validation-1438',
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
  fs.writeFileSync('create_pr_1438.js.result.txt', j.html_url);
} else {
  console.error('Error:', JSON.stringify(j, null, 2));
}
