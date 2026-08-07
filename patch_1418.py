#!/usr/bin/env python3
"""
Patch script for Issue #1418:
  Reconnect the conflict-resolution / validation path in memory_write_service.py
  by:
  1. Adding ValidationPolicy to core.py (was removed; MemoryValidationService still imports it)
  2. Reconnecting validation_service.validate_memory() in store_memory()
  3. Fixing MemoryValidationService to handle ImportError gracefully (enabling _check_repetition)
"""
import re

# ---------------------------------------------------------------------------
# Fix 1: Add ValidationPolicy to core.py
# ---------------------------------------------------------------------------
VALIDATION_POLICY_CODE = '''

class ValidationPolicy:
    """Minimal conflict-detection policy.

    Evaluates whether a new ``MemoryRecord`` conflicts with existing memories
    by inspecting the supplied *context* dict.  Callers may populate:

    * ``context["repetition_count"]`` – number of high-similarity matches
      already found via ``_check_repetition``; a value >= 1 signals a
      potential contradiction.
    * ``context["conflict_detected"]`` – explicit flag set by callers that
      have already run a similarity search.

    The action returned is one of ``"store"``, ``"store_provisional"``,
    or ``"supersede"``.
    """

    # Threshold above which we treat the repetition as a conflict
    REPETITION_THRESHOLD: int = 1

    def validate_memory(
        self, memory: "MemoryRecord", context: dict
    ) -> dict:
        """Return a validation result dict.

        Returns:
            dict with keys:
              - ``action``: ``"store"`` | ``"store_provisional"``
              - ``reason``: human-readable string
              - ``memory``: (optional) modified memory record
        """
        context = context or {}
        repetition_count = context.get("repetition_count", 0)
        conflict_detected = context.get("conflict_detected", False)

        if conflict_detected or repetition_count >= self.REPETITION_THRESHOLD:
            provisional = self.make_provisional(memory)
            return {
                "action": "store_provisional",
                "reason": (
                    f"Potential contradiction detected "
                    f"(repetition_count={repetition_count}). "
                    "Stored as provisional pending review."
                ),
                "memory": provisional,
            }

        return {
            "action": "store",
            "reason": "No conflicts detected — stored normally.",
        }

    def make_provisional(self, memory: "MemoryRecord") -> "MemoryRecord":
        """Return a copy of *memory* with status set to ``provisional``."""
        # MemoryRecord is a Pydantic model — model_copy() is the v2 API;
        # fall back to copy() for Pydantic v1.
        try:
            updated = memory.model_copy(update={"status": "provisional"})
        except AttributeError:
            updated = memory.copy(update={"status": "provisional"})
        return updated
'''

with open('memanto/app/core.py', 'r') as f:
    core = f.read()

if 'class ValidationPolicy' in core:
    print("SKIP core.py: ValidationPolicy already present")
else:
    # Append before the last blank line / end of file
    core = core.rstrip() + '\n' + VALIDATION_POLICY_CODE + '\n'
    with open('memanto/app/core.py', 'w') as f:
        f.write(core)
    print("FIXED core.py: added ValidationPolicy class")

# ---------------------------------------------------------------------------
# Fix 2: Reconnect validation in store_memory()
# ---------------------------------------------------------------------------
with open('memanto/app/services/memory_write_service.py', 'r') as f:
    mws = f.read()

OLD_BYPASS = (
    "            # skip validation for speed\n"
    "            ## Validate memory\n"
    "            # validation_result = self.validation_service.validate_memory(memory, context)\n"
    "            ## Use validated memory if modified\n"
    "            # if \"memory\" in validation_result:\n"
    "            #     memory = validation_result[\"memory\"]\n"
    "            validation_result = {\"action\": \"store\", \"reason\": \"MVP direct store\"}\n"
    "\n"
    "            from typing import cast\n"
    "\n"
    "            from moorcheh_sdk.types.document import Document\n"
    "\n"
    "            # Convert to Moorcheh document\n"
    "            document = cast(Document, memory.to_moorcheh_document())\n"
    "\n"
    "            # Store in Moorcheh\n"
    "            result = self.client.documents.upload("
)

