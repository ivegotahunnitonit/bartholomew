"""
BTP Milestone 5.1: Real-Time Incident Webhooks, SecOps Alerts & SIEM Integration
==============================================================================
Provides high-performance, asynchronous, multi-tenant webhook dispatching for:
- Slack (Block Kit JSON)
- Discord (Rich Embeds)
- PagerDuty (Events API v2 format)
- Generic Enterprise SIEM / Datadog / Splunk (JSON with HMAC-SHA256 signature)
"""

from __future__ import annotations

import os
import json
import time
import hmac
import hashlib
import queue
import threading
import urllib.request
import urllib.error
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class WebhookPlatform(str, Enum):
    SLACK = "slack"
    DISCORD = "discord"
    PAGERDUTY = "pagerduty"
    GENERIC = "generic"


class IncidentEventType(str, Enum):
    AST_VETO = "threat.ast_veto"
    PROMPT_INJECTION = "threat.prompt_injection"
    ESCROW_SLASHED = "escrow.slashed"
    PASSPORT_CIRCUIT_BREAKER = "passport.circuit_breaker"
    SYSCALL_BLOCKED = "threat.syscall_blocked"


@dataclass
class IncidentEvent:
    event_id: str
    tenant_id: str
    org_id: str
    project_id: str
    environment: str
    event_type: IncidentEventType
    severity: AlertSeverity
    title: str
    description: str
    agent_id: str
    tool_name: Optional[str] = None
    target_payload: Optional[str] = None
    slashed_amount_usd: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["event_type"] = self.event_type.value
        d["severity"] = self.severity.value
        return d


@dataclass
class WebhookSubscription:
    subscription_id: str
    tenant_id: str
    platform: WebhookPlatform
    target_url: str
    secret: str
    min_severity: AlertSeverity = AlertSeverity.LOW
    enabled: bool = True
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "tenant_id": self.tenant_id,
            "platform": self.platform.value,
            "target_url": self.target_url,
            "secret": self.secret,
            "min_severity": self.min_severity.value,
            "enabled": self.enabled,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookSubscription":
        return cls(
            subscription_id=data["subscription_id"],
            tenant_id=data["tenant_id"],
            platform=WebhookPlatform(data["platform"]),
            target_url=data["target_url"],
            secret=data.get("secret", ""),
            min_severity=AlertSeverity(data.get("min_severity", "LOW")),
            enabled=data.get("enabled", True),
            created_at=data.get("created_at", time.time()),
        )


class WebhookFormatter:
    """Formats IncidentEvent into platform-specific wire payloads."""

    @staticmethod
    def format_slack(event: IncidentEvent) -> Dict[str, Any]:
        color = {
            AlertSeverity.LOW: "#2eb886",
            AlertSeverity.MEDIUM: "#daa038",
            AlertSeverity.HIGH: "#e01e5a",
            AlertSeverity.CRITICAL: "#7b0000",
        }.get(event.severity, "#e01e5a")

        fields = [
            {"type": "mrkdwn", "text": f"*Tenant:* `{event.tenant_id[:12]}` ({event.org_id}/{event.project_id})"},
            {"type": "mrkdwn", "text": f"*Environment:* `{event.environment}`"},
            {"type": "mrkdwn", "text": f"*Agent ID:* `{event.agent_id}`"},
            {"type": "mrkdwn", "text": f"*Severity:* *{event.severity.value}*"},
        ]
        if event.tool_name:
            fields.append({"type": "mrkdwn", "text": f"*Target Tool:* `{event.tool_name}`"})
        if event.slashed_amount_usd is not None:
            fields.append({"type": "mrkdwn", "text": f"*Slashed Collateral:* `${event.slashed_amount_usd:.2f} USD`"})

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🛡️ BTP Guard: {event.title}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{event.description}*"}
            },
            {
                "type": "section",
                "fields": fields
            }
        ]

        if event.target_payload:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Intercepted Payload:*\n```{event.target_payload[:300]}```"}
            })

        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"Event ID: `{event.event_id}` | Time: <!date^{int(event.timestamp)}^{{date_num}} {{time_secs}}|{event.timestamp}> | Portal: <https://acn-26670.web.app|BTP Audit Portal>"}
            ]
        })

        return {
            "attachments": [
                {
                    "color": color,
                    "blocks": blocks
                }
            ]
        }

    @staticmethod
    def format_discord(event: IncidentEvent) -> Dict[str, Any]:
        color = {
            AlertSeverity.LOW: 3066993,
            AlertSeverity.MEDIUM: 14328888,
            AlertSeverity.HIGH: 14687834,
            AlertSeverity.CRITICAL: 8060928,
        }.get(event.severity, 14687834)

        fields = [
            {"name": "Tenant", "value": f"`{event.tenant_id[:12]}`", "inline": True},
            {"name": "Environment", "value": f"`{event.environment}`", "inline": True},
            {"name": "Severity", "value": f"**{event.severity.value}**", "inline": True},
            {"name": "Agent", "value": f"`{event.agent_id}`", "inline": True},
        ]
        if event.tool_name:
            fields.append({"name": "Target Tool", "value": f"`{event.tool_name}`", "inline": True})
        if event.slashed_amount_usd is not None:
            fields.append({"name": "Slashed Collateral", "value": f"`${event.slashed_amount_usd:.2f} USD`", "inline": True})
        if event.target_payload:
            fields.append({"name": "Quarantined Payload", "value": f"```{event.target_payload[:250]}```", "inline": False})

        embed = {
            "title": f"🛡️ BTP Security Alert: {event.title}",
            "description": event.description,
            "color": color,
            "fields": fields,
            "footer": {"text": f"BTP Guard v5.1 | Event ID: {event.event_id}"},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.timestamp)),
            "url": "https://acn-26670.web.app"
        }
        return {"embeds": [embed]}

    @staticmethod
    def format_pagerduty(event: IncidentEvent, routing_key: str = "") -> Dict[str, Any]:
        pd_severity = {
            AlertSeverity.LOW: "info",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.HIGH: "error",
            AlertSeverity.CRITICAL: "critical",
        }.get(event.severity, "error")

        return {
            "routing_key": routing_key,
            "event_action": "trigger",
            "dedup_key": f"btp-{event.tenant_id}-{event.agent_id}-{event.event_type.value}",
            "payload": {
                "summary": f"[BTP-{event.severity.value}] {event.title}: {event.description}",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.timestamp)),
                "severity": pd_severity,
                "source": f"btp-guard/{event.tenant_id}",
                "component": "ast_invariant_gate",
                "custom_details": event.to_dict()
            },
            "client": "Bartholomew Trust Protocol",
            "client_url": "https://acn-26670.web.app"
        }

    @staticmethod
    def format_generic(event: IncidentEvent) -> Dict[str, Any]:
        return {
            "version": "5.1.0",
            "protocol": "Bartholomew-Trust-Protocol",
            "event": event.to_dict()
        }


