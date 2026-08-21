"""
Bartholomew Native Core FFI Bridge
==================================
Provides direct ctypes binding to compiled C/Rust invariant engine,
with seamless fallback to optimized native Python implementation.
"""

import os
import sys
import ctypes
import math
import time
from typing import Tuple, Optional

# Potential shared library locations
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_LIB_CANDIDATES = [
    os.path.join(CURRENT_DIR, "btp_core.dll"),
    os.path.join(CURRENT_DIR, "libbtp_core.so"),
    os.path.join(CURRENT_DIR, "libbtp_core.dylib"),
]

_c_lib = None
for lib_path in SHARED_LIB_CANDIDATES:
    if os.path.exists(lib_path):
        try:
            _c_lib = ctypes.CDLL(lib_path)
            # Setup argument and return types
            _c_lib.btp_calculate_marginal_utility.argtypes = [ctypes.c_double, ctypes.c_int]
            _c_lib.btp_calculate_marginal_utility.restype = ctypes.c_double

            _c_lib.btp_contains_forbidden_pattern.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            _c_lib.btp_contains_forbidden_pattern.restype = ctypes.c_int

            _c_lib.btp_is_path_traversal_attack.argtypes = [ctypes.c_char_p]
            _c_lib.btp_is_path_traversal_attack.restype = ctypes.c_int
            break
        except Exception:
            _c_lib = None


class NativeInvariantEngine:
    """
    Sub-5 microsecond native invariant bridge.
    Uses C shared library when present; pure optimized fallback otherwise.
    """
    def __init__(self):
        self.is_native_c_loaded = (_c_lib is not None)

    def calculate_marginal_utility(self, decay_rate: float, repetition_count: int) -> float:
        if self.is_native_c_loaded:
            return float(_c_lib.btp_calculate_marginal_utility(ctypes.c_double(decay_rate), ctypes.c_int(repetition_count)))
        
        # Optimized fallback
        if repetition_count <= 1:
            return 1.0
        return max(0.0, min(1.0, math.exp(-decay_rate * (repetition_count - 1))))

    def contains_forbidden_pattern(self, payload: str, pattern: str) -> bool:
        if self.is_native_c_loaded:
            return bool(_c_lib.btp_contains_forbidden_pattern(
                payload.encode("utf-8"),
                pattern.encode("utf-8")
            ))
        
        return pattern.lower() in payload.lower()

    def is_path_traversal_attack(self, path: str) -> bool:
        if self.is_native_c_loaded:
            return bool(_c_lib.btp_is_path_traversal_attack(path.encode("utf-8")))

        if "../" in path or "..\\" in path:
            return True
        
        forbidden = [".env", "id_rsa", "id_ed25519", "shadow", "passwd", "sam", "system"]
        path_lower = path.lower()
        return any(f in path_lower for f in forbidden)


# Global Singleton
NATIVE_ENGINE = NativeInvariantEngine()
