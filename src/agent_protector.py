"""
Bartholomew Universal Agent Protector (BTP v5.4.20)
===================================================
1-line universal in-process security gateway for autonomous AI agents.
Protects LangGraph, CrewAI, AutoGen, OpenAI Agents, Claude Code, and LlamaIndex.

Usage:
    from btp_guard import protect_agent

    # 1 line protects ANY agent instance
    agent = protect_agent(agent)
"""

import functools
from typing import Any, Optional, List, Dict


def protect_agent(agent: Any, spend_cap: float = 50.0, strict: bool = True, guard: Optional[Any] = None) -> Any:
    """Wraps ANY agent instance, swarm, runnable, or tool executor with Bartholomew protection."""
    if guard is None:
        try:
            from btp_guard import Guard
            guard = Guard(spend_cap=spend_cap, strict=strict)
        except Exception:
            from src import Guard
            guard = Guard(spend_cap=spend_cap, strict=strict)

    # 1. Protect tools list if present (LangChain, CrewAI, AutoGen)
    if hasattr(agent, "tools") and isinstance(agent.tools, list):
        wrapped_tools = []
        for tool in agent.tools:
            if callable(tool):
                wrapped_tools.append(guard.protect(tool))
            elif hasattr(tool, "func") and callable(tool.func):
                tool.func = guard.protect(tool.func)
                wrapped_tools.append(tool)
            elif hasattr(tool, "invoke") and callable(tool.invoke):
                orig_invoke = tool.invoke
                def make_tool_wrapper(inv):
                    def tw(*args, **kwargs):
                        arg_str = " ".join(str(a) for a in args if isinstance(a, str))
                        chk = guard.check(arg_str)
                        if not chk.get("allowed", True):
                            raise PermissionError(f"[BTP-VETO] Action blocked: {chk.get('reason', 'Invariant policy violation')}")
                        return inv(*args, **kwargs)
                    return tw
                tool.invoke = make_tool_wrapper(orig_invoke)
                wrapped_tools.append(tool)
            else:
                wrapped_tools.append(tool)
        agent.tools = wrapped_tools

    # 2. Intercept primary execution methods (invoke, run, execute_task, step, generate_reply)
    methods_to_wrap = ["invoke", "run", "execute_task", "step", "generate_reply", "chat"]
    for method_name in methods_to_wrap:
        if hasattr(agent, method_name) and callable(getattr(agent, method_name)):
            original_method = getattr(agent, method_name)

            def make_method_wrapper(orig_fn, m_name):
                @functools.wraps(orig_fn)
                def wrapped_method(*args, **kwargs):
                    # Pre-flight input scrub & inspection
                    scrubbed_args = []
                    for arg in args:
                        if isinstance(arg, str):
                            # Scrub secrets in prompt
                            clean_str = guard.scrub(arg)
                            # Check destructive invariants
                            chk = guard.check(clean_str)
                            if not chk.get("allowed", True):
                                veto_msg = f"[BLOCKED BY BARTHOLOMEW] {chk.get('reason', 'Policy violation')} (Receipt: {chk.get('receipt_sha256', 'N/A')[:16]}...)"
                                if m_name in ["generate_reply", "chat", "run"]:
                                    return veto_msg
                                else:
                                    raise PermissionError(veto_msg)
                            scrubbed_args.append(clean_str)
                        else:
                            scrubbed_args.append(arg)

                    result = orig_fn(*scrubbed_args, **kwargs)

                    # Post-flight output secret redaction
                    if isinstance(result, str):
                        result = guard.scrub(result)
                    elif isinstance(result, dict) and "output" in result and isinstance(result["output"], str):
                        result["output"] = guard.scrub(result["output"])

                    return result
                return wrapped_method

            setattr(agent, method_name, make_method_wrapper(original_method, method_name))

    # 2.5 If agent is directly a callable function/lambda/class
    if callable(agent) and not any(hasattr(agent, m) for m in ["invoke", "step", "execute_task"]):
        orig_callable = agent
        @functools.wraps(orig_callable)
        def wrapped_callable(*args, **kwargs):
            scrubbed_args = []
            for arg in args:
                if isinstance(arg, str):
                    clean_str = guard.scrub(arg)
                    chk = guard.check(clean_str)
                    if not chk.get("allowed", True):
                        veto_msg = f"[BLOCKED BY BARTHOLOMEW] {chk.get('reason', 'Policy violation')} (Receipt: {chk.get('receipt_sha256', 'N/A')[:16]}...)"
                        if not strict:
                            return veto_msg
                        else:
                            return veto_msg
                    scrubbed_args.append(clean_str)
                else:
                    scrubbed_args.append(arg)
            res = orig_callable(*scrubbed_args, **kwargs)
            if isinstance(res, str):
                res = guard.scrub(res)
            return res
        wrapped_callable.btp_guard = guard
        wrapped_callable.is_btp_protected = True
        wrapped_callable.get_audit_receipts = lambda: getattr(guard.gate, "receipts", [])
        return wrapped_callable

    # 3. Attach metadata
    agent.btp_guard = guard
    agent.is_btp_protected = True
    agent.get_audit_receipts = lambda: getattr(guard.gate, "receipts", [])

    return agent
