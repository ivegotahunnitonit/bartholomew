const token = 'YOUR_GITHUB_TOKEN_HERE';

async function run() {
  const prBody = {
    title: 'Fix: Ambiguity Guard bypassed by common auxiliary verbs (is/are/was/were)',
    head: 'ivegotahunnitonit:fix-ambiguity-guard-1375',
    base: 'main',
    body: 'This PR resolves the issue where the `MemoryParsingService` ambiguity guard is bypassed for most English sentences due to standalone auxiliary verbs (`is`, `are`, `was`, `were`) being present in `STRONG_FACT_PATTERNS`.\n\nStandalone auxiliary verbs are too common and weak to bypass the ambiguity check. More specific structures are already mapped to correct confidence scores under classification rules.\n\nCloses #1375\nPart of Bug Challenge #770'
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
