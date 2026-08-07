import fs from 'fs';

async function fetchIssue(num) {
  const res = await fetch(`https://api.github.com/repos/moorcheh-ai/memanto/issues/${num}`);
  const j = await res.json();
  const md = `# Issue #${j.number}: ${j.title}\n\n${j.body || '(no body)'}`;
  fs.writeFileSync(`issue-${num}.md`, md);
  console.log(`Saved issue-${num}.md`);
}

await fetchIssue(1438);
await fetchIssue(1436);
await fetchIssue(1418);
