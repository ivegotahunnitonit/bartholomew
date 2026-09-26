import unittest
import os
import shutil
from btp_guard.warranty_service import WarrantyFundManager
from btp_guard.mcp_clearinghouse import MCPClearinghouseGateway

class TestCommercialRevenueStreams(unittest.TestCase):
    def setUp(self):
        self.tmp_ledger = ".test_warranty_ledger.json"
        self.tmp_mcp_ledger = ".test_clearinghouse_ledger.json"

    def tearDown(self):
        if os.path.exists(self.tmp_ledger):
            os.remove(self.tmp_ledger)
        if os.path.exists(self.tmp_mcp_ledger):
            os.remove(self.tmp_mcp_ledger)

    def test_bonded_agent_warranty_issuance(self):
        fund_mgr = WarrantyFundManager(reserve_pool_usd=100_000.0, ledger_file=self.tmp_ledger)
        bond = fund_mgr.issue_bond(agent_id="autonomous-finance-agent-01", coverage_limit_usd=10_000.0)
        
        self.assertEqual(bond["agent_id"], "autonomous-finance-agent-01")
        self.assertEqual(bond["coverage_limit_usd"], 10_000.0)
        self.assertEqual(bond["premium_paid_usd"], 25.0) # 0.25% of 10,000
        self.assertEqual(bond["status"], "ACTIVE_UNDERWRITTEN")
        self.assertIn("UNAUTHORIZED_CREDENTIAL_EXFILTRATION", bond["covered_perils"])
        
        status = fund_mgr.get_status()
        self.assertEqual(status["active_bonds_count"], 1)
        self.assertEqual(status["reserve_pool_usd"], 100_025.0)

    def test_mcp_clearinghouse_take_rate(self):
        gateway = MCPClearinghouseGateway()
        gateway.LEDGER_FILE = self.tmp_mcp_ledger
        
        # Test 1: Benign paid tool call (e.g. $1.00 web search)
        receipt = gateway.settle_tool_call(
            agent_id="agent-researcher",
            tool_name="web_search_mcp",
            tool_payload="echo 'search python 3.14'",
            tool_price_usd=1.00
        )
        self.assertEqual(receipt["settlement_status"], "SETTLED")
        self.assertEqual(receipt["tool_price_usd"], 1.00)
        self.assertEqual(receipt["protocol_fee_usd"], 0.025) # 2.5% protocol cut!
        self.assertEqual(receipt["provider_net_payout_usd"], 0.975)
        
        # Test 2: Adversarial tool call blocked BEFORE fee is charged
        veto_receipt = gateway.settle_tool_call(
            agent_id="agent-rogue",
            tool_name="shell_execute_mcp",
            tool_payload="rm -rf / --no-preserve-root",
            tool_price_usd=5.00
        )
        self.assertEqual(veto_receipt["settlement_status"], "VETOED_BEFORE_CHARGE")
        self.assertEqual(veto_receipt["verdict"], "DENY")
        self.assertEqual(veto_receipt["charged_usd"], 0.0)

if __name__ == "__main__":
    unittest.main()
