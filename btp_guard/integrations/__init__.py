"""
Bartholomew Trust Protocol (BTP v5.4.19) - Framework Integrations
================================================================
First-class adapters for LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex,
PydanticAI, Smolagents, and OpenAI Swarm.
"""

from .crewai import BtpCrewAIGuard
from .langchain import BtpCallbackHandler, BtpToolGuard
from .swarm import BtpSwarmGuard
from .pydanticai import BtpPydanticAIGuard
from .smolagents import BtpSmolagentsGuard
from .langgraph import LangGraphBTPGuard, btp_langchain_tool
from .autogen import AutoGenBTPInterceptor, btp_autogen_guard
from .llamaindex import LlamaIndexBTPToolGuard, btp_llamaindex_tool

from . import crewai
from . import langchain
from . import langgraph
from . import autogen
from . import llamaindex
from . import pydanticai
from . import smolagents
from . import swarm

__all__ = [
    "BtpCrewAIGuard",
    "BtpCallbackHandler",
    "BtpToolGuard",
    "BtpSwarmGuard",
    "BtpPydanticAIGuard",
    "BtpSmolagentsGuard",
    "LangGraphBTPGuard",
    "btp_langchain_tool",
    "AutoGenBTPInterceptor",
    "btp_autogen_guard",
    "LlamaIndexBTPToolGuard",
    "btp_llamaindex_tool",
    "crewai",
    "langchain",
    "langgraph",
    "autogen",
    "llamaindex",
    "pydanticai",
    "smolagents",
    "swarm",
]
