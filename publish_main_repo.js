import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let GITHUB_TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
if ((!GITHUB_TOKEN || GITHUB_TOKEN === 'ghp_dummy') && fs.existsSync('.env')) {
  const envText = fs.readFileSync('.env', 'utf8');
  const match = envText.match(/GITHUB_TOKEN=([^\r\n]+)/);
  if (match) GITHUB_TOKEN = match[1].trim();
}

const repoName = 'agentic-eval';
const HEADERS = {
  'Authorization': `token ${GITHUB_TOKEN}`,
  'Accept': 'application/vnd.github.v3+json',
  'User-Agent': 'Bartholomew-Security-Publisher'
};

async function publishRepository() {
  console.log('====================================================');
  console.log('  🚀 PUBLISHING BARTHOLOMEW TO GITHUB');
  console.log('====================================================\n');

  let ownerName = 'ivegotahunnitonit';

  try {
    const userRes = await fetch('https://api.github.com/user', { headers: HEADERS });
    if (userRes.ok) {
      const userData = await userRes.json();
      if (userData.login) ownerName = userData.login;
    }
  } catch (e) {}

  const getRes = await fetch(`https://api.github.com/repos/${ownerName}/${repoName}`, { headers: HEADERS });
  let repoData = {};
  if (getRes.ok) {
    repoData = await getRes.json();
    console.log(`📌 Using existing repository: https://github.com/${ownerName}/${repoName}`);
  } else {
    const createRes = await fetch('https://api.github.com/user/repos', {
      method: 'POST',
      headers: HEADERS,
      body: JSON.stringify({ name: repoName, private: false, auto_init: true })
    });
    if (createRes.ok) {
      repoData = await createRes.json();
      console.log(`✅ Repository created: https://github.com/${ownerName}/${repoName}`);
    }
  }

  const branch = repoData.default_branch || 'main';

  // Files to commit
  const filesToPublish = [
    { local: 'EXECUTIVE_ONE_PAGER.md', target: 'README.md' },
    { local: 'LICENSE.md', target: 'LICENSE.md' },
    { local: 'BARTHOLOMEW_OUTBOUND_SALES_KIT.md', target: 'BARTHOLOMEW_OUTBOUND_SALES_KIT.md' },
    { local: 'FINTECH_OUTREACH_KIT.md', target: 'FINTECH_OUTREACH_KIT.md' },
    { local: 'B2B_AUDIT_REPORT_SAMPLE.md', target: 'B2B_AUDIT_REPORT_SAMPLE.md' },
    { local: 'generate_cold_pitch.py', target: 'generate_cold_pitch.py' },
    { local: 'agentic_eval_bot.py', target: 'agentic_eval_bot.py' },
    { local: 'security_stress_tester.py', target: 'security_stress_tester.py' },
    { local: 'institutional_audit_firm.py', target: 'institutional_audit_firm.py' },
    { local: 'export_audit_pdf.py', target: 'export_audit_pdf.py' },
    { local: 'audit_firm_ledger.py', target: 'audit_firm_ledger.py' },
    { local: 'agentic_eval_sdk.py', target: 'agentic_eval_sdk.py' },
    { local: 'auto_patch_pr_engine.py', target: 'auto_patch_pr_engine.py' },
    { local: 'agent_pen_tester.py', target: 'agent_pen_tester.py' },
    { local: 'export_pen_test_report.py', target: 'export_pen_test_report.py' },
    { local: 'agentic_eval_wizard.py', target: 'agentic_eval_wizard.py' },
    { local: 'setup.py', target: 'setup.py' },
    { local: 'pyproject.toml', target: 'pyproject.toml' },
    { local: 'action.yml', target: 'action.yml' },
    { local: 'github_action/action.yml', target: 'github_action/action.yml' },
    { local: 'render.yaml', target: 'render.yaml' },
    { local: 'vercel.json', target: 'vercel.json' },
    { local: 'requirements.txt', target: 'requirements.txt' },
    { local: 'api/requirements.txt', target: 'api/requirements.txt' },
    { local: 'index.html', target: 'index.html' },
    { local: 'api/index.py', target: 'api/index.py' },
    { local: 'agent_qa_guard.py', target: 'agent_qa_guard.py' },
    { local: 'src/LandingPage.tsx', target: 'src/LandingPage.tsx' },
    { local: 'test_agentic_eval_security.py', target: 'test_agentic_eval_security.py' },
    { local: 'python_backend/app/main.py', target: 'python_backend/app/main.py' },
    { local: 'python_backend/app/agent_eval_janitor.py', target: 'python_backend/app/agent_eval_janitor.py' },
    { local: 'python_backend/app/encryption_and_security.py', target: 'python_backend/app/encryption_and_security.py' },
    { local: 'python_backend/app/micro_api_suite.py', target: 'python_backend/app/micro_api_suite.py' },
    { local: 'python_backend/app/auth.py', target: 'python_backend/app/auth.py' },
    { local: 'python_backend/Procfile', target: 'python_backend/Procfile' },
    { local: 'go_services/main.go', target: 'go_services/main.go' },
    { local: 'go_services/main_test.go', target: 'go_services/main_test.go' },
    { local: 'go_services/sdk/bartholomew.go', target: 'go_services/sdk/bartholomew.go' },
    { local: 'go_services/go.mod', target: 'go_services/go.mod' },
    { local: 'go.mod', target: 'go.mod' },
    { local: 'main.go', target: 'main.go' },
    { local: 'datasets/dataset_metadata.json', target: 'datasets/dataset_metadata.json' }
  ];

  for (const item of filesToPublish) {
    const fullLocalPath = path.join(__dirname, item.local);
    if (!fs.existsSync(fullLocalPath)) continue;

    console.log(`📌 Committing ${item.target}...`);
    const content = fs.readFileSync(fullLocalPath, 'utf8');

    // Get current SHA if exists
    const fileUrl = `https://api.github.com/repos/${ownerName}/${repoName}/contents/${item.target}`;
    const currentRes = await fetch(fileUrl, { headers: HEADERS });
    let sha = undefined;
    if (currentRes.status === 200) {
      const currentData = await currentRes.json();
      sha = currentData.sha;
    }

    const putRes = await fetch(fileUrl, {
      method: 'PUT',
      headers: HEADERS,
      body: JSON.stringify({
        message: `Bartholomew Enterprise Update: ${item.target}`,
        content: Buffer.from(content).toString('base64'),
        sha: sha,
        branch: branch
      })
    });

    if (putRes.status === 200 || putRes.status === 201) {
      console.log(`  ✅ Published ${item.target}`);
    } else {
      const errData = await putRes.json();
      console.log(`  ❌ Failed ${item.target}: ${errData.message}`);
    }
  }

  console.log('\n====================================================');
  console.log(`  🎉 BARTHOLOMEW PUBLISHED TO GITHUB SUCCESSFULLY!`);
  console.log(`  Repository URL: https://github.com/${ownerName}/${repoName}`);
  console.log('====================================================\n');
}

publishRepository().catch(console.error);
