"""
Bartholomew Guard for NVIDIA NIM (Inference Microservice)
=========================================================
Sub-35µs AST invariant evaluation, prompt injection screening, Keystone passkey
authorization, and cryptographic Merkle audit receipts for NVIDIA NIM microservices.

Usage:
    from btp_guard.integrations.nvidia_nim import BartholomewNIMGuard

    guard = BartholomewNIMGuard(base_url="http://localhost:8000/v1")
    is_safe, reason = guard.inspect_prompt_payload(messages)
    clearance = guard.inspect_tool_call(tool_name="bash_exec", arguments={"command": cmd})
"""

from src.integrations.nvidia_nim import BartholomewNIMGuard

__all__ = ["BartholomewNIMGuard"]