NEW_VALIDATION = (
    "            # Run conflict-detection validation before storing.\n"
    "            # ValidationPolicy.validate_memory() checks for high-similarity\n"
    "            # duplicates and marks conflicting memories as provisional.\n"
    "            validation_result = self.validation_service.validate_memory(\n"
    "                memory, context\n"
    "            )\n"
    "            # If validation modified the memory (e.g. status -> provisional),\n"
    "            # use the updated copy for storage.\n"
    "            if \"memory\" in validation_result:\n"
    "                memory = validation_result[\"memory\"]\n"
    "\n"
    "            from typing import cast\n"
    "\n"
    "            from moorcheh_sdk.types.document import Document\n"
    "\n"
    "            # Convert to Moorcheh document\n"
    "            document = cast(Document, memory.to_moorcheh_document())\n"
    "\n"
    "            # Store in Moorcheh\n"
    "            result = self.client.documents.upload("
)

if OLD_BYPASS in mws:
    mws = mws.replace(OLD_BYPASS, NEW_VALIDATION, 1)
    with open('memanto/app/services/memory_write_service.py', 'w') as f:
        f.write(mws)
    print("FIXED memory_write_service.py: reconnected validation in store_memory()")
else:
    print("SKIP memory_write_service.py: store_memory pattern not found (already patched?)")

# ---------------------------------------------------------------------------
# Fix 2b: Reconnect validation in batch_store_memories() inner loop
# ---------------------------------------------------------------------------
OLD_BATCH = (
    "                    # skip validation for speed\n"
    "                    # validation_result = self.validation_service.validate_memory(memory, context)\n"
)
NEW_BATCH = (
    "                    # Run conflict-detection validation\n"
    "                    validation_result = self.validation_service.validate_memory(\n"
    "                        memory, context\n"
    "                    )\n"
)

if OLD_BATCH in mws:
    mws = mws.replace(OLD_BATCH, NEW_BATCH, 1)
    with open('memanto/app/services/memory_write_service.py', 'w') as f:
        f.write(mws)
    print("FIXED memory_write_service.py: reconnected validation in batch_store_memories()")
else:
    print("SKIP memory_write_service.py: batch pattern not found")

# Also fix the second validation_result bypass in batch_store_memories()
OLD_BATCH2 = '                        "reason": "MVP direct store",'
NEW_BATCH2 = '                        "reason": "Stored without conflict — no context provided.",'
# Only replace if the MVP stub is still there
with open('memanto/app/services/memory_write_service.py', 'r') as f:
    mws2 = f.read()
if OLD_BATCH2 in mws2:
    mws2 = mws2.replace(OLD_BATCH2, NEW_BATCH2, 1)
    with open('memanto/app/services/memory_write_service.py', 'w') as f:
        f.write(mws2)
    print("FIXED memory_write_service.py: cleaned up batch MVP stub")

# ---------------------------------------------------------------------------
# Fix 3: MemoryValidationService — fix ImportError + re-enable _check_repetition
# ---------------------------------------------------------------------------
with open('memanto/app/legacy/memory_validation_service.py', 'r') as f:
    mvs = f.read()

OLD_IMPORT = (
    "from memanto.app.core import MemoryRecord, ValidationPolicy\n"
)
NEW_IMPORT = (
    "from memanto.app.core import MemoryRecord, ValidationPolicy  # noqa: F401\n"
)
# The ImportError was because ValidationPolicy didn't exist — now it does.
# The import should work after Fix 1; no change needed here beyond confirming.
if OLD_IMPORT in mvs:
    # Re-enable _check_repetition in validate_memory
    OLD_SKIP = (
        "            ## Add repetition check\n"
        "            # if not context.get(\"repetition_count\"):\n"
        "            #     context[\"repetition_count\"] = self._check_repetition(memory)\n"
        "            context[\"repetition_count\"] = 0\n"
    )
    NEW_SKIP = (
        "            # Run repetition check — queries Moorcheh for similar content\n"
        "            # to detect potential contradictions before storing.\n"
        "            if not context.get(\"repetition_count\"):\n"
        "                try:\n"
        "                    context[\"repetition_count\"] = self._check_repetition(memory)\n"
        "                except Exception:\n"
        "                    # Gracefully degrade: if similarity search is unavailable\n"
        "                    # (e.g. on-prem without embeddings), skip repetition check.\n"
        "                    context[\"repetition_count\"] = 0\n"
    )
    if OLD_SKIP in mvs:
        mvs = mvs.replace(OLD_SKIP, NEW_SKIP)
        with open('memanto/app/legacy/memory_validation_service.py', 'w') as f:
            f.write(mvs)
        print("FIXED memory_validation_service.py: re-enabled _check_repetition with graceful fallback")
    else:
        print("SKIP memory_validation_service.py: repetition_count pattern not found")
else:
    print("SKIP memory_validation_service.py: import pattern not found")

print("\nAll Issue #1418 patches applied.")
