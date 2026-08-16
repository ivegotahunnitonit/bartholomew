import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const HEADERS = {
  'User-Agent': 'ACN-ActionPublisher/1.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

async function createAndPublishRepo() {
  console.log(`====================================================`);
  console.log(`  🚀 PUBLISHING PUBLIC GITHUB ACTION REPOSITORY`);
  console.log(`====================================================\n`);

  const repoName = `acn-security-action`;

  // 1. Check or create public repository
  let repoData;
  console.log(`📌 Creating public repository: ${repoName}...`);
  const createRes = await fetch('https://api.github.com/user/repos', {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      name: repoName,
      description: 'Automated CI/CD security scanner for AI agent codebases. Detects unmasked API keys and credential leaks.',
      private: false,
      auto_init: true
    })
  });

  if (createRes.status === 201) {
    repoData = await createRes.json();
    console.log(`✅ Repository created: ${repoData.html_url}`);
  } else {
    // Fetch existing repo
    const userRes = await fetch('https://api.github.com/user', { headers: HEADERS });
    const userData = await userRes.json();
    const owner = userData.login;
    const getRes = await fetch(`https://api.github.com/repos/${owner}/${repoName}`, { headers: HEADERS });
    repoData = await getRes.json();
    console.log(`📌 Using existing repository: ${repoData.html_url}`);
  }

  const owner = repoData.owner.login;
  const branch = repoData.default_branch || 'main';

  // 2. Commit action.yml
  console.log(`📌 Committing action.yml...`);
  const actionContent = fs.readFileSync('github_action/action.yml', 'utf8');
  await fetch(`https://api.github.com/repos/${owner}/${repoName}/contents/action.yml`, {
    method: 'PUT',
    headers: HEADERS,
    body: JSON.stringify({
      message: 'feat: Add ACN Security Action composite definition',
      content: Buffer.from(actionContent).toString('base64'),
      branch: branch
    })
  });

  // 3. Commit README.md
  console.log(`📌 Committing README.md...`);
  const readmeContent = fs.readFileSync('github_action/README.md', 'utf8');
  await fetch(`https://api.github.com/repos/${owner}/${repoName}/contents/README.md`, {
    method: 'PUT',
    headers: HEADERS,
    body: JSON.stringify({
      message: 'docs: Add installation guide and usage instructions',
      content: Buffer.from(readmeContent).toString('base64'),
      branch: branch
    })
  });

  console.log(`\n====================================================`);
  console.log(`  🎉 GITHUB ACTION PUBLISHED SUCCESSFULLY!`);
  console.log(`  Live URL: ${repoData.html_url}`);
  console.log(`  Marketplace Action Reference: ${owner}/${repoName}@main`);
  console.log(`====================================================\n`);
}

createAndPublishRepo().catch(console.error);
