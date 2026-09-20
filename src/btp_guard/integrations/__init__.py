"""
Bartholomew Trust Protocol (BTP v1.0.0) - Framework Integrations
================================================================
First-class adapters for CrewAI, LangChain, LangGraph, and AutoGen.
"""

from .crewai import BtpCrewAIGuard
from .langchain import BtpCallbackHandler, BtpToolGuard
from .swarm import BtpSwarmGuard
from .pydanticai import BtpPydanticAIGuard
from .smolagents import BtpSmolagentsGuard

__all__ = [
    "BtpCrewAIGuard",
    "BtpCallbackHandler",
    "BtpToolGuard",
    "BtpSwarmGuard",
    "BtpPydanticAIGuard",
    "BtpSmolagentsGuard",
]
