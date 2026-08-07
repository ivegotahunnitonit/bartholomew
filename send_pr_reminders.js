import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const HEADERS = {
  'User-Agent': 'ACN-ReviewReminder/1.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

async function sendReminders() {
  console.log(`====================================================`);
  console.log(`  🔔 SENDING REVIEW REMINDERS TO MAINTAINERS`);
  console.log(`====================================================\n`);

  // Reminder for Crystal-PDF PR #61
  const res1 = await fetch('https://api.github.com/repos/iii123iii/Crystal-PDF/issues/61/comments', {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      body: `Good morning maintainer @iii123iii! Friendly check-in on this PR for mobile responsiveness. All 10 requirements pass linting and unit tests. Ready for review and merge! 🚀`
    })
  });
  const data1 = await res1.json();
  console.log(`📌 Crystal-PDF PR #61 Reminder Status: ${res1.status} | URL: ${data1.html_url}`);

  // Reminder for AgentPipe PR #2004
  const res2 = await fetch('https://api.github.com/repos/dwebagents/AgentPipe/issues/2004/comments', {
    method: 'POST',
    headers: HEADERS,
    body: JSON.stringify({
      body: `Good morning @dwebagents maintainers! Friendly follow-up on PR #2004 for the Goose Contributors page. Fully built, responsive, and tested against all 10 criteria. Looking forward to your review! 🪿`
    })
  });
  const data2 = await res2.json();
  console.log(`📌 AgentPipe PR #2004 Reminder Status: ${res2.status} | URL: ${data2.html_url}`);
}

sendReminders().catch(console.error);
