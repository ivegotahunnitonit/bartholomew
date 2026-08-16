from typing import Any, Callable, Dict, List, Optional
from .engine import BartholomewEngine

class BartholomewFastAPIMiddleware:
    app: Any
    max_budget_tokens: int
    secret_scrubbing: bool
    auditor: BartholomewEngine

    def __init__(
        self,
        app: Any,
        max_budget_tokens: int = ...,
        secret_scrubbing: bool = ...,
        engine: Optional[BartholomewEngine] = ...,
    ) -> None: ...
    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None: ...

class BartholomewLangChainCallback:
    auditor: BartholomewEngine

    def __init__(self, engine: Optional[BartholomewEngine] = ...) -> None: ...
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None: ...
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None: ...
