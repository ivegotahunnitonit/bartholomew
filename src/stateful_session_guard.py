"""
Bartholomew Stateful Multi-Turn Session Guard (BTP v2.5.0)
=========================================================
Catches indirect prompt injection and split-payload attacks across multiple
agent execution turns.

Problem:
  Adversaries split destructive commands across distinct agent steps to bypass
  stateless per-turn scanners:
    Turn 1: cmd_part1 = "rm -"
    Turn 2: cmd_part2 = "rf /"
    Turn 3: subprocess.run(cmd_part1 + cmd_part2)

Solution:
  Maintains an in-memory rolling session context window per `session_id` using a
  high-performance FIFO ring buffer. Evaluates both the immediate turn and the
  synthesized cross-turn trajectory to detect reconstructed shell, SQL, or
  exfiltration signatures before execution.
"""

import re
import time
from collections import deque
from typing import Dict, Any, List, Optional, Tuple

class RollingSessionContext:
    """
    Fixed-capacity ring buffer tracking rolling agent trajectory state.
    """
    def __init__(self, session_id: str, max_turns: int = 8):
        self.session_id = session_id
        self.max_turns = max_turns
        self.history: deque = deque(maxlen=max_turns)
        self.cumulative_variables: Dict[str, str] = {}
        self.violation_count: int = 0
        self.created_at: float = time.time()
        self.last_active: float = time.time()

    def add_turn(self, action_type: str, payload: Dict[str, Any], raw_code: str = "") -> None:
        """Records a new execution step in the rolling window."""
        self.last_active = time.time()
        turn_entry = {
            "timestamp": self.last_active,
            "action_type": action_type,
            "payload": payload,
            "raw_code": raw_code
        }
        self.history.append(turn_entry)

        # Track string variable assignments across turns: var = "..." or '...'
        if raw_code:
            matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*["\']([^"\']+)["\']', raw_code)
            for var_name, str_val in matches:
                self.cumulative_variables[var_name] = str_val

    def get_synthesized_buffer(self) -> str:
        """Concatenates historical code snippets and reconstructed variables for composite AST inspection."""
        pieces = []
        for turn in self.history:
            code = turn.get("raw_code", "")
            if code:
                pieces.append(code)
                # Resolve pairwise string variable concatenations: v1 + v2
                concat_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\+\s*([a-zA-Z_][a-zA-Z0-9_]*)', code)
                for v1, v2 in concat_matches:
                    if v1 in self.cumulative_variables and v2 in self.cumulative_variables:
                        resolved = self.cumulative_variables[v1] + self.cumulative_variables[v2]
                        pieces.append(f"RESOLVED_CONCAT: {resolved}")
            else:
                pieces.append(str(turn.get("payload", {})))

        # Include direct joined variable values
        if self.cumulative_variables:
            pieces.append("".join(self.cumulative_variables.values()))
            pieces.append(" ".join(self.cumulative_variables.values()))

        return "\n".join(pieces)


class StatefulSessionSecurityManager:
    """
    Stateful multi-turn invariant evaluator.
    Interprets current turn in context of session history to catch stealth multi-turn payloads.
    """
    DESTRUCTIVE_CROSS_TURN_PATTERNS = [
        re.compile(r'rm\s*-\s*[rRfF]+\s*[/~]', re.IGNORECASE),
        re.compile(r'rm\s*-[rRfF]+\s*[/~]', re.IGNORECASE),
        re.compile(r'drop\s+(table|database|schema)\b', re.IGNORECASE),
        re.compile(r'truncate\s+table\b', re.IGNORECASE),
        re.compile(r'format\s+[a-zA-Z]:', re.IGNORECASE),
        re.compile(r'chmod\s+777', re.IGNORECASE),
        re.compile(r'(mkfs|dd\s+if=)', re.IGNORECASE),
        re.compile(r'__import__\s*\(\s*[\'"]os[\'"]\s*\)\s*\.\s*system', re.IGNORECASE),
        re.compile(r'getattr\s*\(\s*__import__\s*\(\s*[\'"]os[\'"]\s*\)', re.IGNORECASE)
    ]

    @staticmethod
    def normalize_text(text: str) -> str:
        """Strips SQL/C comments and collapses whitespace to defeat comment-injection obfuscation."""
        clean = re.sub(r'/\*.*?\*/', ' ', text)
        clean = re.sub(r'--[^\r\n]*', ' ', clean)
        return re.sub(r'\s+', ' ', clean)

    def __init__(self, max_history_turns: int = 8, session_ttl_seconds: float = 3600.0):
        self.sessions: Dict[str, RollingSessionContext] = {}
        self.max_history_turns = max_history_turns
        self.session_ttl = session_ttl_seconds

    def get_or_create_session(self, session_id: str) -> RollingSessionContext:
        """Retrieves or initializes a session context."""
        now = time.time()
        # Clean up stale sessions
        stale_keys = [k for k, s in self.sessions.items() if now - s.last_active > self.session_ttl]
        for k in stale_keys:
            del self.sessions[k]

        if session_id not in self.sessions:
            self.sessions[session_id] = RollingSessionContext(session_id, max_turns=self.max_history_turns)
        return self.sessions[session_id]

    def evaluate_turn(
        self,
        session_id: str,
        action_type: str,
        payload: Dict[str, Any],
        raw_code: str = ""
    ) -> Tuple[bool, str, float]:
        """
        Evaluates a turn against both isolated invariants and rolling cross-turn synthesis.
        Returns (is_allowed, reason, latency_us).
        """
        t0 = time.perf_counter()
        session = self.get_or_create_session(session_id)

        # 1. Immediate Turn Assessment
        combined_immediate = f"{raw_code} {payload}"
        normalized_immediate = self.normalize_text(combined_immediate)
        for pattern in self.DESTRUCTIVE_CROSS_TURN_PATTERNS:
            if pattern.search(combined_immediate) or pattern.search(normalized_immediate):
                session.violation_count += 1
                dt_us = (time.perf_counter() - t0) * 1_000_000
                return False, f"BTP-STATEFUL-001: Immediate destructive pattern detected ({pattern.pattern})", dt_us

        # 2. Add turn to session trajectory
        session.add_turn(action_type, payload, raw_code)

        # 3. Cross-Turn Reconstructed Payload Assessment (Evaluated on execution, synthesis, or invocation actions)
        is_execution_or_concat = any(act in action_type.upper() for act in ["EXEC", "SYSTEM", "RUN", "EVAL", "MUTATE", "DISPATCH", "INVOKE"]) or \
                                any(kw in raw_code for kw in ["os.system", "eval(", "exec(", "subprocess", "cursor.execute", "system(", "+"])

        if is_execution_or_concat:
            synthesized_text = session.get_synthesized_buffer()
            normalized_synth = self.normalize_text(synthesized_text)
            for pattern in self.DESTRUCTIVE_CROSS_TURN_PATTERNS:
                if pattern.search(synthesized_text) or pattern.search(normalized_synth):
                    session.violation_count += 1
                    dt_us = (time.perf_counter() - t0) * 1_000_000
                    return False, f"BTP-STATEFUL-002: Multi-turn indirect injection intercepted across {len(session.history)} turns ({pattern.pattern})", dt_us

        dt_us = (time.perf_counter() - t0) * 1_000_000
        return True, "Stateful multi-turn invariants verified clean", dt_us

StatefulSessionGuard = StatefulSessionSecurityManager

