import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const HEADERS = {
  'User-Agent': 'ACN-RealProfitHunter/5.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

async function ghFetch(path, opts = {}) {
  const res = await fetch(`https://api.github.com${path}`, {
    ...opts,
    headers: { ...HEADERS, ...(opts.headers || {}) },
  });
  const data = await res.json();
  return { status: res.status, data };
}

async function submitPR() {
  const TARGET_REPO = 'iii123iii/Crystal-PDF';
  const FORK_REPO   = 'ivegotahunnitonit/Crystal-PDF';
  const FILE_PATH   = 'frontend/src/pages/LandingPage.tsx';
  const BRANCH      = 'fix/mobile-responsive-landing';

  console.log(`[Crystal-PDF $100 Bounty] Starting submission...`);

  // 1. Get default branch SHA of fork
  const { data: refData } = await ghFetch(`/repos/${FORK_REPO}/git/refs/heads/main`);
  const mainSha = refData.object?.sha;
  if (!mainSha) {
    console.error('Failed to get main SHA for fork:', refData);
    return;
  }

  // 2. Create branch on fork
  const { status: bStatus, data: bData } = await ghFetch(`/repos/${FORK_REPO}/git/refs`, {
    method: 'POST',
    body: JSON.stringify({ ref: `refs/heads/${BRANCH}`, sha: mainSha })
  });
  console.log(`[Branch] Created/checked ${BRANCH}:`, bStatus);

  // 3. Get existing file SHA on branch
  const { data: fileMeta } = await ghFetch(`/repos/${FORK_REPO}/contents/${FILE_PATH}?ref=${BRANCH}`);
  const fileSha = fileMeta.sha;

  // 4. Update file on fork branch
  const newContent = fs.readFileSync('LandingPage.tsx', 'utf8');
  const { status: cStatus, data: cData } = await ghFetch(`/repos/${FORK_REPO}/contents/${FILE_PATH}`, {
    method: 'PUT',
    body: JSON.stringify({
      message: 'fix(responsive): make landing page 100% mobile-responsive across all viewports (Closes #3)',
      content: Buffer.from(newContent).toString('base64'),
      branch: BRANCH,
      ...(fileSha ? { sha: fileSha } : {})
    })
  });
  console.log(`[Commit] Updated ${FILE_PATH}:`, cStatus);

  // 5. Create Pull Request on target repo
  const prBody = `## Mobile Responsiveness Fix ($100 USD Bounty)

Closes #3

### 📱 Summary of Improvements

1. **Responsive Grid Layouts:** Changed fixed \`grid-cols-2\` tool grid to fluid \`grid-cols-1 xs:grid-cols-2 md:grid-cols-4\` to prevent card content overflow on mobile viewports (<380px).
2. **Mobile Typography & Padding:** Added \`clamp()\` font scaling for headings, dynamic section padding (\`py-16 sm:py-24 md:py-32\`), and responsive horizontal margins (\`px-4 sm:px-6\`).
3. **Touch-Optimized Navigation & Buttons:**
   - Sign in / Get Started navigation buttons auto-scale gracefully on mobile screens without wrapping awkwardly.
   - Hero and CTA action buttons scale to full width (\`w-full sm:w-auto\`) on mobile for effortless thumb tap targets.
4. **Adaptive Prism Graphic:** Made crystal prism graphic fluid (\`clamp(240px, 75vw, 340px)\`) and centered cleanly across all device orientations.
5. **Fluid Footer:** Re-aligned footer text and status badge into responsive column/row layouts (\`flex-col sm:flex-row text-center sm:text-left\`).

---

### 🧪 Tested Viewports
- [x] iPhone SE / 13 / 14 / 15 Pro (375px - 430px)
- [x] iPad Mini & Air / Tablet portrait (768px)
- [x] Desktop / Ultrawide (>1280px)
`;

  const { status: prStatus, data: prData } = await ghFetch(`/repos/${TARGET_REPO}/pulls`, {
    method: 'POST',
    body: JSON.stringify({
      title: 'fix(responsive): make landing page 100% mobile-responsive across all viewports ($100 USD bounty)',
      head: 'ivegotahunnitonit:' + BRANCH,
      base: 'main',
      body: prBody
    })
  });

  console.log(`[Pull Request] Status ${prStatus}:`, prData.html_url || prData);
}

submitPR().catch(console.error);
