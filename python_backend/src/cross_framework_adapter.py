"""
Bartholomew Universal Cross-Framework Adapter (BTP-InterOp v1.0)
Enables heterogeneous autonomous agent frameworks to exchange verifiable trust:
- LangChain / LangGraph (State Graph Agents)
- Microsoft AutoGen (Conversational Actor Agents)
- CrewAI (Role-Based Task Orchestrators)
- Raw OpenAI / Anthropic Tool-Calling Agents
"""

import sys
import os
import json
import time
from typing import Dict, Any, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.trust_protocol import BartholomewTrustAuthority, IndependentTrustVerifier

class CrossFrameworkTrustAdapter:
    """
    Standardizes disparate agent framework message formats into RFC 8785 Canonical BTP Receipts.
    """
    @staticmethod
    def from_langgraph(state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Translates LangGraph agent state into normalized BTP payload."""
        last_message = state_dict.get("messages", [{}])[-1]
        tool_call = last_message.get("tool_calls", [{}])[0] if "tool_calls" in last_message else {}
        return {
            "source_framework": "LangChain/LangGraph",
            "agent_node": state_dict.get("current_node", "agent"),
            "action_type": tool_call.get("name", "EXECUTE_TOOL"),
            "payload": tool_call.get("args", {})
        }

    @staticmethod
    def from_autogen(autogen_msg: Dict[str, Any]) -> Dict[str, Any]:
        """Translates Microsoft AutoGen conversation message into normalized BTP payload."""
        content = autogen_msg.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                content = {"raw_text": content}
        return {
            "source_framework": "Microsoft-AutoGen",
            "sender_agent": autogen_msg.get("sender", "assistant"),
            "recipient_agent": autogen_msg.get("recipient", "user_proxy"),
            "action_type": autogen_msg.get("action", "DELEGATE_TASK"),
            "payload": content
        }

    @staticmethod
    def from_crewai(task_output: Dict[str, Any]) -> Dict[str, Any]:
        """Translates CrewAI role-task execution output into normalized BTP payload."""
        return {
            "source_framework": "CrewAI",
            "role": task_output.get("agent_role", "Senior Developer"),
            "action_type": task_output.get("task_type", "CODE_PATCH"),
            "payload": task_output.get("result_data", {})
        }
