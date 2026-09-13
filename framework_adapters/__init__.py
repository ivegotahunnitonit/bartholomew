"""
Bartholomew Trust Protocol (BTP v5.4.10) - Universal Execution Guards
Direct AST execution guards, secret scrubbing, and cryptographic receipts
for universal LLM providers (OpenAI, Anthropic, Gemini, DeepSeek, Ollama).
"""

import os

_sub_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bartholomew", "framework_adapters")
if os.path.isdir(_sub_path) and _sub_path not in __path__:
    __path__.append(_sub_path)

from src.universal_model_guard import UniversalBTPModelGuard, ModelProvider

__all__ = [
    "UniversalBTPModelGuard",
    "ModelProvider",
]
