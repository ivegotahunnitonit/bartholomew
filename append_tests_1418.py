#!/usr/bin/env python3
"""Appends unit tests for Issue #1418 fixes to tests/test_unit.py"""

test_code = '''

# =====================================================================
# Tests for Issue #1418: Conflict resolution reconnected
# =====================================================================


class TestValidationPolicyExists:
    """ValidationPolicy must be importable from memanto.app.core."""

    def test_validation_policy_importable(self):
        from memanto.app.core import ValidationPolicy
        assert ValidationPolicy is not None

    def test_validate_memory_no_conflict(self):
        """No conflict when repetition_count == 0."""
        from memanto.app.core import MemoryRecord, ValidationPolicy

        policy = ValidationPolicy()
        mem = MemoryRecord(
            type="fact",
            title="Favorite color",
            content="The user's favorite color is blue.",
            agent_id="agent-1",
            actor_id="user-1",
            source="user",
        )
        result = policy.validate_memory(mem, {"repetition_count": 0})
        assert result["action"] == "store"

    def test_validate_memory_conflict_marks_provisional(self):
        """High repetition_count must yield store_provisional action."""
        from memanto.app.core import MemoryRecord, ValidationPolicy

        policy = ValidationPolicy()
        mem = MemoryRecord(
            type="fact",
            title="Favorite color",
            content="The user's favorite color is red.",
            agent_id="agent-1",
            actor_id="user-1",
            source="user",
        )
        result = policy.validate_memory(mem, {"repetition_count": 2})
        assert result["action"] == "store_provisional"
        assert "memory" in result
        assert result["memory"].status == "provisional"

    def test_validate_memory_conflict_flag(self):
        """conflict_detected=True triggers provisional even without repetition_count."""
        from memanto.app.core import MemoryRecord, ValidationPolicy

        policy = ValidationPolicy()
        mem = MemoryRecord(
            type="preference",
            title="Deadline",
            content="Deadline is April 22.",
            agent_id="agent-1",
            actor_id="user-1",
            source="user",
        )
        result = policy.validate_memory(mem, {"conflict_detected": True})
        assert result["action"] == "store_provisional"
        assert result["memory"].status == "provisional"

    def test_make_provisional_returns_copy(self):
        """make_provisional should return a new object, not mutate in-place."""
        from memanto.app.core import MemoryRecord, ValidationPolicy

        policy = ValidationPolicy()
        mem = MemoryRecord(
            type="fact",
            title="Color",
            content="Blue.",
            agent_id="agent-1",
            actor_id="user-1",
            source="user",
            status="active",
        )
        provisional = policy.make_provisional(mem)
        assert provisional.status == "provisional"
        assert mem.status == "active"  # original unchanged


class TestMemoryWriteServiceValidationReconnected:
    """store_memory() must call validation_service and honour provisional flag."""

    def test_store_memory_calls_validation_service(self):
        """validation_service.validate_memory is invoked on every store_memory call."""
        from unittest.mock import MagicMock, patch, call
        from memanto.app.core import MemoryRecord
        from memanto.app.services.memory_write_service import MemoryWriteService

        mock_client = MagicMock()
        mock_client.documents.upload.return_value = {"status": "queued"}

        svc = MemoryWriteService(mock_client)

        # Inject a mock validation_service
        mock_vs = MagicMock()
        mock_vs.validate_memory.return_value = {
            "action": "store",
            "reason": "No conflict.",
        }
        svc._validation_service = mock_vs

        mem = MemoryRecord(
            type="fact",
            title="T",
            content="Content.",
            agent_id="agent-1",
            actor_id="user-1",
            source="user",
        )
        svc.store_memory(mem)

        mock_vs.validate_memory.assert_called_once()

    def test_store_memory_respects_provisional_status(self):
        """When validation returns a provisional memory, it must be stored as provisional."""
        from unittest.mock import MagicMock
        from memanto.app.core import MemoryRecord, ValidationPolicy
        from memanto.app.services.memory_write_service import MemoryWriteService

        uploaded = {}

        def capture_upload(namespace_name, documents):
            uploaded["doc"] = documents[0]
            return {"status": "queued"}

        mock_client = MagicMock()
        mock_client.documents.upload.side_effect = capture_upload

        svc = MemoryWriteService(mock_client)

        # Inject validation service that marks memories as provisional
        policy = ValidationPolicy()
        mock_vs = MagicMock()
        mem_input = MemoryRecord(
            type="fact",
            title="Color",
            content="Red.",
            agent_id="agent-1",
            actor_id="user-1",
            source="user",
        )
        provisional = policy.make_provisional(mem_input)
        mock_vs.validate_memory.return_value = {
            "action": "store_provisional",
            "reason": "Conflict detected.",
            "memory": provisional,
        }
        svc._validation_service = mock_vs

        svc.store_memory(mem_input)

        assert uploaded["doc"]["status"] == "provisional"
'''

with open("tests/test_unit.py", "a") as f:
    f.write(test_code)
print("Appended Issue #1418 tests to tests/test_unit.py")
