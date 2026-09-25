import unittest
import threading
import time
import json
import urllib.request
import urllib.error
from http.server import HTTPServer
from packages.sidecar_proxy.proxy import SidecarProxyHandler

class TestSidecarServerE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start proxy server on random high port
        cls.port = 19095
        cls.server = HTTPServer(("127.0.0.1", cls.port), SidecarProxyHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_endpoint(self):
        url = f"http://127.0.0.1:{self.port}/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "HEALTHY")
            self.assertEqual(data["version"], "5.4.21")
            self.assertEqual(data["gpu_vram_mb"], 0)
            self.assertEqual(resp.getheader("X-Protected-By"), "Bartholomew-ARP-v5.4.21")

    def test_adversarial_command_blocked_403(self):
        url = f"http://127.0.0.1:{self.port}/execute"
        payload = json.dumps({"command": "rm -rf / --no-preserve-root"}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json", "X-Agent-ID": "test-adversary"},
            method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        
        self.assertEqual(ctx.exception.code, 403)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(body["error"], "BTP_GUARD_INTERCEPT")
        self.assertEqual(body["verdict"], "DENY")
        self.assertIn("Catastrophic shell pattern detected", body["reason"])
        self.assertEqual(body["engine"], "Bartholomew-Compiler-AST")
        self.assertLess(body["latency_us"], 1000)

if __name__ == "__main__":
    unittest.main()