class WebhookSignatureEngine:
    """Generates and verifies cryptographic HMAC-SHA256 signatures for webhooks."""

    @staticmethod
    def sign_payload(payload_bytes: bytes, secret: str, timestamp: Optional[int] = None) -> str:
        ts = timestamp if timestamp is not None else int(time.time())
        to_sign = f"t={ts}.".encode("utf-8") + payload_bytes
        sig = hmac.new(secret.encode("utf-8"), to_sign, hashlib.sha256).hexdigest()
        return f"t={ts},v1={sig}"

    @staticmethod
    def verify_signature(
        payload_bytes: bytes,
        signature_header: str,
        secret: str,
        max_age_seconds: int = 300
    ) -> bool:
        if not signature_header or not secret:
            return False

        try:
            parts = dict(kv.split("=", 1) for kv in signature_header.split(","))
            ts_str = parts.get("t")
            sig = parts.get("v1")
            if not ts_str or not sig:
                return False

            timestamp = int(ts_str)
            now = int(time.time())
            if abs(now - timestamp) > max_age_seconds:
                return False

            expected_to_sign = f"t={timestamp}.".encode("utf-8") + payload_bytes
            expected_sig = hmac.new(secret.encode("utf-8"), expected_to_sign, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected_sig, sig)
        except Exception:
            return False


