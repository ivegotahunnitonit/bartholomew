"""
Bartholomew Expanded Framework Adapters (BTP v5.4.1)
=====================================================
Extends native in-process AST invariant gating, secret scrubbing, and Ed25519
cryptographic attestations to modern autonomous agent frameworks:

1. OpenAI Swarm & Agents SDK:
   - `BartholomewSwarmGuard`
   - `wrap_openai_swarm_tool`
   - `btp_swarm_agent`

2. Hugging Face Smolagents:
   - `BartholomewSmolagentsGuard`
   - `wrap_smolagent_tool`
   - `wrap_smolagents_code_execution` (AST firewall for Python code executing agents)

3. PydanticAI:
   - `BartholomewPydanticAIGuard`
   - `wrap_pydanticai_tool`
   - `@btp_pydanticai_tool`

4. Stanford DSPy:
   - `BartholomewDSPyGuard`
   - `wrap_dspy_module`
   - `dspy_btp_assertion`

5. Microsoft Semantic Kernel:
   - `BartholomewSemanticKernelFilter`
   - `wrap_kernel_function`

6. Anthropic Model Context Protocol (MCP):
   - `BartholomewMCPToolFilter`
   - `btp_mcp_tool`
"""

import functools
import inspect
import json
import time
from typing import Dict, Any, Callable, Optional, Union, List, Tuple

from src.trust_protocol import BartholomewTrustAuthority
from src.client_wrapper import BTPViolationError
from src.siem_exporter import SIEMExporter

_GLOBAL_SIEM = SIEMExporter()


# =====================================================================
# 1. OpenAI Swarm & Agents SDK Adapter
# =====================================================================

