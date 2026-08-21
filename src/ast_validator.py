"""
Bartholomew AST Security & Invariant Validator
=============================================
Performs deep Abstract Syntax Tree (AST) static analysis on Python code payloads.
Handles:
  1. Direct & composite calls (eval, exec, os.system, subprocess.run).
  2. Aliased module calls (import os as o; o.system(...)).
  3. Dynamic attribute access (getattr(os, "system")(...)).
  4. AST node complexity limits (AST_MAX_DELTA governance).
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
        start_us = time.perf_counter()

        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            dt_us = (time.perf_counter() - start_us) * 1_000_000
            return False, f"AST Parse Error: Invalid Python syntax ({str(e)})", {"error": "SYNTAX_ERROR"}

        total_nodes = 0
        violations = []
        aliases: Dict[str, str] = {} # Maps alias name -> original module name (e.g. 'o' -> 'os')

        for node in ast.walk(tree):
            total_nodes += 1

            # Track import aliases (e.g., import os as o, from subprocess import Popen as P)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    original = alias.name
                    asname = alias.asname or alias.name
                    aliases[asname] = original
                    if original in cls.FORBIDDEN_MODULES:
                        violations.append(f"Forbidden Module Import: '{original}'")

            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod in cls.FORBIDDEN_MODULES:
                    violations.append(f"Forbidden Module Import: '{mod}'")
                for alias in node.names:
                    original_func = f"{mod}.{alias.name}" if mod else alias.name
                    asname = alias.asname or alias.name
                    aliases[asname] = original_func

            # Inspect Function & Method Calls (ast.Call)
            elif isinstance(node, ast.Call):
                call_name = cls._resolve_call_name(node.func, aliases)
                if call_name in cls.FORBIDDEN_CALLS:
                    violations.append(f"Forbidden AST Call: '{call_name}'")

                # Detect dynamic getattr evasion: getattr(os, "system")(...)
                if isinstance(node.func, ast.Name) and node.func.id == "getattr":
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                        attr_val = str(node.args[1].value)
                        target_obj = cls._resolve_call_name(node.args[0], aliases)
                        resolved_getattr = f"{target_obj}.{attr_val}"
                        if resolved_getattr in cls.FORBIDDEN_CALLS or attr_val in {"system", "popen", "rmtree"}:
                            violations.append(f"Forbidden Dynamic Call via getattr: '{resolved_getattr}'")

        dt_us = (time.perf_counter() - start_us) * 1_000_000

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

    @classmethod
    def _resolve_call_name(cls, func_node: ast.AST, aliases: Dict[str, str]) -> str:
        """Resolves function names through import alias mappings."""
        if isinstance(func_node, ast.Name):
            return aliases.get(func_node.id, func_node.id)
        elif isinstance(func_node, ast.Attribute):
            val_name = cls._resolve_call_name(func_node.value, aliases)
            if val_name:
                return f"{val_name}.{func_node.attr}"
            return func_node.attr
        return ""
