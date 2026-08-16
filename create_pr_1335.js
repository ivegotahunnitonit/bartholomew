const token = 'YOUR_GITHUB_TOKEN_HERE';

async function run() {
  const prBody = {
    title: 'Fix: update_memory() overwrites original_id by dropping extra fields in formatting',
    head: 'ivegotahunnitonit:fix-original-id-1335',
    base: 'main',
    body: 'This PR resolves the issue where `update_memory()` overwrites extra metadata fields like `original_id` and `created_at` because `_format_memory_item` in `MemoryReadService` discards custom/non-schema fields when retrieving the record from Moorcheh.\n\nWe modified `_format_memory_item` to preserve all extra metadata fields by dynamically copying keys from `metadata` and `item` that do not conflict with standard schema keys.\n\nCloses #1335\nPart of Bug Challenge #770'
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
