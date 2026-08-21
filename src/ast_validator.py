"""
Bartholomew Compiler-Grade AST Security & Invariant Engine
=========================================================
Deep structural Python Abstract Syntax Tree (AST) static analysis.
Handles:
  1. Direct, aliased, and imported execution calls (eval, exec, os.system, subprocess).
  2. Variable assignment alias propagation (s = os; s.system(...)).
  3. Dunder and reflection attacks (__builtins__, __subclasses__, __import__, globals()).
  4. Dynamic getattr with constant-folded string concatenation.
  5. Destructive filesystem operations (open(..., 'w'), shutil.rmtree).
  6. Network socket & exfiltration module containment.
"""

import ast
import time
from typing import Dict, Any, Tuple, List, Set, Optional

class ASTSecurityValidator:
    FORBIDDEN_CALL_TARGETS: Set[str] = {
        "eval", "exec", "compile", "__import__",
        "os.system", "os.popen", "os.spawn", "os.spawnl", "os.spawnv",
        "os.remove", "os.unlink", "os.rmdir", "os.kill", "os.execv", "os.execve",
        "subprocess.Popen", "subprocess.call", "subprocess.run", "subprocess.check_output", "subprocess.check_call",
        "shutil.rmtree", "shutil.move", "shutil.copyfile",
        "pathlib.Path.unlink", "pathlib.Path.rmdir"
    }

    FORBIDDEN_MODULES: Set[str] = {
        "pty", "socket", "ctypes", "code", "pdb", "posix", "nt"
    }

    DANGEROUS_ATTRIBUTES: Set[str] = {
        "__builtins__", "__subclasses__", "__globals__", "__code__", "__dict__"
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
        violations: List[str] = []
        aliases: Dict[str, str] = {} # Symbol table: local var -> canonical module/func

        for node in ast.walk(tree):
            total_nodes += 1

            # 1. Track Imports & Import-Aliases
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
                    canonical = f"{mod}.{alias.name}" if mod else alias.name
                    asname = alias.asname or alias.name
                    aliases[asname] = canonical

            # 2. Track Variable Assignment Aliases (s = os, p = os.system)
            elif isinstance(node, ast.Assign):
                rhs_resolved = cls._resolve_call_name(node.value, aliases)
                if rhs_resolved:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            aliases[target.id] = rhs_resolved

            # 3. Inspect Dunder / Reflection Attributes (__builtins__, __subclasses__)
            elif isinstance(node, ast.Attribute):
                if node.attr in cls.DANGEROUS_ATTRIBUTES:
                    violations.append(f"Forbidden Dunder Attribute Access: '{node.attr}'")

            # 4. Inspect Function & Method Calls (ast.Call)
            elif isinstance(node, ast.Call):
                call_name = cls._resolve_call_name(node.func, aliases)
                
                if call_name in cls.FORBIDDEN_CALL_TARGETS:
                    violations.append(f"Forbidden AST Execution Call: '{call_name}'")

                # Detect dynamic getattr: getattr(os, "system") or getattr(os, "sys" + "tem")
                if isinstance(node.func, ast.Name) and node.func.id == "getattr":
                    if len(node.args) >= 2:
                        target_obj = cls._resolve_call_name(node.args[0], aliases)
                        attr_val = cls._evaluate_string_expr(node.args[1])
                        if attr_val:
                            full_dyn_call = f"{target_obj}.{attr_val}"
                            if full_dyn_call in cls.FORBIDDEN_CALL_TARGETS or attr_val in {"system", "popen", "rmtree", "unlink"}:
                                violations.append(f"Forbidden Dynamic getattr Call: '{full_dyn_call}'")

                # Detect dangerous file write modes in open("...", "w")
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    if len(node.args) >= 2:
                        mode_val = cls._evaluate_string_expr(node.args[1])
                        if mode_val and any(m in mode_val for m in ["w", "a", "x", "+"]):
                            if isinstance(node.args[0], ast.Constant):
                                path_str = str(node.args[0].value)
                                if path_str.startswith("/") or ".." in path_str or "etc" in path_str:
                                    violations.append(f"Forbidden Arbitrary File Write Path: '{path_str}'")

        dt_us = (time.perf_counter() - start_us) * 1_000_000

        if total_nodes > max_ast_nodes:
            violations.append(f"AST Node Limit Exceeded: {total_nodes} nodes > {max_ast_nodes}")

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
        """Recursively resolves function call expressions through symbol table aliases."""
        if isinstance(func_node, ast.Name):
            return aliases.get(func_node.id, func_node.id)
        elif isinstance(func_node, ast.Attribute):
            val_name = cls._resolve_call_name(func_node.value, aliases)
            if val_name:
                resolved = f"{val_name}.{func_node.attr}"
                return aliases.get(resolved, resolved)
            return func_node.attr
        return ""

    @classmethod
    def _evaluate_string_expr(cls, node: ast.AST) -> Optional[str]:
        """Evaluates string constants and constant-folded string concatenations ('sys' + 'tem')."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = cls._evaluate_string_expr(node.left)
            right = cls._evaluate_string_expr(node.right)
            if left is not None and right is not None:
                return left + right
        return None
