"""
btp_guard: BTP v2.2 Universal Agent Trust Guard
"""

from .guard import BTPGuard
from .verifier import independent_verify_btp_receipt, rfc8785_canonicalize

__version__ = "2.2.0"
__all__ = ["BTPGuard", "independent_verify_btp_receipt", "rfc8785_canonicalize"]
