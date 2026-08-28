# Bartholomew Security Guard for CrewAI

> Zero-escape AST invariant checking, recursive loop dampening (LDMU), and secret vault scrubbing for CrewAI multi-agent swarms.

## 🚀 Installation

```bash
pip install btp-guard
```

## 🛠️ Usage

```python
from crewai import Agent, Task, Crew
from integrations.crewai.bartholomew_tool_guard import BartholomewCrewAIGuard

# Wrap any CrewAI tool with zero-escape AST protection
guarded_tool = BartholomewCrewAIGuard(tool=my_custom_tool, max_retries=5)

agent = Agent(
    role="Senior Backend Engineer",
    goal="Safely refactor legacy services without destructive commands",
    tools=[guarded_tool]
)
```
