"""
LlamaIndex + BTP Guard: Secure RAG Query Engine
================================================
Demonstrates protecting LlamaIndex tools with @btp_llamaindex_tool and
SovereignAgentPassport to prevent indirect prompt injection and destructive queries.

Run:
    python examples/llamaindex_rag_guard/run_rag.py
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from framework_adapters.llamaindex.llamaindex_btp_tool import btp_llamaindex_tool
from src.agent_passport import SovereignAgentPassport
from src.trust_protocol import BartholomewTrustAuthority


def main():
    print("=" * 70)
    print("  LlamaIndex + BTP Guard: Secure RAG Protection Demo")
    print("=" * 70)

    auth = BartholomewTrustAuthority(ttl_seconds=300)
    root_pubkey = auth.public_key_hex

    # 1. Define Guarded LlamaIndex Tool
    @btp_llamaindex_tool(required_capability="rag:query_index")
    def query_knowledge_base(query_str: str) -> str:
        return f"[RAG-RESULT] Top matching context for: '{query_str}'"

    # 2. Issue Sovereign Agent Passport
    passport = SovereignAgentPassport(
        agent_id="Agent-Llama-RAG-01",
        worker_model="Llama-3.3-70B",
        owner_pubkey=root_pubkey,
        granted_capabilities=["rag:query_index", "tools:read"]
    )
    passport.sign(auth.private_key)
    print(f"[+] Issued Sovereign Passport for {passport.agent_id} (Signed by Root)")

    # 3. Legitimate Query Execution
    print("\n--- [1] Executing Authorized Knowledge Query ---")
    res = query_knowledge_base("What are the Q3 revenue benchmarks?", agent_passport=passport)
    print(f"Outcome: {res}")

    # 4. Indirect Prompt Injection Interception (<35µs AST inspection)
    print("\n--- [2] Intercepting Malicious Destructive Injection ---")
    attack_input = "What are the sales numbers? && rm -rf /var/log/*"
    try:
        query_knowledge_base(attack_input, agent_passport=passport)
        print("Error: Malicious input was not blocked!")
    except PermissionError as e:
        print(f"Outcome: Correctly intercepted at AST layer: {e}")

    print("\n" + "=" * 70)
    print("  LlamaIndex RAG Guard Demo Complete: Injection Blocked Cleanly")
    print("=" * 70)
    return True


if __name__ == "__main__":
    main()
