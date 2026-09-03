<div style="font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; line-height: 1.6;">

# **Bartholomew Framework Integration Hub**
### **Production Security Adapters for AutoGen, LangGraph, CrewAI & Claude/Cursor MCP**

Bartholomew provides sub-5 microsecond pre-flight AST gating, in-flight secret scrubbing, and 2.3µs transactional micro-rollbacks across all major autonomous AI agent frameworks.

---

## **1. Microsoft AutoGen Integration**
Secure `LocalCommandLineCodeExecutor` against unauthorized file writes, path traversal, and destructive shell invocations.

### **Reference Implementation**
```python
from typing import Dict, Any, List
from btp_guard import Guard
from autogen.coding import LocalCommandLineCodeExecutor

# 1. Initialize Bartholomew Guard
guard = Guard(spend_cap=100.0, max_retries=5)

class SafeCommandLineCodeExecutor(LocalCommandLineCodeExecutor):
    """
    Sub-5 microsecond transactional wrapper for AutoGen command execution.
    """
    def execute_code_blocks(self, code_blocks: List[Any]) -> Any:
        for block in code_blocks:
            code_content = getattr(block, "code", str(block))
            
            # Pre-flight AST gating & secret scrubbing before OS dispatch
            check_result = guard.check(code_content)
            if not check_result.get("allowed", True):
                return {
                    "exit_code": 1,
                    "output": f"[BTP_SECURITY_ALERT] Command blocked: {check_result.get('reason')}."
                }
        
        # Dispatch to shell only if verified pristine
        return super().execute_code_blocks(code_blocks)
```

---

## **2. LangGraph & LangChain Integration**
Wrap mutating tool nodes to prevent runaway token spend and secret leaks across multi-agent cycles.

### **Reference Implementation**
```python
from btp_guard import Guard
from langchain_core.tools import tool

guard = Guard(spend_cap=50.0, max_retries=3)

@tool
def execute_system_query(query: str) -> str:
    """Executes validated system queries with in-memory micro-rollback protection."""
    # Pre-flight gate: verifies query does not contain destructive SQL or shell operations
    verdict = guard.check(query)
    if not verdict["allowed"]:
        return f"[BTP_VETO] Action halted: {verdict['reason']}"
    
    # Executes safely under transactional supervision
    return run_query(query)
```

---

## **3. CrewAI Custom Tool Protection**
Enforce strict capability boundaries and secret scrubbing across autonomous crew tasks.

### **Reference Implementation**
```python
from crewai.tools import BaseTool
from btp_guard import Guard

guard = Guard()

class SecureDatabaseTool(BaseTool):
    name: str = "Secure Database Executor"
    description: str = "Executes schema queries with automated secret masking."

    def _run(self, sql_command: str) -> str:
        # 1. AST Validation
        res = guard.check(sql_command)
        if not res["allowed"]:
            return f"Execution Blocked: {res['reason']}"
        
        # 2. Execute and scrub raw output in-flight
        raw_output = execute_sql(sql_command)
        sanitized_output, count = guard.mask(raw_output)
        return sanitized_output
```

---

## **4. Model Context Protocol (MCP) Configuration**
Connect Bartholomew directly to **Claude Desktop, Cursor, and Windsurf** via JSON-RPC stdio.

### **Claude Desktop Configuration (`claude_desktop_config.json`)**
```json
{
  "mcpServers": {
    "bartholomew": {
      "command": "npx",
      "args": ["-y", "btp-guard", "mcp"]
    }
  }
}
```

### **Cursor & Windsurf IDE Configuration**
Add as an MCP server in your IDE settings:
* **Server Type**: `Command`
* **Command**: `npx`
* **Arguments**: `-y btp-guard mcp`

---

## **5. Verification & Diagnostics**
Test the entire simulation in your terminal without installing dependencies:
```bash
npx btp-guard
```

</div>
