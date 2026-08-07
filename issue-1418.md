# Issue #1418: Conflict resolution doesn't run — the "reconciles contradictions" feature is dead code

### Conflict resolution doesn't run — the "reconciles contradictions" feature is dead code
I went looking for how Memanto handles contradicting memories, since that's called out pretty heavily as a differentiator (both on memanto.ai and in the whitepaper, arXiv:2604.22085 Sec. E — the pitch is that when a new memory contradicts an old one, Memanto flags it and reconciles instead of just keeping both). Turns out it doesn't do that at all right now, on main / v0.2.4.

MemoryWriteService.store_memory() and batch_store_memories() never call any validation/conflict logic. It's just hardcoded:

```python

memanto/app/services/memory_write_service.py
skip validation for speed
Validate memory
validation_result = self.validation_service.validate_memory(memory, context)
Use validated memory if modified
if "memory" in validation_result:
memory = validation_result["memory"]
validation_result = {"action": "store", "reason": "MVP direct store"} ```

That comment made me assume there was a flag somewhere to turn it back on, but there isn't — the class it would call, ValidationPolicy, isn't defined anywhere in the repo anymore (grep -rn "class ValidationPolicy" comes up empty). The module that references it, memanto/app/legacy/memory_validation_service.py, throws an ImportError if you try to import it. So this isn't disabled, it's just gone — moved to legacy/ at some point and never reconnected. Same story for MemorySupersedeService in legacy/universal_services.py, which is presumably what would mark an old memory superseded — it's never called from the live write path either.

Practically: store "the deadline is April 15," then later "the deadline is April 22," and both sit there as active memories with unchanged confidence, forever. recall() has no way to know which one is current. This seems squarely in the "fails to resolve direct contradictions" / timeline-amnesia bucket from the bounty scope, and given it's a documented core feature that just silently doesn't run, I'd call it high severity rather than an edge case.

reproducing it
Doesn't need Docker or a Moorcheh key — the bug lives in plain Python logic, so the client is just mocked.

```python from unittest.mock import MagicMock from memanto.app.core import MemoryRecord from memanto.app.services.memory_write_service import MemoryWriteService

mock_client = MagicMock() mock_client.documents.upload.return_value = {"status": "success"} svc = MemoryWriteService(mock_client)

mem_v1 = MemoryRecord(type="preference", title="Favorite color", content="The user's favorite color is blue.", agent_id="agent-1", actor_id="user-1", source="user", confidence=0.9) mem_v2 = MemoryRecord(type="preference", title="Favorite color", content="The user's favorite color is red.", agent_id="agent-1", actor_id="user-1", source="user", confidence=0.9)

r1 = svc.store_memory(mem_v1) r2 = svc.store_memory(mem_v2)

both r1 and r2 come back memory_status == "active", confidence == 0.9, unchanged
from memanto.app.legacy.memory_validation_service import MemoryValidationService

ImportError: cannot import name 'ValidationPolicy' from 'memanto.app.core'
```

Full script + output attached.

a second thing I ran into while I was in there
Not directly related but found it tracing the same code path, so flagging it here rather than opening a separate issue: update_memory() (backs memanto edit) deletes the old document before it knows the new one uploaded successfully:

```python

Step 3: Delete old version
delete_result = self.client.documents.delete(...) ...

Step 4: Upload new version
upload_result = self.client.documents.upload(...) # if this throws, old one is already gone ```

If step 4 fails — timeout, 5xx, whatever — there's no rollback and no re-insert. The memory is just gone. Repro'd this with a mocked delete that succeeds and an upload that raises ConnectionError; update_memory re-raises but the delete already happened. Attached as a second script.

what I'd probably do about it
Not 100% sure this is the right shape without knowing more about the intended architecture, but roughly:

Bring back some version of ValidationPolicy (or replace it) and actually call it from the write path instead of leaving the call commented out. A reasonable starting point: run a similarity search scoped to the same memory_type before storing, and if something looks like a high-similarity conflict, mark the new one provisional or supersede the old one — there's already a _check_repetition stub in the legacy validation service that's most of the way there.
Hook MemorySupersedeService back up to that path instead of leaving it orphaned in legacy/.
For update_memory, flip the order — upload the new version first, only delete the old one once that's confirmed. If Moorcheh doesn't support that ordering for some reason (same ID collision, etc.) then at minimum a failed upload shouldn't leave you with nothing.
Would be good to have a regression test asserting a supersede/status change happens on conflicting stores, and that a failed update doesn't drop the original — both are easy to write against a mocked client, per the repros above.
Happy to take a stab at the actual PR if that's useful, just didn't want to guess at the intended design too much without a maintainer weighing in first.

Tested against main, installed via pip install -e ., Python 3.12 — this is all mocked-client behavior, doesn't touch the real backend either way.

[repro_conflict_resolution_bug.py](https://github.com/user-attachments/files/29840683/repro_conflict_resolution_bug.py)

[repro_update_data_loss.py](https://github.com/user-attachments/files/29840684/repro_update_data_loss.py)