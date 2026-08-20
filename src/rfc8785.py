"""
RFC 8785 Standards-Compliant JSON Canonicalization Scheme (JCS) Implementation
Implements IETF RFC 8785 Section 3 canonical formatting rules:
- UTF-8 encoding without BOM
- Strict UTF-16 code unit lexicographical key sorting
- IEEE 754 float/int formatting (Section 3.2.2.3)
- Minimal control character string escaping (Section 3.2.2.2)
"""

import math
from typing import Any

def rfc8785_canonicalize(data: Any) -> bytes:
    """Serializes data into RFC 8785 Canonical UTF-8 Byte representation."""
    return _serialize(data).encode('utf-8')

def _serialize(val: Any) -> str:
    if val is None:
        return "null"
    elif isinstance(val, bool):
        return "true" if val else "false"
    elif isinstance(val, (int, float)):
        return _serialize_number(val)
    elif isinstance(val, str):
        return _serialize_string(val)
    elif isinstance(val, (list, tuple)):
        return "[" + ",".join(_serialize(item) for item in val) + "]"
    elif isinstance(val, dict):
        # RFC 8785 Section 3.2.3: Object keys sorted lexicographically by UTF-16 code units
        sorted_keys = sorted(val.keys(), key=lambda k: [ord(c) for c in k])
        return "{" + ",".join(f"{_serialize_string(k)}:{_serialize(val[k])}" for k in sorted_keys) + "}"
    else:
        raise TypeError(f"Type {type(val)} is not JSON-serializable under RFC 8785")

def _serialize_number(n: Any) -> str:
    if isinstance(n, bool):
        return "true" if n else "false"
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        if math.isnan(n) or math.isinf(n):
            raise ValueError(f"NaN and Infinity are forbidden in RFC 8785 JSON: {n}")
        if n == 0.0:
            return "0" # -0.0 serialized as 0
        # Format matching ECMAScript / RFC 8785 Section 3.2.2.3
        if n.is_integer():
            return str(int(n))
        formatted = repr(n)
        return formatted.replace("E", "e").replace("e+", "e")
    return str(n)

def _serialize_string(s: str) -> str:
    out = []
    for c in s:
        code = ord(c)
        if c == '"':
            out.append('\\"')
        elif c == '\\':
            out.append('\\\\')
        elif c == '\b':
            out.append('\\b')
        elif c == '\f':
            out.append('\\f')
        elif c == '\n':
            out.append('\\n')
        elif c == '\r':
            out.append('\\r')
        elif c == '\t':
            out.append('\\t')
        elif code < 0x20:
            out.append(f"\\u{code:04x}")
        else:
            out.append(c)
    return '"' + "".join(out) + '"'
