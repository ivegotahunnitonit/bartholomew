# Bartholomew Guard for LangChain & LangGraph

> Sub-50 µs in-memory AST invariant gate and cryptographic attestation handler for LangChain and LangGraph agent swarms.

##  Installation

```bash
pip install btp-guard
```

##  Usage

### 1. LangGraph Node Integration (2 Lines)
```python
from btp_guard import LangGraphBTPGuard
from langgraph.graph import StateGraph

# Wrap your existing agent execution node
workflow.add_node("agent_executor", LangGraphBTPGuard(my_existing_agent_function))
```

### 2. LangChain Callback Handler
```python
from integrations.langchain.bartholomew_guard import BartholomewCallbackHandler
from langchain.agents import initialize_agent

handler = BartholomewCallbackHandler(spend_cap_usd=250.0)
agent = initialize_agent(tools, llm, callbacks=[handler])
```

### 3. Individual Tool Decorator
```python
from integrations.langchain.bartholomew_guard import BartholomewToolGuard

@BartholomewToolGuard(spend_cap_usd=100.0)
def execute_sql(query: str):
    # Automatically drops DROP TABLE / schema corruption in <50 µs
    return db.execute(query)
```
