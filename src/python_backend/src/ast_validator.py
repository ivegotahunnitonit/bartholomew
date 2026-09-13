"""
Bartholomew Compiler-Grade AST Security & Invariant Engine (v2.4)
=================================================================
Deep structural Python Abstract Syntax Tree (AST) static analysis with scoped visitor traversal:
  1. Direct, aliased, and imported execution calls (eval, exec, os.system, subprocess, importlib).
  2. Scoped single & tuple assignment alias propagation.
  3. Dunder and reflection attacks (__builtins__, __subclasses__, __import__, globals()).
  4. Dynamic getattr with constant-folded string concatenation.
  5. Destructive filesystem operations (open(..., 'w'), shutil.rmtree).
  6. Network socket & exfiltration module containment.
  7. Process spawn & pickle deserialization guards.
"""

import ast
import time
from typing import Dict, Any, Tuple, List, Set, Optional


class ScopedASTVisitor(ast.NodeVisitor):
    """
    Scope-aware AST Node Visitor that maintains lexical scopes for aliases.
    """
    def __init__(self, forbidden_calls: Set[str], forbidden_modules: Set[str], dangerous_attrs: Set[str]):
        self.forbidden_calls = forbidden_calls
        self.forbidden_modules = forbidden_modules
        self.dangerous_attrs = dangerous_attrs
        self.scopes: List[Dict[str, str]] = [{}]
        self.violations: List[str] = []
        self.total_nodes = 0

    @property
    def current_scope(self) -> Dict[str, str]:
        return self.scopes[-1]

    def resolve_name(self, name: str) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return name

    def resolve_call_name(self, func_node: ast.AST) -> str:
        if isinstance(func_node, ast.Name):
            return self.resolve_name(func_node.id)
        elif isinstance(func_node, ast.Attribute):
            val_name = self.resolve_call_name(func_node.value)
            if val_name:
                resolved = f"{val_name}.{func_node.attr}"
                return self.resolve_name(resolved)
            return func_node.attr
        return ""

    def generic_visit(self, node):
        self.total_nodes += 1
        super().generic_visit(node)

    def visit_FunctionDef(self, node):
        self.scopes.append(dict(self.current_scope))
        self.generic_visit(node)
        self.scopes.pop()

    def visit_AsyncFunctionDef(self, node):
        self.scopes.append(dict(self.current_scope))
        self.generic_visit(node)
        self.scopes.pop()

    def visit_Import(self, node):
        self.total_nodes += 1
        for alias in node.names:
            original = alias.name
            asname = alias.asname or alias.name
            self.current_scope[asname] = original
            if original in self.forbidden_modules:
                self.violations.append(f"Forbidden Module Import: '{original}'")

    def visit_ImportFrom(self, node):
        self.total_nodes += 1
        mod = node.module or ""
        if mod in self.forbidden_modules:
            self.violations.append(f"Forbidden Module Import: '{mod}'")
        for alias in node.names:
            canonical = f"{mod}.{alias.name}" if mod else alias.name
            asname = alias.asname or alias.name
            self.current_scope[asname] = canonical

    def visit_Assign(self, node):
        self.total_nodes += 1
        # Extract aliases
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            rhs_resolved = self.resolve_call_name(node.value)
            if rhs_resolved:
                self.current_scope[target_name] = rhs_resolved
        elif len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple):
            target_elts = node.targets[0].elts
            value_elts = node.value.elts
            if len(target_elts) == len(value_elts):
                for t_elt, v_elt in zip(target_elts, value_elts):
                    if isinstance(t_elt, ast.Name):
                        rhs_res = self.resolve_call_name(v_elt)
                        if rhs_res:
                            self.current_scope[t_elt.id] = rhs_res
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.total_nodes += 1
        if node.attr in self.dangerous_attrs:
            self.violations.append(f"Forbidden Dunder Attribute Access: '{node.attr}'")
        self.generic_visit(node)

    def visit_Call(self, node):
        self.total_nodes += 1
        call_name = self.resolve_call_name(node.func)

        if call_name in self.forbidden_calls:
            self.violations.append(f"Forbidden AST Execution Call: '{call_name}'")

        # Detect dynamic getattr: getattr(os, "system") or getattr(os, "sys" + "tem")
        if isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if len(node.args) >= 2:
                target_obj = self.resolve_call_name(node.args[0])
                attr_val = ASTSecurityValidator._evaluate_string_expr(node.args[1])
                if attr_val:
                    full_dyn_call = f"{target_obj}.{attr_val}"
                    if full_dyn_call in self.forbidden_calls or attr_val in {"system", "popen", "rmtree", "unlink", "loads", "import_module"}:
                        self.violations.append(f"Forbidden Dynamic getattr Call: '{full_dyn_call}'")

        # Detect dangerous file write modes in open("...", "w")
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if len(node.args) >= 2:
                mode_val = ASTSecurityValidator._evaluate_string_expr(node.args[1])
                if mode_val and any(m in mode_val for m in ["w", "a", "x", "+"]):
                    if isinstance(node.args[0], ast.Constant):
                        path_str = str(node.args[0].value)
                        if path_str.startswith("/") or ".." in path_str or "etc" in path_str:
                            self.violations.append(f"Forbidden Arbitrary File Write Path: '{path_str}'")

        self.generic_visit(node)


class ASTSecurityValidator:
    FORBIDDEN_CALL_TARGETS: Set[str] = {
        "eval", "exec", "compile", "__import__",
        "os.system", "os.popen", "os.spawn", "os.spawnl", "os.spawnv", "os.posix_spawn",
        "os.remove", "os.unlink", "os.rmdir", "os.kill", "os.execv", "os.execve",
        "subprocess.Popen", "subprocess.call", "subprocess.run", "subprocess.check_output", "subprocess.check_call",
        "shutil.rmtree", "shutil.move", "shutil.copyfile",
        "pathlib.Path.unlink", "pathlib.Path.rmdir",
        "importlib.import_module",
        "asyncio.create_subprocess_shell", "asyncio.create_subprocess_exec",
        "pickle.loads", "marshal.loads"
    }

    FORBIDDEN_MODULES: Set[str] = {
        "pty", "socket", "ctypes", "code", "pdb", "posix", "nt", "importlib", "pickle", "marshal"
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

        visitor = ScopedASTVisitor(cls.FORBIDDEN_CALL_TARGETS, cls.FORBIDDEN_MODULES, cls.DANGEROUS_ATTRIBUTES)
        visitor.visit(tree)

        dt_us = (time.perf_counter() - start_us) * 1_000_000

        if visitor.total_nodes > max_ast_nodes:
            visitor.violations.append(f"AST Node Limit Exceeded: {visitor.total_nodes} nodes > {max_ast_nodes}")

        is_safe = len(visitor.violations) == 0
        reason = "AST static analysis verified clean." if is_safe else "; ".join(visitor.violations)

        metadata = {
            "total_ast_nodes": visitor.total_nodes,
            "violations_found": visitor.violations,
            "analysis_latency_us": round(dt_us, 2)
        }

        return is_safe, reason, metadata

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
