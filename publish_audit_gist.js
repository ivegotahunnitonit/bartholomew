import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const HEADERS = {
  'User-Agent': 'ACN-GistPublisher/1.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

async function publishGist() {
  console.log(`====================================================`);
  console.log(`  🌐 PUBLISHING PUBLIC GIST FOR AGENT AUDIT REPORT`);
  console.log(`====================================================\n`);

  const reportContent = fs.readFileSync('dextonai_agent_audit_report.md', 'utf8');

  const res = await fetch('https://api.github.com/gists', {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      description: 'ACN Enterprise Agentic QA & Reliability Audit Report — Case Study',
      public: true,
      files: {
        'dextonai_agent_audit_report.md': {
          content: reportContent
        }
      }
    })
  });

  const data = await res.json();
  const gistUrl = data.html_url || (data.files && data.files['dextonai_agent_audit_report.md'] ? data.files['dextonai_agent_audit_report.md'].raw_url : '');
  console.log(`✅ Public Gist Created Successfully!`);
  console.log(`📌 Public URL: ${gistUrl}`);
  if (!res.ok) {
    console.error('Gist Error Detail:', JSON.stringify(data));
  }
  console.log(`====================================================\n`);

  if (gistUrl) {
    fs.writeFileSync('PUBLIC_GIST_URL.txt', gistUrl);
  }

}

publishGist().catch(console.error);
