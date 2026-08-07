import fs from 'fs';

async function checkPR(num) {
  const res = await fetch(`https://api.github.com/repos/moorcheh-ai/memanto/pulls/${num}`);
  const j = await res.json();
  return { num, state: j.state, merged: j.merged_at, title: j.title?.slice(0,60) };
}

async function checkIssue(num) {
  const res = await fetch(`https://api.github.com/repos/moorcheh-ai/memanto/issues/${num}`);
  const j = await res.json();
  return { num, state: j.state, title: j.title?.slice(0,60), labels: j.labels?.map(l=>l.name) };
}

const prs = await Promise.all([1524, 1525, 1526].map(checkPR));
const issues = await Promise.all([1436, 1437, 1438, 1418].map(checkIssue));

console.log('=== PR STATUS ===');
prs.forEach(p => console.log(`PR #${p.num}: ${p.state} | merged: ${p.merged} | ${p.title}`));
console.log('\n=== ISSUE STATUS ===');
issues.forEach(i => console.log(`Issue #${i.num}: ${i.state} | labels: ${i.labels?.join(',')} | ${i.title}`));
