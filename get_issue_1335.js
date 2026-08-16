import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/moorcheh-ai/memanto/issues/1335');
  const data = await res.json();
  fs.writeFileSync('issue-1335.md', data.body || '');
  console.log('Saved issue-1335.md');
}

run();
