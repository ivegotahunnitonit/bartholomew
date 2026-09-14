"""
Bartholomew Trust Protocol (BTP) Guard Package.
Sub-35µs zero-trust AST execution firewall and multi-tenant security gateway.
"""

from .btp_guard import Guard, WireGuard

# Canonical drop-in instance and decorator for autonomous agents & LLMs
guard = Guard()
protect = guard.protect

__version__ = "5.4.12"

__all__ = [
    "Guard",
    "WireGuard",
    "guard",
    "protect",
    "__version__"
]
