"""
Bartholomew Trust Protocol (BTP v4.1) — Framework Adapters
Drop-in AST execution guards, secret scrubbing, and cryptographic receipts
for AutoGen, CrewAI, LangGraph, and LlamaIndex.
"""

from .autogen import btp_autogen_guard, AutoGenBTPInterceptor, BTPViolationError as AutoGenBTPViolationError
from .crewai import btp_crewai_tool, CrewAIBTPTaskGuard, BTPViolationError as CrewAIBTPViolationError
from .langgraph import btp_langchain_tool, LangGraphBTPGuard, BTPViolationError as LangGraphBTPViolationError
from .llamaindex import btp_llamaindex_tool, BartholomewLlamaIndexTool, BTPViolationError as LlamaIndexBTPViolationError

__all__ = [
    "btp_autogen_guard",
    "AutoGenBTPInterceptor",
    "AutoGenBTPViolationError",
    "btp_crewai_tool",
    "CrewAIBTPTaskGuard",
    "CrewAIBTPViolationError",
    "btp_langchain_tool",
    "LangGraphBTPGuard",
    "LangGraphBTPViolationError",
    "btp_llamaindex_tool",
    "BartholomewLlamaIndexTool",
    "LlamaIndexBTPViolationError",
]
