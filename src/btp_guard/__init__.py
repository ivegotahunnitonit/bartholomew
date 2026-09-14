"""
Bartholomew Trust Protocol (BTP) Guard Package.
Sub-35µs zero-trust AST execution firewall and multi-tenant security gateway.
"""

from .btp_guard import Guard, WireGuard

# Canonical drop-in instance and decorator for autonomous agents & LLMs
guard = Guard()
protect = guard.protect

try:
    from src.client_wrapper import auto_patch, wrap_client
except ImportError:
    try:
        from ..client_wrapper import auto_patch, wrap_client
    except Exception:
        def auto_patch(*args, **kwargs):
            return {}
        def wrap_client(client, *args, **kwargs):
            return client

__version__ = "5.4.12"

__all__ = [
    "Guard",
    "WireGuard",
    "guard",
    "protect",
    "auto_patch",
    "wrap_client",
    "__version__"
]
