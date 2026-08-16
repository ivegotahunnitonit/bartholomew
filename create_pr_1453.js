const token = 'YOUR_GITHUB_TOKEN_HERE';

async function run() {
  const prBody = {
    title: 'Fix: agent creation limit conflict swallowing and standardize endpoint exception mapping',
    head: 'ivegotahunnitonit:fix-agent-creation-1453',
    base: 'main',
    body: 'This PR resolves the issues where:\n1. Agent creation plan-limit conflicts are silently swallowed and return HTTP 201/200 because of overly broad substring matching (`"conflict"`).\n2. General exceptions raised during agent management endpoints escape FastAPI and leak internal SDK paths.\n\nWe modified:\n- `create_agent` in `agent_service.py` to narrow the exception matching and raise `AgentError` with clean, path-free messages.\n- `sessions.py` to wrap agent lifecycle and status route endpoints in try/except blocks mapping exceptions via `map_error_to_http_exception`.\n- `errors.py` to explicitly handle `AgentError` in `map_error_to_http_exception`.\n\nCloses #1453\nPart of Bug Challenge #770'
  };

  const res = await fetch('https://api.github.com/repos/moorcheh-ai/memanto/pulls', {
    method: 'POST',
    headers: {
      'Authorization': `token ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Antigravity-Agent',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(prBody)
  });

  if (res.ok) {
    const data = await res.json();
    console.log('PR created successfully:', data.html_url);
  } else {
    const text = await res.text();
    console.error('Failed to create PR:', res.status, text);
  }
}

run();
