const token = 'YOUR_GITHUB_TOKEN_HERE';

async function run() {
  const res = await fetch('https://api.github.com/repos/moorcheh-ai/memanto/forks', {
    method: 'POST',
    headers: {
      'Authorization': `token ${token}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Antigravity-Agent'
    }
  });
  if (res.ok) {
    const data = await res.json();
    console.log('Fork created successfully:', data.html_url);
  } else {
    const text = await res.text();
    console.error('Failed to create fork:', res.status, text);
  }
}

run();
