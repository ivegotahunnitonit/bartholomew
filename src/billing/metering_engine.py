"""
BTP Multi-Tenant Usage Metering & Billing Engine.
"""

import os
import json
import time
import hmac
import hashlib
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, List


DEFAULT_LEDGER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", ".btp_usage_ledger.json"
)

# Standard pricing units
AST_SCAN_UNIT_USD = 0.0001
THREAT_BLOCKED_UNIT_USD = 0.001
ESCROW_FEE_RATIO = 0.005  # 0.5%
WEBHOOK_UNIT_USD = 0.002
BASE_PRO_SUBSCRIPTION_USD = 49.00


@dataclass
class TenantUsageRecord:
    tenant_id: str
    org_id: str = "default-org"
    project_id: str = "default-project"
    ast_scans: int = 0
    threats_blocked: int = 0
    escrow_volume_usd: float = 0.0
    webhooks_dispatched: int = 0
    period_start_utc: float = field(default_factory=time.time)
    last_updated_utc: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeteredInvoice:
    invoice_id: str
    tenant_id: str
    org_id: str
    period_start: float
    period_end: float
    base_subscription_usd: float
    ast_scans_count: int
    ast_scans_cost_usd: float
    threats_blocked_count: int
    threats_blocked_cost_usd: float
    escrow_volume_cleared_usd: float
    escrow_fees_usd: float
    webhooks_count: int
    webhooks_cost_usd: float
    total_due_usd: float
    currency: str = "USD"
    settlement_rail: str = "STRIPE_METERED"
    signature: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TenantUsageMeter:
    """Tracks and persists usage across all tenant workspaces."""

    def __init__(self, ledger_path: Optional[str] = None):
        self.ledger_path = os.path.abspath(ledger_path or DEFAULT_LEDGER_PATH)
        self.records: Dict[str, TenantUsageRecord] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.get("tenants", {}).items():
                        self.records[k] = TenantUsageRecord(**v)
            except Exception:
                pass

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump({
                    "version": "5.3.0",
                    "tenants": {k: v.to_dict() for k, v in self.records.items()}
                }, f, indent=2)
        except Exception:
            pass

    def get_or_create(self, tenant_id: str, org_id: str = "default-org", project_id: str = "default-project") -> TenantUsageRecord:
        if tenant_id not in self.records:
            self.records[tenant_id] = TenantUsageRecord(
                tenant_id=tenant_id,
                org_id=org_id,
                project_id=project_id,
                period_start_utc=time.time(),
                last_updated_utc=time.time()
            )
            self._save()
        return self.records[tenant_id]

    def record_ast_scan(self, tenant_id: str, count: int = 1):
        rec = self.get_or_create(tenant_id)
        rec.ast_scans += count
        rec.last_updated_utc = time.time()
        self._save()

    def record_threat_blocked(self, tenant_id: str, count: int = 1):
        rec = self.get_or_create(tenant_id)
        rec.threats_blocked += count
        rec.last_updated_utc = time.time()
        self._save()

    def record_escrow_settlement(self, tenant_id: str, volume_usd: float):
        rec = self.get_or_create(tenant_id)
        rec.escrow_volume_usd += volume_usd
        rec.last_updated_utc = time.time()
        self._save()

    def record_webhook_dispatch(self, tenant_id: str, count: int = 1):
        rec = self.get_or_create(tenant_id)
        rec.webhooks_dispatched += count
        rec.last_updated_utc = time.time()
        self._save()


class MeteredInvoiceGenerator:
    """Calculates, signs, and exports itemized metered invoices for tenants."""

    SIGNING_SECRET = "btp_signing_master_k881"

    @classmethod
    def generate_invoice(
        cls,
        usage: TenantUsageRecord,
        settlement_rail: str = "STRIPE_METERED",
        include_base_subscription: bool = True
    ) -> MeteredInvoice:
        base_fee = BASE_PRO_SUBSCRIPTION_USD if include_base_subscription else 0.0
        ast_cost = round(usage.ast_scans * AST_SCAN_UNIT_USD, 4)
        threat_cost = round(usage.threats_blocked * THREAT_BLOCKED_UNIT_USD, 4)
        escrow_cost = round(usage.escrow_volume_usd * ESCROW_FEE_RATIO, 4)
        webhook_cost = round(usage.webhooks_dispatched * WEBHOOK_UNIT_USD, 4)

        total = round(base_fee + ast_cost + threat_cost + escrow_cost + webhook_cost, 2)
        entropy = f"{usage.tenant_id}:{time.time_ns()}:{total}"
        invoice_id = f"INV-BTP-{hashlib.sha256(entropy.encode()).hexdigest()[:12].upper()}"

        # Cryptographic HMAC-SHA256 signature
        sign_payload = f"{invoice_id}:{usage.tenant_id}:{total}:{settlement_rail}"
        sig = hmac.new(cls.SIGNING_SECRET.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()

        return MeteredInvoice(
            invoice_id=invoice_id,
            tenant_id=usage.tenant_id,
            org_id=usage.org_id,
            period_start=usage.period_start_utc,
            period_end=time.time(),
            base_subscription_usd=base_fee,
            ast_scans_count=usage.ast_scans,
            ast_scans_cost_usd=ast_cost,
            threats_blocked_count=usage.threats_blocked,
            threats_blocked_cost_usd=threat_cost,
            escrow_volume_cleared_usd=usage.escrow_volume_usd,
            escrow_fees_usd=escrow_cost,
            webhooks_count=usage.webhooks_dispatched,
            webhooks_cost_usd=webhook_cost,
            total_due_usd=total,
            currency="USD",
            settlement_rail=settlement_rail,
            signature=f"btp_sig_{sig[:32]}"
        )
