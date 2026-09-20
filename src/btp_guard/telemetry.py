from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class TelemetryEmitter:
    """Very small telemetry emitter for authorization events."""

    def __init__(self, output_path: Optional[str] = None):
        self.output_path = Path(output_path) if output_path else None

    def emit(self, event: Dict[str, Any]) -> Dict[str, Any]:
        enriched = {
            **event,
            "timestamp": event.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        }

        if self.output_path is not None:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with self.output_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(enriched, sort_keys=True) + "\n")

        return enriched
