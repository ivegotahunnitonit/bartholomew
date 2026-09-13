import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/moorcheh-ai/memanto/issues?state=open&per_page=100');
  const data = await res.json();
  const list = data
    .filter(item => !item.pull_request)
    .map(issue => ({
      number: issue.number,
      title: issue.title,
      html_url: issue.html_url
    }));
  fs.writeFileSync('memanto-only-issues.json', JSON.stringify(list, null, 2));
  console.log('Saved memanto-only-issues.json, count:', list.length);
}

run();