class WebhookDispatcher:
    """
    Thread-safe, asynchronous multi-tenant webhook dispatching engine.
    Persists subscriptions in `.btp_webhooks.json` and dispatches alerts asynchronously.
    """

    DEFAULT_STORE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", ".btp_webhooks.json"
    )

    def __init__(
        self,
        store_path: Optional[str] = None,
        sync_mode: bool = False,
        http_post_fn: Optional[Callable[[str, bytes, Dict[str, str]], Tuple[int, str]]] = None
    ):
        self.store_path = os.path.abspath(store_path or self.DEFAULT_STORE_PATH)
        self.sync_mode = sync_mode
        self._http_post_fn = http_post_fn
        self._lock = threading.Lock()
        self._subscriptions: Dict[str, WebhookSubscription] = {}
        self._queue: queue.Queue = queue.Queue()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._dispatched_history: List[Dict[str, Any]] = []

        self._load_subscriptions()

        if not self.sync_mode:
            self._start_worker()

    def _load_subscriptions(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("subscriptions", []):
                        sub = WebhookSubscription.from_dict(item)
                        self._subscriptions[sub.subscription_id] = sub
            except Exception:
                self._subscriptions = {}

    def _save_subscriptions(self):
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump({
                    "version": "5.1.0",
                    "subscriptions": [s.to_dict() for s in self._subscriptions.values()]
                }, f, indent=2)
        except Exception:
            pass

    def _start_worker(self):
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def _process_queue(self):
        while self._running:
            try:
                task = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            event, sub = task
            self._deliver_to_subscription(event, sub)
            self._queue.task_done()

    def register_subscription(
        self,
        tenant_id: str,
        platform: Union[WebhookPlatform, str],
        target_url: str,
        secret: Optional[str] = None,
        min_severity: Union[AlertSeverity, str] = AlertSeverity.LOW,
    ) -> WebhookSubscription:
        sub_id = f"sub_{hashlib.sha256(f'{tenant_id}:{target_url}:{time.time_ns()}'.encode()).hexdigest()[:16]}"
        resolved_secret = secret or f"btp_wh_{hashlib.sha256(os.urandom(32)).hexdigest()[:32]}"
        
        sub = WebhookSubscription(
            subscription_id=sub_id,
            tenant_id=tenant_id,
            platform=WebhookPlatform(platform) if isinstance(platform, str) else platform,
            target_url=target_url,
            secret=resolved_secret,
            min_severity=AlertSeverity(min_severity) if isinstance(min_severity, str) else min_severity,
            enabled=True
        )
        with self._lock:
            self._subscriptions[sub_id] = sub
            self._save_subscriptions()
        return sub

    def list_subscriptions(self, tenant_id: Optional[str] = None) -> List[WebhookSubscription]:
        with self._lock:
            if tenant_id:
                return [s for s in self._subscriptions.values() if s.tenant_id == tenant_id]
            return list(self._subscriptions.values())

    def delete_subscription(self, subscription_id: str) -> bool:
        with self._lock:
            if subscription_id in self._subscriptions:
                del self._subscriptions[subscription_id]
                self._save_subscriptions()
                return True
            return False

    def emit_incident(self, event: IncidentEvent) -> List[Dict[str, Any]]:
        """Emits an incident to all matching tenant subscriptions."""
        matching_subs: List[WebhookSubscription] = []
        with self._lock:
            for s in self._subscriptions.values():
                if not s.enabled:
                    continue
                # Tenant boundary check (or universal '*' tenant for global secops)
                if s.tenant_id != "*" and s.tenant_id != event.tenant_id:
                    continue
                # Severity threshold check
                severity_order = [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL]
                if severity_order.index(event.severity) < severity_order.index(s.min_severity):
                    continue
                matching_subs.append(s)

        results = []
        for sub in matching_subs:
            if self.sync_mode:
                res = self._deliver_to_subscription(event, sub)
                results.append(res)
            else:
                self._queue.put((event, sub))
                results.append({
                    "subscription_id": sub.subscription_id,
                    "status": "QUEUED",
                    "platform": sub.platform.value,
                    "target_url": sub.target_url
                })
        return results

    def _deliver_to_subscription(
        self,
        event: IncidentEvent,
        sub: WebhookSubscription
    ) -> Dict[str, Any]:
        """Formats, signs, and dispatches payload to target URL."""
        if sub.platform == WebhookPlatform.SLACK:
            payload = WebhookFormatter.format_slack(event)
        elif sub.platform == WebhookPlatform.DISCORD:
            payload = WebhookFormatter.format_discord(event)
        elif sub.platform == WebhookPlatform.PAGERDUTY:
            payload = WebhookFormatter.format_pagerduty(event)
        else:
            payload = WebhookFormatter.format_generic(event)

        payload_bytes = json.dumps(payload).encode("utf-8")
        sig_header = WebhookSignatureEngine.sign_payload(payload_bytes, sub.secret)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Bartholomew-Trust-Protocol-Guard/5.1.0",
            "X-BTP-Event-Type": event.event_type.value,
            "X-BTP-Event-ID": event.event_id,
            "X-BTP-Tenant-ID": event.tenant_id,
            "X-BTP-Signature": sig_header,
        }

        # Mock / Custom HTTP hook or live POST
        status_code = 200
        resp_text = "OK"
        start_t = time.perf_counter()

        if self._http_post_fn is not None:
            try:
                status_code, resp_text = self._http_post_fn(sub.target_url, payload_bytes, headers)
            except Exception as e:
                status_code = 500
                resp_text = str(e)
        else:
            # Default HTTP dispatch
            try:
                req = urllib.request.Request(
                    url=sub.target_url,
                    data=payload_bytes,
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    status_code = resp.getcode()
                    resp_text = resp.read().decode("utf-8", errors="ignore")[:200]
            except urllib.error.HTTPError as e:
                status_code = e.code
                resp_text = str(e)
            except Exception as e:
                status_code = 500
                resp_text = str(e)

        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)
        delivery_record = {
            "event_id": event.event_id,
            "subscription_id": sub.subscription_id,
            "platform": sub.platform.value,
            "target_url": sub.target_url,
            "status_code": status_code,
            "response": resp_text,
            "signature_header": sig_header,
            "latency_ms": elapsed_ms,
            "timestamp": time.time(),
            "success": 200 <= status_code < 300
        }

        with self._lock:
            self._dispatched_history.append(delivery_record)
            if len(self._dispatched_history) > 100:
                self._dispatched_history.pop(0)

        return delivery_record

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return list(reversed(self._dispatched_history[-limit:]))

    def close(self):
        self._running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
