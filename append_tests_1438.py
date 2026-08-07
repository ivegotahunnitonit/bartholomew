#!/usr/bin/env python3
"""Appends unit tests for Issue #1438 fixes to tests/test_unit.py"""
import os

test_code = '''

# =====================================================================
# Tests for Issue #1438: Rate-limiter fail-open + validation fixes
# =====================================================================

import pytest
import re


class TestRateLimiterFailClosed:
    """Rate limiter must raise ValueError for unknown operations (fail-closed)."""

    def test_check_rate_limit_raises_for_unknown_operation(self):
        from memanto.app.utils.rate_limiting import RateLimiter

        limiter = RateLimiter()
        with pytest.raises(ValueError, match="Unknown rate-limit operation"):
            limiter.check_rate_limit("nonexistent_op", "agent-1")

    def test_enforce_rate_limit_raises_for_unknown_operation(self):
        from memanto.app.utils.rate_limiting import RateLimiter

        limiter = RateLimiter()
        with pytest.raises(ValueError, match="Unknown rate-limit operation"):
            limiter.enforce_rate_limit("nonexistent_op", "agent-1")

    def test_enforce_namespace_rate_limit_raises_for_list(self):
        """enforce_namespace_rate_limit('list', ...) must not silently pass."""
        from memanto.app.utils.rate_limiting import enforce_namespace_rate_limit

        # 'namespace_list' is not a registered operation → must raise ValueError
        with pytest.raises(ValueError, match="Unknown rate-limit operation"):
            enforce_namespace_rate_limit("list", "agent-1")

    def test_known_operations_still_work(self):
        """Registered operations must still return (allowed, None) when not exhausted."""
        from memanto.app.utils.rate_limiting import RateLimiter

        limiter = RateLimiter()
        allowed, retry_after = limiter.check_rate_limit("memory_write", "agent-ok")
        assert allowed is True
        assert retry_after is None

    def test_namespace_create_allowed(self):
        from memanto.app.utils.rate_limiting import RateLimiter

        limiter = RateLimiter()
        # 'namespace_create' is a registered key
        allowed, _ = limiter.check_rate_limit("namespace_create", "agent-x")
        assert allowed is True


class TestIsValidMemoryIdAligned:
    """ids.is_valid_memory_id must accept hyphenated IDs (aligned with safe_deletion)."""

    def test_accepts_underscore_id(self):
        from memanto.app.utils.ids import is_valid_memory_id

        assert is_valid_memory_id("mem_abc123") is True

    def test_accepts_hyphenated_id(self):
        """IDs like abc-123 must now pass (safe_deletion already accepts them)."""
        from memanto.app.utils.ids import is_valid_memory_id

        assert is_valid_memory_id("abc-123") is True

    def test_rejects_short_id(self):
        from memanto.app.utils.ids import is_valid_memory_id

        assert is_valid_memory_id("ab") is False
        assert is_valid_memory_id("") is False

    def test_rejects_special_chars(self):
        from memanto.app.utils.ids import is_valid_memory_id

        assert is_valid_memory_id("mem id!") is False
        assert is_valid_memory_id("mem/id") is False

    def test_length_boundary(self):
        """Minimum valid length is 4 characters."""
        from memanto.app.utils.ids import is_valid_memory_id

        assert is_valid_memory_id("abcd") is True   # exactly 4 → valid
        assert is_valid_memory_id("abc") is False   # 3 chars → invalid


class TestKnownSourceTypes:
    """KNOWN_SOURCE_TYPES must export the canonical built-in source values."""

    def test_known_source_types_exported(self):
        from memanto.app.constants import KNOWN_SOURCE_TYPES

        assert isinstance(KNOWN_SOURCE_TYPES, frozenset)

    def test_canonical_values_present(self):
        from memanto.app.constants import KNOWN_SOURCE_TYPES

        assert "user" in KNOWN_SOURCE_TYPES
        assert "agent" in KNOWN_SOURCE_TYPES
        assert "tool" in KNOWN_SOURCE_TYPES
        assert "system" in KNOWN_SOURCE_TYPES

    def test_custom_agent_name_not_in_known_set(self):
        """Custom agent names are intentionally absent from the known set."""
        from memanto.app.constants import KNOWN_SOURCE_TYPES

        assert "my_custom_agent" not in KNOWN_SOURCE_TYPES
'''

target = "tests/test_unit.py"
with open(target, "a") as f:
    f.write(test_code)
print(f"Appended tests to {target}")
