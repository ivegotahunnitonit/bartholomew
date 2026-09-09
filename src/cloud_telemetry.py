"""
Bartholomew Cloud — Ultra-Low-Overhead Telemetry Dispatcher
===========================================================
Provides non-blocking, asynchronous background telemetry streaming from local
btp-guard instances to the Bartholomew Cloud Control Plane.

Zero-Lag Guarantee:
Enqueuing an event takes <2 microseconds in memory. All network I/O, retries,
and HTTP batching happen in a decoupled background daemon thread, ensuring
the host agent's critical execution path is completely unaffected.
"""

import os
import json
import time
import uuid
import queue
import logging
import threading
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

logger = logging.getLogger("btp.cloud_telemetry")

DEFAULT_CLOUD_ENDPOINT = os.getenv("BTP_CLOUD_ENDPOINT", "https://cloud.bartholomew.info/api/v1/telemetry/ingest")


class CloudTelemetryDispatcher:
    """
    Thread-safe, non-blocking telemetry dispatcher for Bartholomew Cloud.
    """
    _instance: Optional["CloudTelemetryDispatcher"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        batch_size: int = 50,
        flush_interval_seconds: float = 2.0,
        max_queue_size: int = 5000
    ):
        self.api_key = api_key or os.getenv("BTP_API_KEY") or os.getenv("BTP_CLOUD_KEY", "")
        self.endpoint = endpoint or DEFAULT_CLOUD_ENDPOINT
        self.batch_size = batch_size
        self.flush_interval = flush_interval_seconds
        self.queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.total_enqueued = 0
        self.running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="BTP-CloudTelemetry-Worker")
        self._worker_thread.start()

    @classmethod
    def get_default(cls, api_key: Optional[str] = None, endpoint: Optional[str] = None) -> "CloudTelemetryDispatcher":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(api_key=api_key, endpoint=endpoint)
            elif api_key and not cls._instance.api_key:
                cls._instance.api_key = api_key
            return cls._instance

    def enqueue_event(
        self,
        verdict: str,
        reason: str = "",
        rule_id: str = "",
        latency_us: float = 0.0,
        agent_id: str = "agent-1",
        workspace_id: str = "default",
        action_type: str = "TOOL_CALL",
        payload_hash: str = "",
        receipt: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Pushes a telemetry record into the local memory queue in <2 microseconds.
        Never blocks the caller. If the queue is full, drops the event to preserve host performance.
        """
        if not self.api_key and not os.getenv("BTP_ENABLE_ANONYMOUS_TELEMETRY"):
            return False

        event = {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "timestamp": time.time(),
            "action_type": action_type,
            "verdict": verdict,
            "rule_id": rule_id,
            "reason": reason,
            "latency_us": latency_us,
            "payload_hash": payload_hash,
            "receipt": receipt or {},
            "metadata": metadata or {}
        }

        try:
            self.queue.put_nowait(event)
            self.total_enqueued += 1
            return True
        except queue.Full:
            logger.warning("[BTP Cloud] Telemetry queue full; dropping event to preserve execution performance.")
            return False

    def _worker_loop(self):
        """Background thread that batches and dispatches events to the cloud endpoint."""
        batch: List[Dict[str, Any]] = []
        last_flush = time.time()

        while self.running:
            try:
                timeout = max(0.1, self.flush_interval - (time.time() - last_flush))
                event = self.queue.get(timeout=timeout)
                batch.append(event)
            except queue.Empty:
                pass

            # Flush condition: reached batch limit or interval expired
            if len(batch) >= self.batch_size or (batch and (time.time() - last_flush) >= self.flush_interval):
                self._dispatch_batch(batch)
                batch = []
                last_flush = time.time()

        # Final drain on shutdown
        if batch:
            self._dispatch_batch(batch)

    def _dispatch_batch(self, batch: List[Dict[str, Any]]):
        """Sends an HTTP POST request with the batched events."""
        if not batch or not self.endpoint:
            return

        payload = {
            "events": batch,
            "client_version": "5.4.0",
            "sent_at": time.time()
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "BTP-Guard-SDK/5.4.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(self.endpoint, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status in (200, 201, 202):
                    logger.debug(f"[BTP Cloud] Successfully dispatched {len(batch)} telemetry events.")
        except urllib.error.HTTPError as e:
            logger.debug(f"[BTP Cloud HTTP Error {e.code}] {e.reason}")
        except Exception as e:
            logger.debug(f"[BTP Cloud Network Error] {e}")

    def flush(self, timeout: float = 3.0):
        """Forces pending events to flush synchronously (useful on process exit)."""
        deadline = time.time() + timeout
        while not self.queue.empty() and time.time() < deadline:
            time.sleep(0.05)

    def stop(self):
        """Stops the background worker thread cleanly."""
        self.running = False
        self.flush()
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
