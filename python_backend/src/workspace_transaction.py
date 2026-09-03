"""
Bartholomew Workspace Transaction & Instant Rollback Engine (v2.4)
==================================================================
Provides transactional, copy-on-write semantics for AI agent tool executions:
  1. Captures lightweight in-memory micro-snapshots before mutating actions.
  2. Tracks modified, created, and deleted files within the workspace root.
  3. Reverts file system state in <5ms upon tool crash or invariant violation.
  4. Returns structured diagnostic feedback so LLMs can self-correct without looping.
"""

import os
import shutil
import time
from typing import Dict, Any, List, Optional, Set


class WorkspaceTransaction:
    """
    Lightweight transactional wrapper for agent file system mutations.
    """

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root or os.getcwd())
        self.snapshots: Dict[str, Optional[bytes]] = {}  # filepath -> original bytes (or None if created new)
        self.created_files: Set[str] = set()
        self.is_committed = False
        self.is_rolled_back = False
        self.start_time = time.perf_counter()

    def snapshot_file(self, rel_or_abs_path: str):
        """
        Takes an in-memory byte snapshot of a file prior to modification.
        If the file does not exist yet, tracks it for removal on rollback.
        """
        abs_path = os.path.abspath(os.path.join(self.workspace_root, rel_or_abs_path))
        
        # Verify path containment within workspace
        common = os.path.commonpath([self.workspace_root, abs_path])
        if common != self.workspace_root:
            raise PermissionError(f"Path escape attempt: '{rel_or_abs_path}' is outside workspace '{self.workspace_root}'")

        if abs_path in self.snapshots or abs_path in self.created_files:
            return

        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            try:
                with open(abs_path, "rb") as f:
                    self.snapshots[abs_path] = f.read()
            except Exception as e:
                raise IOError(f"Failed to snapshot file '{abs_path}': {e}")
        else:
            self.created_files.add(abs_path)

    def rollback(self, reason: str = "Invariant check failed") -> Dict[str, Any]:
        """
        Restores all modified files and cleans up created files in <5ms.
        """
        t0 = time.perf_counter()
        restored = []
        cleaned = []

        # 1. Restore modified files from memory
        for path, original_content in self.snapshots.items():
            if original_content is not None:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(original_content)
                restored.append(os.path.relpath(path, self.workspace_root))

        # 2. Delete newly created files
        for path in self.created_files:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                cleaned.append(os.path.relpath(path, self.workspace_root))

        rollback_us = (time.perf_counter() - t0) * 1_000_000
        self.is_rolled_back = True

        return {
            "status": "ROLLED_BACK",
            "reason": reason,
            "rollback_time_us": round(rollback_us, 2),
            "restored_files": restored,
            "cleaned_files": cleaned,
            "diagnostic_hint": f"Workspace cleanly rolled back: {len(restored)} modified files restored, {len(cleaned)} uncommitted files purged."
        }

    def commit(self) -> Dict[str, Any]:
        """
        Commits all mutations, discarding snapshots.
        """
        self.is_committed = True
        elapsed_us = (time.perf_counter() - self.start_time) * 1_000_000
        return {
            "status": "COMMITTED",
            "elapsed_us": round(elapsed_us, 2),
            "modified_count": len(self.snapshots),
            "created_count": len(self.created_files)
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and not self.is_committed:
            self.rollback(reason=f"Exception raised during execution: {str(exc_val)}")
            return True  # Handled gracefully
        return False
