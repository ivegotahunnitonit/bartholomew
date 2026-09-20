from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class BillableLedger:
    """Minimal SQLite-backed ledger for approved guard actions."""

    def __init__(self, ledger_path: Optional[str] = None):
        self.ledger_path = Path(ledger_path) if ledger_path else Path("btp_guard_ledger.db")
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.ledger_path))
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger_events (
                id TEXT PRIMARY KEY,
                event_name TEXT NOT NULL,
                tenant_id TEXT,
                agent_id TEXT,
                action_type TEXT,
                amount_usd REAL NOT NULL,
                currency TEXT NOT NULL,
                policy_version TEXT,
                receipt_sha256 TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def record_allowed_action(self, action: Dict[str, Any], result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if result.get("verdict") != "ALLOW":
            return None

        payload = action.get("payload", {})
        amount_usd = payload.get("amount_usd")
        if amount_usd is None:
            amount_usd = 0.01

        event = {
            "id": f"evt_{result.get('receipt_sha256', 'unknown')[:16]}",
            "event_name": "btp.guard.action.allowed",
            "tenant_id": action.get("tenant_id", "unknown-tenant"),
            "agent_id": action.get("agent_id", "unknown-agent"),
            "action_type": action.get("action_type", "unknown"),
            "amount_usd": float(amount_usd),
            "currency": "USD",
            "policy_version": result.get("policy_version", "unknown"),
            "receipt_sha256": result.get("receipt_sha256"),
            "metadata_json": json.dumps({"action": action, "result": result}, sort_keys=True),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.conn.execute(
            """
            INSERT INTO ledger_events (
                id, event_name, tenant_id, agent_id, action_type, amount_usd, currency,
                policy_version, receipt_sha256, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["id"],
                event["event_name"],
                event["tenant_id"],
                event["agent_id"],
                event["action_type"],
                event["amount_usd"],
                event["currency"],
                event["policy_version"],
                event["receipt_sha256"],
                event["metadata_json"],
                event["created_at"],
            ),
        )
        self.conn.commit()
        return event

    def list_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM ledger_events ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self.conn.close()
