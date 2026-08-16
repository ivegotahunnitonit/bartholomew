const https = require('https');
const fs = require('fs');
const token = process.env.GITHUB_TOKEN || require('./.env.js');
const options = {
  hostname: 'api.github.com',
  path: '/repos/moorcheh-ai/memanto/issues/1437',
  headers: { 'User-Agent': 'node', 'Authorization': `token ${token}` }
};
https.get(options, res => {
  let d = '';
  res.on('data', c => d += c);
  res.on('end', () => {
    const j = JSON.parse(d);
    const md = `# Issue #${j.number}: ${j.title}\n\n${j.body}`;
    fs.writeFileSync('issue-1437.md', md);
    console.log('Saved issue-1437.md');
  });
});
