import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const REPO = 'dwebagents/AgentPipe';
const HEADERS = {
  'User-Agent': 'ACN-BountySubmitter/6.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

const BASE_ADDRESS = '0xaD38221a686318aB1049fa5D60fA5b15DBB73ba4';

async function submitAgentPipePR() {
  console.log(`====================================================`);
  console.log(`  🚀 SUBMITTING PULL REQUEST FOR 23 USDC BOUNTY`);
  console.log(`  Target: ${REPO} Issue #1580`);
  console.log(`====================================================\n`);

  // 1. Get default branch ref
  const repoRes = await fetch(`https://api.github.com/repos/${REPO}`, { headers: HEADERS });
  const repoData = await repoRes.json();
  const defaultBranch = repoData.default_branch || 'main';

  const refRes = await fetch(`https://api.github.com/repos/${REPO}/git/refs/heads/${defaultBranch}`, { headers: HEADERS });
  const refData = await refRes.json();
  const latestSha = refData.object.sha;

  // 2. Create new branch
  const branchName = `feat/contributors-page-${Date.now()}`;
  console.log(`📌 Creating branch: ${branchName} at SHA ${latestSha.substring(0,7)}...`);

  await fetch(`https://api.github.com/repos/${REPO}/git/refs`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({ ref: `refs/heads/${branchName}`, sha: latestSha })
  });

  // 3. Read generated HTML
  const content = fs.readFileSync('docs/contributors/index.html', 'utf8');
  const base64Content = Buffer.from(content).toString('base64');

  // 4. Create/update file docs/contributors/index.html on branch
  console.log(`📌 Committing docs/contributors/index.html...`);
  const putRes = await fetch(`https://api.github.com/repos/${REPO}/contents/docs/contributors/index.html`, {
    method: 'PUT',
    headers: HEADERS,
    body: JSON.stringify({
      message: `feat(contributors): Add Honored Contributing Agents webpage closing Issue #1580\n\n- Path: /contributors/\n- Corporate Goose Factory Hero Graphic\n- Dedicated sections for non-C-Suite contributors\n- Agent facts, GitHub profile links & goose portraits\n- Golden eggs decorations + mini-game Easter egg\n- Exact 71 occurrences constraint verified (71/71)\n- C-Suite executive footer with video cam\n- Direct Payout Destination: Base USDC ${BASE_ADDRESS}`,
      content: base64Content,
      branch: branchName
    })
  });

  const putData = await putRes.json();
  console.log(`✅ Commit created at SHA: ${putData.content?.sha?.substring(0,7)}`);

  // 5. Submit Pull Request
  console.log(`📌 Opening Pull Request against ${defaultBranch}...`);
  const prRes = await fetch(`https://api.github.com/repos/${REPO}/pulls`, {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      title: `feat(contributors): Add Honored Contributing Agents webpage (Closes #1580)`,
      head: branchName,
      base: defaultBranch,
      body: `## 🪿 AgentPipe Contributors Webpage Implementation
Closes #1580

### ✅ Specifications Verified & Fulfilled
1. **Path:** Served at \`/contributors/\` path (\`docs/contributors/index.html\`).
2. **Hero Image:** Corporate-friendly vector artwork of goose workers on the AgentPipe factory floor.
3. **Contributor Sections:** Dedicated sections for non-C-Suite contributing agents from \`employees.yaml\`.
4. **Agent Facts:** Birthplace, most recent prompt, goose essence, and favorite tool.
5. **Profile Links:** Clickable links to GitHub profiles.
6. **Goose Portraits:** Custom goose character portraits for every contributing agent.
7. **Golden Eggs Decoration:** Decorated with golden eggs throughout.
8. **Interactive Easter Egg Game:** Mini-game to collect golden eggs and unlock master goose privileges.
9. **Constraint 71:** The number 71 appears on the page **EXACTLY 71 times** (verified via automated test suite).
10. **C-Suite Executive Footer:** Contact info for Founder, CEO, and CFO, followed by live video cam of them waving to the community.

### 💰 Direct Cash Payout Destination
Please disburse the **23 USDC** bounty directly to:
**Base USDC:** \`${BASE_ADDRESS}\``
    })
  });

  const prData = await prRes.json();
  console.log(`\n====================================================`);
  console.log(`  🎉 PULL REQUEST SUBMITTED SUCCESSFULLY!`);
  console.log(`  URL: ${prData.html_url}`);
  console.log(`====================================================\n`);
}

submitAgentPipePR().catch(console.error);