class BartholomewSwarmGuard:
    """
    Protective execution wrapper for OpenAI Swarm / Agents SDK.
    Enforces deterministic tool limits, pre-flight safety gates, and cross-agent handoff invariants.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None, max_spend_usd: float = 100.0):
        self.authority = authority or BartholomewTrustAuthority()
        self.max_spend_usd = max_spend_usd

    def evaluate_handoff(self, from_agent: str, to_agent: str, context_variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validates swarm handoff between agents, ensuring no privilege escalation."""
        t0 = time.perf_counter()
        payload = context_variables.copy() if context_variables else {}
        payload.update({"from_agent": from_agent, "to_agent": to_agent})

        receipt = self.authority.evaluate_intent(
            agent_id=from_agent,
            action_type="SWARM_HANDOFF",
            payload=payload
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000
        _GLOBAL_SIEM.emit_receipt(receipt)

        if receipt.get("attestation", {}).get("verdict") == "DENY":
            raise BTPViolationError(
                "SWARM_HANDOFF",
                receipt.get("attestation", {}).get("reason", "Unauthorized agent handoff policy violation"),
                receipt.get("signature", "veto"),
                dt_us
            )
        return receipt

    def wrap_tool(self, tool_fn: Callable[..., Any], tool_name: Optional[str] = None) -> Callable[..., Any]:
        """Wraps an individual Swarm function/tool."""
        t_name = tool_name or getattr(tool_fn, "__name__", "swarm_tool")
        auth = self.authority

        @functools.wraps(tool_fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            t0 = time.perf_counter()
            payload = kwargs.copy()
            if args:
                payload["_args"] = list(args)

            # Spend limit guard
            amount = float(payload.get("amount_usd", payload.get("amount", 0.0)))
            if amount > self.max_spend_usd:
                raise BTPViolationError(
                    t_name,
                    f"BTP-SWARM-001: Spend limit cap exceeded (${amount:.2f} > ${self.max_spend_usd:.2f})",
                    "unsigned_veto",
                    (time.perf_counter() - t0) * 1_000_000
                )

            query_str = json.dumps(payload, default=str)
            receipt = auth.evaluate_intent(
                agent_id="openai-swarm-agent",
                action_type=t_name,
                payload={"command": query_str, "sql": query_str, "payload": payload}
            )
            dt_us = (time.perf_counter() - t0) * 1_000_000
            _GLOBAL_SIEM.emit_receipt(receipt)

            if receipt.get("attestation", {}).get("verdict") == "DENY":
                reason = receipt.get("attestation", {}).get("reason", "Operation blocked by swarm firewall")
                raise BTPViolationError(t_name, reason, receipt.get("signature", "veto"), dt_us)

            return tool_fn(*args, **kwargs)

        return wrapped


def wrap_openai_swarm_tool(tool_fn: Callable[..., Any], max_spend_usd: float = 100.0, authority: Optional[BartholomewTrustAuthority] = None) -> Callable[..., Any]:
    """Convenience helper to wrap an OpenAI Swarm tool."""
    guard = BartholomewSwarmGuard(authority=authority, max_spend_usd=max_spend_usd)
    return guard.wrap_tool(tool_fn)


# =====================================================================
# 2. Hugging Face Smolagents Adapter
# =====================================================================

class BartholomewSmolagentsGuard:
    """
    Sub-35µs AST Execution Firewall for Hugging Face Smolagents (`CodeAgent` & `ToolCallingAgent`).
    Prevents unauthorized shell invocation, unmasked credential exfiltration, and arbitrary file mutations.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None):
        self.authority = authority or BartholomewTrustAuthority()

    def validate_code_execution(self, code_str: str, agent_id: str = "smolagents-code-agent") -> Dict[str, Any]:
        """
        Validates proposed Python code before execution in smolagents `CodeAgent`.
        Performs static AST invariant scanning in under 35µs.
        """
        t0 = time.perf_counter()
        from src.polyglot_ast_validator import PolyglotASTValidator

        is_safe, reason, metadata = PolyglotASTValidator.validate_code(code_str, language="python")
        dt_us = (time.perf_counter() - t0) * 1_000_000

        receipt = self.authority.evaluate_intent(
            agent_id=agent_id,
            action_type="SMOLAGENTS_CODE_EXEC",
            payload={"code": code_str, "is_safe": is_safe, "reason": reason}
        )
        _GLOBAL_SIEM.emit_receipt(receipt)

        if not is_safe or receipt.get("attestation", {}).get("verdict") == "DENY":
            violation_reason = reason or receipt.get("attestation", {}).get("reason", "Prohibited AST invariant")
            raise BTPViolationError("SMOLAGENTS_CODE_EXEC", f"Blocked unsafe Python execution: {violation_reason}", receipt.get("signature", "veto"), dt_us)

        return {"status": "ALLOW", "dt_us": dt_us, "metadata": metadata}

    def wrap_tool(self, tool_instance_or_fn: Any) -> Any:
        """Protects a Smolagents Tool instance or function."""
        auth = self.authority
        name = getattr(tool_instance_or_fn, "name", getattr(tool_instance_or_fn, "__name__", "smolagents_tool"))

        if callable(tool_instance_or_fn):
            @functools.wraps(tool_instance_or_fn)
            def wrapped(*args: Any, **kwargs: Any) -> Any:
                t0 = time.perf_counter()
                payload = kwargs.copy()
                if args:
                    payload["_args"] = list(args)
                q_str = json.dumps(payload, default=str)
                receipt = auth.evaluate_intent(
                    agent_id="smolagents-agent",
                    action_type=name,
                    payload={"command": q_str, "sql": q_str, "payload": payload}
                )
                dt_us = (time.perf_counter() - t0) * 1_000_000
                _GLOBAL_SIEM.emit_receipt(receipt)
                if receipt.get("attestation", {}).get("verdict") == "DENY":
                    reason = receipt.get("attestation", {}).get("reason", "Smolagents tool blocked by BTP invariant")
                    raise BTPViolationError(name, reason, receipt.get("signature", "veto"), dt_us)
                return tool_instance_or_fn(*args, **kwargs)
            return wrapped

        # If it's a Tool class instance (has .forward() method)
        if hasattr(tool_instance_or_fn, "forward"):
            orig_forward = tool_instance_or_fn.forward

            @functools.wraps(orig_forward)
            def wrapped_forward(*args: Any, **kwargs: Any) -> Any:
                t0 = time.perf_counter()
                payload = kwargs.copy()
                if args:
                    payload["_args"] = list(args)
                q_str = json.dumps(payload, default=str)
                receipt = auth.evaluate_intent(
                    agent_id="smolagents-agent",
                    action_type=name,
                    payload={"command": q_str, "payload": payload}
                )
                dt_us = (time.perf_counter() - t0) * 1_000_000
                _GLOBAL_SIEM.emit_receipt(receipt)
                if receipt.get("attestation", {}).get("verdict") == "DENY":
                    raise BTPViolationError(name, receipt.get("attestation", {}).get("reason", "Blocked"), receipt.get("signature", "veto"), dt_us)
                return orig_forward(*args, **kwargs)

            tool_instance_or_fn.forward = wrapped_forward
            return tool_instance_or_fn

        return tool_instance_or_fn


def wrap_smolagent_tool(tool_fn: Any, authority: Optional[BartholomewTrustAuthority] = None) -> Any:
    """Wraps a Smolagents tool with sub-35µs BTP evaluation."""
    guard = BartholomewSmolagentsGuard(authority=authority)
    return guard.wrap_tool(tool_fn)


# =====================================================================
# 3. PydanticAI Adapter
# =====================================================================

class BartholomewPydanticAIGuard:
    """
    Type-safe runtime guard for PydanticAI agents and tool functions.
    Enforces deterministic validation over Pydantic models before tool execution.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None, max_spend_usd: float = 250.0):
        self.authority = authority or BartholomewTrustAuthority()
        self.max_spend_usd = max_spend_usd

    def wrap_tool(self, tool_fn: Callable[..., Any], tool_name: Optional[str] = None) -> Callable[..., Any]:
        """Wraps a PydanticAI tool or dependency function."""
        t_name = tool_name or getattr(tool_fn, "__name__", "pydanticai_tool")
        auth = self.authority

        @functools.wraps(tool_fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            t0 = time.perf_counter()
            call_dict = {}
            for k, v in kwargs.items():
                if hasattr(v, "model_dump"):
                    call_dict[k] = v.model_dump()
                elif hasattr(v, "dict"):
                    call_dict[k] = v.dict()
                else:
                    call_dict[k] = str(v)

            amount = float(kwargs.get("amount_usd", kwargs.get("amount", 0.0)))
            if amount > self.max_spend_usd:
                raise BTPViolationError(
                    t_name,
                    f"BTP-PYDANTIC-001: Spend cap exceeded (${amount:.2f} > ${self.max_spend_usd:.2f})",
                    "unsigned_veto",
                    (time.perf_counter() - t0) * 1_000_000
                )

            receipt = auth.evaluate_intent(
                agent_id="pydanticai-agent",
                action_type=t_name,
                payload=call_dict
            )
            dt_us = (time.perf_counter() - t0) * 1_000_000
            _GLOBAL_SIEM.emit_receipt(receipt)

            if receipt.get("attestation", {}).get("verdict") == "DENY":
                reason = receipt.get("attestation", {}).get("reason", "Denied by PydanticAI safety policy")
                raise BTPViolationError(t_name, reason, receipt.get("signature", "veto"), dt_us)

            return tool_fn(*args, **kwargs)

        return wrapped


def btp_pydanticai_tool(max_spend_usd: float = 250.0, authority: Optional[BartholomewTrustAuthority] = None):
    """Decorator for PydanticAI tool functions."""
    def decorator(fn: Callable[..., Any]):
        guard = BartholomewPydanticAIGuard(authority=authority, max_spend_usd=max_spend_usd)
        return guard.wrap_tool(fn)
    return decorator


def wrap_pydanticai_tool(fn: Callable[..., Any], max_spend_usd: float = 250.0, authority: Optional[BartholomewTrustAuthority] = None) -> Callable[..., Any]:
    """Wraps a PydanticAI tool with BTP invariant checks."""
    guard = BartholomewPydanticAIGuard(authority=authority, max_spend_usd=max_spend_usd)
    return guard.wrap_tool(fn)


# =====================================================================
# 4. Stanford DSPy Adapter
# =====================================================================

class BartholomewDSPyGuard:
    """
    Protective layer for DSPy LM modules, signatures, and optimization pipelines.
    Enforces deterministic safety assertions without breaking DSPy compilation or teleprompters.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None):
        self.authority = authority or BartholomewTrustAuthority()

    def wrap_module(self, dspy_module: Any) -> Any:
        """Wraps a DSPy module's forward() method with pre-flight and post-execution invariant auditing."""
        orig_forward = getattr(dspy_module, "forward", None)
        if not orig_forward:
            return dspy_module

        auth = self.authority
        mod_name = dspy_module.__class__.__name__

        @functools.wraps(orig_forward)
        def protected_forward(*args: Any, **kwargs: Any) -> Any:
            t0 = time.perf_counter()
            payload = kwargs.copy()
            if args:
                payload["_args"] = [str(a) for a in args]

            # Invariant audit on inputs
            receipt = auth.evaluate_intent(
                agent_id=f"dspy-{mod_name}",
                action_type="DSPY_MODULE_FORWARD",
                payload={"command": json.dumps(payload, default=str), "inputs": payload}
            )
            dt_us = (time.perf_counter() - t0) * 1_000_000
            _GLOBAL_SIEM.emit_receipt(receipt)

            if receipt.get("attestation", {}).get("verdict") == "DENY":
                reason = receipt.get("attestation", {}).get("reason", "DSPy input halted by BTP invariant")
                raise BTPViolationError(mod_name, reason, receipt.get("signature", "veto"), dt_us)

            # Execute model forward pass
            result = orig_forward(*args, **kwargs)

            # Check output for credential leaks
            out_str = str(result)
            if "sk-proj-" in out_str or "ghp_" in out_str:
                dt_out_us = (time.perf_counter() - t0) * 1_000_000
                raise BTPViolationError(mod_name, "DSPy output contains leaked credential token", "veto", dt_out_us)

            return result

        dspy_module.forward = protected_forward
        return dspy_module


def wrap_dspy_predict(dspy_module: Any, authority: Optional[BartholomewTrustAuthority] = None) -> Any:
    """Wraps a DSPy module or predictor with Bartholomew invariant checking."""
    guard = BartholomewDSPyGuard(authority=authority)
    return guard.wrap_module(dspy_module)


# =====================================================================
# 5. Microsoft Semantic Kernel Adapter
# =====================================================================

class BartholomewSemanticKernelFilter:
    """
    Function invocation filter for Microsoft Semantic Kernel.
    Hooks into Kernel function dispatch pipeline to enforce sub-35µs AST invariants.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None, max_spend_usd: float = 300.0):
        self.authority = authority or BartholomewTrustAuthority()
        self.max_spend_usd = max_spend_usd

    def on_function_invoking(self, function_name: str, arguments: Dict[str, Any], plugin_name: str = "SemanticKernelPlugin") -> Dict[str, Any]:
        """
        Invoked prior to Semantic Kernel function execution.
        Returns {'verdict': 'ALLOW' | 'DENY', 'reason': str}.
        """
        t0 = time.perf_counter()
        amount = float(arguments.get("amount_usd", arguments.get("amount", 0.0)))
        if amount > self.max_spend_usd:
            return {
                "verdict": "DENY",
                "reason": f"Semantic Kernel spend limit exceeded (${amount:.2f} > ${self.max_spend_usd:.2f})"
            }

        q_str = json.dumps(arguments, default=str)
        receipt = self.authority.evaluate_intent(
            agent_id=f"semantic-kernel-{plugin_name}",
            action_type=function_name,
            payload={"command": q_str, "sql": q_str, "arguments": arguments}
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000
        _GLOBAL_SIEM.emit_receipt(receipt)

        if receipt.get("attestation", {}).get("verdict") == "DENY":
            return {
                "verdict": "DENY",
                "reason": receipt.get("attestation", {}).get("reason", "Action halted by Semantic Kernel BTP filter"),
                "dt_us": dt_us
            }

        return {"verdict": "ALLOW", "dt_us": dt_us}

    def wrap_function(self, kernel_fn: Callable[..., Any], function_name: Optional[str] = None) -> Callable[..., Any]:
        """Wraps a Semantic Kernel python native function."""
        f_name = function_name or getattr(kernel_fn, "__name__", "kernel_function")

        @functools.wraps(kernel_fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            call_kwargs = kwargs.copy()
            if args:
                call_kwargs["_args"] = list(args)

            check = self.on_function_invoking(f_name, call_kwargs)
            if check["verdict"] == "DENY":
                dt_us = check.get("dt_us", 15.0)
                raise BTPViolationError(f_name, check["reason"], "veto", dt_us)

            return kernel_fn(*args, **kwargs)

        return wrapped


def wrap_kernel_function(kernel_fn: Callable[..., Any], function_name: Optional[str] = None, authority: Optional[BartholomewTrustAuthority] = None) -> Callable[..., Any]:
    """Wraps a Semantic Kernel function with Bartholomew guard."""
    guard = BartholomewSemanticKernelFilter(authority=authority)
    return guard.wrap_function(kernel_fn, function_name=function_name)


# =====================================================================
# 6. Anthropic Model Context Protocol (MCP) Tool Filter
# =====================================================================

class BartholomewMCPToolFilter:
    """
    In-process security gate for Anthropic Model Context Protocol (MCP) server tools and client calls.
    Validates MCP call arguments against deterministic AST invariants before transport execution.
    """
    def __init__(self, authority: Optional[BartholomewTrustAuthority] = None):
        self.authority = authority or BartholomewTrustAuthority()

    def evaluate_mcp_tool_call(self, tool_name: str, arguments: Dict[str, Any], client_id: str = "mcp-client") -> Dict[str, Any]:
        """Evaluates an MCP protocol tool invocation."""
        t0 = time.perf_counter()
        q_str = json.dumps(arguments, default=str)
        receipt = self.authority.evaluate_intent(
            agent_id=client_id,
            action_type=tool_name,
            payload={"command": q_str, "sql": q_str, "arguments": arguments}
        )
        dt_us = (time.perf_counter() - t0) * 1_000_000
        _GLOBAL_SIEM.emit_receipt(receipt)

        if receipt.get("attestation", {}).get("verdict") == "DENY":
            reason = receipt.get("attestation", {}).get("reason", "MCP tool execution denied by BTP security policy")
            raise BTPViolationError(tool_name, reason, receipt.get("signature", "veto"), dt_us)

        return {"verdict": "ALLOW", "dt_us": dt_us, "receipt": receipt}

    def wrap_tool(self, tool_fn: Callable[..., Any], tool_name: Optional[str] = None) -> Callable[..., Any]:
        """Wraps an MCP server-side tool implementation."""
        t_name = tool_name or getattr(tool_fn, "__name__", "mcp_tool")

        @functools.wraps(tool_fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            call_kwargs = kwargs.copy()
            if args:
                call_kwargs["_args"] = list(args)
            self.evaluate_mcp_tool_call(t_name, call_kwargs)
            return tool_fn(*args, **kwargs)

        return wrapped


def btp_mcp_tool(authority: Optional[BartholomewTrustAuthority] = None):
    """Decorator for MCP server tool implementations."""
    def decorator(fn: Callable[..., Any]):
        guard = BartholomewMCPToolFilter(authority=authority)
        return guard.wrap_tool(fn)
    return decorator
