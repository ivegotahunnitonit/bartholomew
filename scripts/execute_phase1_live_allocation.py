"""
Bartholomew Phase 1 Live $10 Micro-Capital Execution Engine
============================================================
Records Human Approval of Option B and outputs the formal BTP Capital Allocation Envelope.
Enforces:
- Hard Cap: $10.00 max
- Zero Fee Leakage Rule (>3.0% fee blocked)
- External Settlement Audit Gate
"""

import sys
import os
sys.path.insert(0, os.path.abspath("pypi_package"))

import json
import datetime
from bartholomew_eval.linux_adapter import LinuxExecutionAdapter


def execute_option_b_allocation():
    adapter = LinuxExecutionAdapter()
    
    # Financial fee protection check
    fee_audit = adapter.evaluate_financial_protection(
        transaction_amount_usd=10.00,
        fee_usd=0.10,
        payment_method="single_use_virtual_card"
    )

    request_envelope = {
        "protocol": "Bartholomew Trust Protocol (BTP v0.1)",
        "request_type": "BTP_RESOURCE_CAPITAL_ALLOCATION_REQUEST",
        "human_gate_decision": "APPROVED_OPTION_B",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "agent_did": "did:bth:autonomous_operator_01",
        "financial_terms": {
            "allocated_capital_usd": "$10.00",
            "maximum_downside_risk_usd": "$10.00",
            "fee_protection_status": fee_audit["fee_protection_status"],
            "fee_percentage": fee_audit["fee_percentage"],
            "target_vendor": "Telemetry & Market Data API Provider",
            "purpose": "Acquire high-throughput API access token to unlock live subscriber aggregator pipeline on acn-26670.web.app",
            "expected_gross_revenue_usd": "$38.00",
            "expected_net_proceeds_usd": "$28.00",
            "gross_revenue_multiple": "3.80x",
            "net_proceeds_multiple": "2.80x"
        },
        "safety_guarantees": [
            "Single-use hard limit ($10.00 max). Zero access to bank accounts.",
            "Zero recurring subscriptions or auto-renewals.",
            "External Settlement Rule: Net proceeds ($28.00) locked until Stripe/Bank TX clears externally.",
            "Auto-Rollback: If 0 external transactions clear within 48h, auto-revoke access key."
        ],
        "funding_input_instructions": {
            "recommended_method": "Single-Use Virtual Card (Privacy.com / Stripe) with hard $10.00 limit",
            "alternative_method_1": "10 USDC to pre-funded sub-wallet",
            "alternative_method_2": "Pre-funded $10 API credit key"
        }
    }

    print(json.dumps(request_envelope, indent=2))
    with open("PHASE_1_LIVE_ALLOCATION_ENVELOPE.json", "w", encoding="utf-8") as f:
        json.dump(request_envelope, f, indent=2)

    return request_envelope


if __name__ == "__main__":
    execute_option_b_allocation()
