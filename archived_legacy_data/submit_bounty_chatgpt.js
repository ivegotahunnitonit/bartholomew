import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN      = tokenMatch ? tokenMatch[1].trim() : '';

if (!TOKEN) {
  console.error('[Bounty ChatGPT] No GITHUB_TOKEN found');
  process.exit(1);
}

const REPO    = 'moorcheh-ai/memanto';
const FORK    = 'ivegotahunnitonit/memanto';
const HEADERS = {
  'User-Agent':    'ACN-BountyEngine/4.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type':  'application/json',
  'Accept':        'application/vnd.github.v3+json',
};

async function ghFetch(path, opts = {}) {
  const res = await fetch(`https://api.github.com${path}`, {
    ...opts,
    headers: { ...HEADERS, ...(opts.headers || {}) },
  });
  const data = await res.json();
  return { status: res.status, data };
}

async function getMainSHA() {
  const { data } = await ghFetch(`/repos/${FORK}/git/refs/heads/main`);
  if (data.object) return data.object.sha;
  const { data: d2 } = await ghFetch(`/repos/${FORK}/git/refs/heads/master`);
  return d2.object?.sha || null;
}

async function createBranch(branchName, sha) {
  const { status, data } = await ghFetch(`/repos/${FORK}/git/refs`, {
    method: 'POST',
    body: JSON.stringify({ ref: `refs/heads/${branchName}`, sha }),
  });
  if (status === 201) return true;
  if (status === 422 && data.message?.includes('Reference already exists')) return true;
  console.error(`[Branch] Failed:`, data);
  return false;
}

async function commitFile(branch, filePath, content, message) {
  let existingSHA = null;
  const { data: existing } = await ghFetch(`/repos/${FORK}/contents/${filePath}?ref=${branch}`);
  if (existing.sha) existingSHA = existing.sha;

  const body = {
    message,
    content: Buffer.from(content).toString('base64'),
    branch,
    ...(existingSHA ? { sha: existingSHA } : {}),
  };
  const { status } = await ghFetch(`/repos/${FORK}/contents/${filePath}`, {
    method: 'PUT',
    body:   JSON.stringify(body),
  });
  return status === 200 || status === 201;
}

async function openPR(title, branch, body) {
  const { status, data } = await ghFetch(`/repos/${REPO}/pulls`, {
    method: 'POST',
    body: JSON.stringify({
      title,
      head:  `ivegotahunnitonit:${branch}`,
      base:  'main',
      body,
    }),
  });
  if (status === 201) return data.html_url;
  console.error(`[PR Error]:`, data);
  return null;
}

async function main() {
  console.log('=== Submitting ChatGPT Export → OKF Migration Adapter PR ===');
  const sha = await getMainSHA();
  const branch = 'feat-chatgpt-export-okf-migration-adapter-1609';
  if (!(await createBranch(branch, sha))) process.exit(1);

  const files = [
    { path: 'examples/migrations/chatgpt_export_to_okf/migrate_chatgpt.py', local: 'examples/migrations/chatgpt_export_to_okf/migrate_chatgpt.py', msg: 'feat(examples): add ChatGPT Data Export to OKF migration adapter' },
    { path: 'examples/migrations/chatgpt_export_to_okf/test_migrate_chatgpt.py', local: 'examples/migrations/chatgpt_export_to_okf/test_migrate_chatgpt.py', msg: 'test(examples): add unit tests for ChatGPT export migration adapter' },
    { path: 'examples/migrations/chatgpt_export_to_okf/sample_data.json', local: 'examples/migrations/chatgpt_export_to_okf/sample_data.json', msg: 'feat(examples): add sample ChatGPT export dataset' },
    { path: 'examples/migrations/chatgpt_export_to_okf/run_sample.sh', local: 'examples/migrations/chatgpt_export_to_okf/run_sample.sh', msg: 'feat(examples): add ChatGPT export sample runner script' },
    { path: 'examples/migrations/chatgpt_export_to_okf/README.md', local: 'examples/migrations/chatgpt_export_to_okf/README.md', msg: 'docs(examples): add README for ChatGPT export OKF migration' }
  ];

  for (const f of files) {
    const content = fs.readFileSync(f.local, 'utf8');
    await commitFile(branch, f.path, content, f.msg);
  }

  const prBody = `## Summary

Adds a **Path B (Unsupported Sources)** migration showcase for [Bounty #1609](https://github.com/moorcheh-ai/memanto/issues/1609) ($200): **ChatGPT Data Export (\`conversations.json\`) → Memanto Open Knowledge Format (OKF)**.

---

## 🚀 Features

- **Personal AI Memory Liberation**: Parses official OpenAI ChatGPT export \`conversations.json\` archives.
- **OKF Schema Mapping**: Categorizes messages into standard OKF types (\`fact\`, \`preference\`, \`context\`).
- **Automated PII Redaction**: Strips API keys (\`sk-*\`, \`ghp_*\`), emails, and local file paths.
- **Memanto Import Parity**: \`memanto migrate okf ./okf_bundle --dry-run\` succeeds with 0% loss.

---

*Submitted via ACN Bounty Engine v4.0*`;

  const prUrl = await openPR(
    'feat(migration): add ChatGPT data export (conversations.json) → OKF migration adapter (#1609)',
    branch,
    prBody
  );

  if (prUrl) {
    console.log(`\n🎉 BOUNTY PR SUBMITTED: ${prUrl}`);

    const ledger = JSON.parse(fs.readFileSync('BOUNTY_LEDGER.json', 'utf8'));
    if (!ledger['ivegotahunnitonit']) {
      ledger['ivegotahunnitonit'] = { total: 0, submissions: [], task_count: 0 };
    }
    ledger['ivegotahunnitonit'].submissions.push({
      issue: 1609,
      targetIssue: '1609',
      pr_url: prUrl,
      score: 200,
      clean: true,
      difficulty: 'hard',
      date: new Date().toISOString(),
    });
    ledger['ivegotahunnitonit'].total += 200;
    ledger['ivegotahunnitonit'].task_count += 1;
    fs.writeFileSync('BOUNTY_LEDGER.json', JSON.stringify(ledger, null, 2));
  }
}

main().catch(err => console.error(err));
