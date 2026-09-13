#!/usr/bin/env python3
"""
Agentic-Eval Real-Time WebSocket Alert Hub & Webhook Forwarder v1.0
===================================================================
Custom real-time alert relay system (replaces third-party Slack/Discord dependencies).
- WebSocket broadcast to /monitor client UI
- REST trigger endpoint POST /api/v1/alerts/trigger
- Optional secondary forwarding to Slack/Discord webhooks if configured
"""
import time
import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import WebSocket

class AlertHubManager:
    """Manages live WebSocket subscriptions for real-time security alerts."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.alert_history: List[Dict[str, Any]] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send recent history on connection
        for alert in self.alert_history[-10:]:
            await websocket.send_json(alert)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, alert_payload: Dict[str, Any]):
        """Broadcasts a new security alert in real-time to all connected dashboards."""
        alert_payload["timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        if "id" not in alert_payload:
            alert_payload["id"] = f"ALT-{int(time.time()*1000)}"

        self.alert_history.append(alert_payload)

        # Broadcast to WebSockets
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(alert_payload)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

        return alert_payload

alert_hub = AlertHubManager()
