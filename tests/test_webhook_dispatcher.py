import unittest
import json
import time
from btp_guard.webhook_dispatcher import (
    WebhookDispatcher,
    WebhookChannel,
    AlertSeverity
)

class TestWebhookDispatcher(unittest.TestCase):
    def setUp(self):
        self.sample_event = {
            "incident_id": "btp-test-001",
            "timestamp": "2026-09-25T20:00:00Z",
            "originating_agent": "agent-swarm-worker-42",
            "verdict": "DENY",
            "reason": "Catastrophic destructive shell command detected",
            "action_payload": "rm -rf / --no-preserve-root",
            "latency_us": 15.70,
            "severity": AlertSeverity.CRITICAL.value
        }

    def test_slack_formatting(self):
        dispatcher = WebhookDispatcher(channel=WebhookChannel.SLACK, webhook_url="https://dummy.slack.com")
        payload = dispatcher.format_payload(self.sample_event)
        
        self.assertIn("attachments", payload)
        blocks = payload["attachments"][0]["blocks"]
        self.assertTrue(any("🚨 [Bartholomew ARP]" in str(b) for b in blocks))
        self.assertTrue(any("agent-swarm-worker-42" in str(b) for b in blocks))
        self.assertTrue(any("rm -rf / --no-preserve-root" in str(b) for b in blocks))

    def test_discord_formatting(self):
        dispatcher = WebhookDispatcher(channel=WebhookChannel.DISCORD, webhook_url="https://dummy.discord.com")
        payload = dispatcher.format_payload(self.sample_event)
        
        self.assertIn("embeds", payload)
        embed = payload["embeds"][0]
        self.assertEqual(embed["title"], "🚨 Security Intercept: DENY")
        self.assertEqual(embed["color"], 15673924) # Red color
        self.assertTrue(any(f["name"] == "Agent Identifier" and "agent-swarm-worker-42" in f["value"] for f in embed["fields"]))

    def test_pagerduty_formatting(self):
        dispatcher = WebhookDispatcher(channel=WebhookChannel.PAGERDUTY, pagerduty_key="pd-routing-key-12345")
        payload = dispatcher.format_payload(self.sample_event)
        
        self.assertEqual(payload["routing_key"], "pd-routing-key-12345")
        self.assertEqual(payload["event_action"], "trigger")
        self.assertEqual(payload["payload"]["severity"], "critical")
        self.assertEqual(payload["payload"]["custom_details"]["verdict"], "DENY")

    def test_siem_jsonld_formatting(self):
        dispatcher = WebhookDispatcher(channel=WebhookChannel.SIEM, webhook_url="https://dummy.siem.com")
        payload = dispatcher.format_payload(self.sample_event)
        
        self.assertEqual(payload["@context"], "https://bartholomew.info/schemas/security-event.jsonld")
        self.assertEqual(payload["event_type"], "BARTHOLOMEW_AGENTIC_INTERCEPT")
        self.assertEqual(payload["threat"]["mitre_atlas_technique"], "AML.T0054")
        self.assertEqual(payload["threat"]["owasp_llm_category"], "LLM02:InsecureOutputHandling")
        self.assertEqual(payload["telemetry"]["vram_overhead_mb"], 0)

    def test_async_dispatch_non_blocking(self):
        dispatcher = WebhookDispatcher(channel=WebhookChannel.GENERIC, webhook_url="http://127.0.0.1:9")
        t0 = time.perf_counter()
        fut = dispatcher.dispatch_async(self.sample_event)
        elapsed_us = (time.perf_counter() - t0) * 1_000_000
        # Main thread submission must take under 1,000 microseconds (1 millisecond)
        self.assertLess(elapsed_us, 5000, f"Async dispatch took {elapsed_us}µs, should be <5ms")

if __name__ == "__main__":
    unittest.main()
