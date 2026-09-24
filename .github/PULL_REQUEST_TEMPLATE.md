## Summary

<!-- 1-3 sentence description of what this PR does -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would break existing functionality)
- [ ] Performance improvement (measurable latency reduction)
- [ ] Documentation update
- [ ] CI / tooling update

## Motivation

<!-- Why is this change needed? Link to relevant issue if applicable. -->
Closes #

## Changes Made

<!-- List of files changed and why -->
-
-

## Test Coverage

- [ ] Added new tests for changed behaviour
- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] Adversarial fuzzer passes (`pytest tests/test_adversarial_jailbreak_fuzzer.py -v`)
- [ ] Benchmark regression-free (`btp-guard bench` p50 ≤ 35µs)

## Security Checklist

- [ ] No new `eval` / `exec` / `os.system` calls added
- [ ] No secrets / credentials committed
- [ ] `SECURITY.md` updated if attack surface changed
- [ ] New forbidden patterns added to `polyglot_ast_validator.py` if applicable

## Benchmarks (if performance-related)

| Metric | Before | After |
|--------|--------|-------|
| p50 latency | µs | µs |
| p99 latency | µs | µs |
| False negative rate | 0% | 0% |

## Screenshots / Recordings (if UI-related)

<!-- Drag and drop images/videos here -->
