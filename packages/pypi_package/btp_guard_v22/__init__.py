"""
btp_guard: BTP v2.2 Universal Agent Trust Guard
"""

from .guard import BTPGuard
from .verifier import independent_verify_btp_receipt, rfc8785_canonicalize

try:
    from src import Guard, SovereignAgentPassport
except Exception:
    Guard = BTPGuard
    SovereignAgentPassport = None

try:
    from btp_guard import WireGuard
except Exception:
    class WireGuard:
        pass

__version__ = "5.4.6"
__all__ = ["BTPGuard", "Guard", "independent_verify_btp_receipt", "rfc8785_canonicalize", "WireGuard"]
