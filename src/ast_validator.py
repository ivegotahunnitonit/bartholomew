"""
Bartholomew AST Security & Invariant Validator
=============================================
Performs deep Abstract Syntax Tree (AST) static analysis on Python code payloads.
Replaces naive substring filtering with structural AST node inspection:
  - Detects dynamic execution calls (eval, exec, __import__, compile).
  - Detects destructive OS/process invocations (os.system, subprocess, shutil.rmtree).
  - Calculates AST node mutation deltas (AST_MAX_DELTA governance).
"""

import ast
import time
from typing import Dict, Any, Tuple, List, Set

class ASTSecurityValidator:
    FORBIDDEN_CALLS: Set[str] = {
        "eval", "exec", "compile", "__import__",
        "os.system", "os.popen", "os.spawn", "os.remove", "os.unlink", "os.rmdir",
        "subprocess.Popen", "subprocess.call", "subprocess.run", "subprocess.check_output",
        "shutil.rmtree", "shutil.move"
    }

    FORBIDDEN_MODULES: Set[str] = {
        "pty", "socket", "ctypes"
    }

    @classmethod
    def validate_code_ast(cls, code_str: str, max_ast_nodes: int = 500) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Parses Python code into an AST and inspects all nodes structurally.
        Returns: (is_safe, reason, metadata)
        """
        start_us = time.perf_counter()

        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return False, f"AST Parse Error: Invalid Python syntax ({str(e)})", {"error": "SYNTAX_ERROR"}

        total_nodes = 0
        violations = []

        for node in ast.walk(tree):
            total_nodes += 1

            # 1. Inspect Function & Method Calls (ast.Call)
            if isinstance(node, ast.Call):
                call_name = cls._get_call_name(node.func)
                if call_name in cls.FORBIDDEN_CALLS:
                    violations.append(f"Forbidden AST Call: '{call_name}'")

            # 2. Inspect Direct Imports (ast.Import / ast.ImportFrom)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in cls.FORBIDDEN_MODULES:
                        violations.append(f"Forbidden Module Import: '{alias.name}'")

            elif isinstance(node, ast.ImportFrom):
                if node.module in cls.FORBIDDEN_MODULES:
                    violations.append(f"Forbidden Module Import: '{node.module}'")

        dt_us = (time.perf_counter() - start_us) * 1_000_000

        # 3. Check AST Complexity / Node Limit
        if total_nodes > max_ast_nodes:
            violations.append(f"AST Delta Limit Exceeded: {total_nodes} nodes > cap {max_ast_nodes}")

        is_safe = len(violations) == 0
        reason = "AST static analysis verified clean." if is_safe else "; ".join(violations)

        metadata = {
            "total_ast_nodes": total_nodes,
            "violations_found": violations,
            "analysis_latency_us": round(dt_us, 2)
        }

        return is_safe, reason, metadata

    @staticmethod
    def _get_call_name(func_node: ast.AST) -> str:
        """Resolves composite function call names like 'os.system' or 'subprocess.run'."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            value_name = ASTSecurityValidator._get_call_name(func_node.value)
            if value_name:
                return f"{value_name}.{func_node.attr}"
            return func_node.attr
        return ""
