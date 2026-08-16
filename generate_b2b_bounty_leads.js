import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const HEADERS = {
  'User-Agent': 'ACN-LeadScout/1.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

// Top Open-Source AI Agent Repositories Forked by Enterprise Teams
const AGENT_REPOS = [
  'dextonai/agent-browser',
  'crewAIInc/crewAI',
  'browser-use/browser-use'
];

async function scanB2BLeads() {
  console.log(`====================================================`);
  console.log(`  🎯 B2B LEADS GENERATOR — AI AGENT FORK SNIPER`);
  console.log(`====================================================\n`);

  const leads = [];

  for (const repo of AGENT_REPOS) {
    console.log(`🔍 Scanning forks for: ${repo}...`);
    try {
      const res = await fetch(`https://api.github.com/repos/${repo}/forks?sort=stargazers&per_page=15`, { headers: HEADERS });
      if (res.ok) {
        const forks = await res.json();
        for (const fork of forks) {
          const owner = fork.owner;
          leads.push({
            repo_forked: repo,
            fork_name: fork.full_name,
            owner_login: owner.login,
            owner_type: owner.type, // User or Organization
            profile_url: owner.html_url,
            avatar_url: owner.avatar_url,
            fork_created_at: fork.created_at,
            audit_pitch_angle: owner.type === 'Organization' 
              ? 'Corporate Fork Telemetry & Secret Leak Audit ($750)'
              : 'Senior Developer Custom Agent Observability Audit ($250)'
          });
        }
      }
    } catch (err) {
      console.error(`Error scanning ${repo}:`, err.message);
    }
  }

  const outputData = {
    generated_at: new Date().toISOString(),
    total_leads_found: leads.length,
    service_target: "Agentic QA & Reliability Audit ($250 - $750)",
    leads: leads
  };

  fs.writeFileSync('B2B_AUDIT_LEADS.json', JSON.stringify(outputData, null, 2));

  console.log(`\n====================================================`);
  console.log(`  ✅ B2B LEADS GENERATED: ${leads.length} High-Intent Contacts`);
  console.log(`  Saved to: B2B_AUDIT_LEADS.json`);
  console.log(`====================================================\n`);
}

scanB2BLeads().catch(console.error);
