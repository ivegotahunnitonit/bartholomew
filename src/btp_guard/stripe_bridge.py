from __future__ import annotations

import json
from typing import Any, Dict, Optional
from urllib import error, request
from urllib.parse import urlencode

urlopen = request.urlopen


class StripeMeterBridge:
    """Minimal Stripe metered-usage bridge for the allowed-action ledger event."""

    STRIPE_API_BASE = "https://api.stripe.com/v1"

    def __init__(
        self,
        api_key: str,
        meter_name: str = "autonomous_action_allowed",
        customer_map: Optional[Dict[str, str]] = None,
    ):
        self.api_key = api_key
        self.meter_name = meter_name
        self.customer_map = customer_map or {}

    def _resolve_customer_id(self, tenant_id: str) -> str:
        return self.customer_map.get(tenant_id, tenant_id)

    def _get_json(self, path: str) -> Dict[str, Any]:
        req = request.Request(
            f"{self.STRIPE_API_BASE}{path}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Stripe-Version": "2024-06-20",
            },
            method="GET",
        )
        response = urlopen(req)
        try:
            response_body = response.read().decode("utf-8")
        finally:
            if hasattr(response, "close"):
                response.close()
        if not response_body:
            return {}
        return json.loads(response_body)

    def validate_configuration(self, tenant_id: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "failed", "reason": "missing_api_key"}

        customer_id = self._resolve_customer_id(str(tenant_id))
        result: Dict[str, Any] = {
            "status": "ok",
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "meter_name": self.meter_name,
            "account_found": False,
            "meter_found": False,
            "customer_found": False,
        }

        try:
            account = self._get_json("/account")
            result["account_found"] = bool(account.get("id"))
            result["account_id"] = account.get("id")
        except error.URLError as exc:
            result["status"] = "failed"
            result["account_error"] = str(exc)

        try:
            meters = self._get_json("/billing/meters?limit=100")
            data = meters.get("data", []) if isinstance(meters, dict) else []
            meter_names = {
                (item.get("display_name") or item.get("id") or "").lower(): item
                for item in data
            }
            result["meter_found"] = (self.meter_name.lower() in meter_names) or any(
                (item.get("display_name") or item.get("id") or "").lower() == self.meter_name.lower()
                for item in data
            )
            result["meter_id"] = next(
                (
                    item.get("id")
                    for item in data
                    if (item.get("display_name") or item.get("id") or "").lower() == self.meter_name.lower()
                ),
                None,
            )
        except error.URLError as exc:
            result["status"] = "failed"
            result["meter_error"] = str(exc)

        try:
            customer = self._get_json(f"/customers/{customer_id}")
            result["customer_found"] = bool(customer.get("id"))
            result["customer_details"] = customer
        except error.URLError as exc:
            result["status"] = "failed"
            result["customer_error"] = str(exc)

        if result["status"] == "ok" and not (result["account_found"] and result["meter_found"] and result["customer_found"]):
            result["status"] = "failed"
            result["reason"] = "Stripe account, meter, or customer mismatch"

        return result

    def build_usage_payload(self, event: Dict[str, Any]) -> Dict[str, Any]:
        amount = float(event.get("amount_usd", 0.0) or 0.0)
        quantity = 1 if amount > 0 else 0
        tenant_id = event.get("tenant_id", "unknown")

        return {
            "event_name": event.get("event_name", "btp.guard.action.allowed"),
            "customer_id": self._resolve_customer_id(str(tenant_id)),
            "quantity": quantity,
            "value": amount,
            "currency": event.get("currency", "USD"),
            "tenant_id": tenant_id,
            "agent_id": event.get("agent_id", "unknown"),
            "action_type": event.get("action_type", "unknown"),
            "policy_version": event.get("policy_version", "unknown"),
            "receipt_sha256": event.get("receipt_sha256"),
            "metadata": {
                "event_id": event.get("id"),
                "created_at": event.get("created_at"),
                "meter_name": self.meter_name,
            },
        }

    def report_usage(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None

        payload = self.build_usage_payload(event)
        meter_event = {
            "event_name": self.meter_name,
            "payload[stripe_customer_id]": payload["customer_id"],
            "payload[value]": str(payload["quantity"]),
        }

        body = urlencode(meter_event).encode("utf-8")
        req = request.Request(
            f"{self.STRIPE_API_BASE}/billing/meter_events",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Stripe-Version": "2024-06-20",
            },
            method="POST",
        )

        try:
            response = urlopen(req)
            try:
                response_body = response.read().decode("utf-8")
            finally:
                if hasattr(response, "close"):
                    response.close()
            return {
                "status": "success",
                "meter_name": self.meter_name,
                "usage": payload,
                "response": json.loads(response_body) if response_body else {},
            }
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            return {
                "status": "failed",
                "meter_name": self.meter_name,
                "usage": payload,
                "response": json.loads(response_body) if response_body else {},
                "error": str(exc),
            }
        except error.URLError as exc:
            return {
                "status": "failed",
                "meter_name": self.meter_name,
                "usage": payload,
                "response": {},
                "error": str(exc),
            }
