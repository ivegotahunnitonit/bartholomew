from typing import Any, Callable, Dict, Optional, TypeVar
from .engine import BartholomewEngine

F = TypeVar("F", bound=Callable[..., Any])

class GuardViolation(Exception):
    audit_summary: Dict[str, Any]
    def __init__(self, message: str, audit_summary: Optional[Dict[str, Any]] = ...) -> None: ...

def guard(
    max_budget_tokens: int = ...,
    secret_scrubbing: bool = ...,
    enforce_loop_guard: bool = ...,
    agent_name: Optional[str] = ...,
    engine: Optional[BartholomewEngine] = ...,
) -> Callable[[F], F]: ...
