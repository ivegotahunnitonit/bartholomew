import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/moorcheh-ai/memanto/issues?state=open');
  const data = await res.json();
  const list = data.map(issue => ({
    number: issue.number,
    title: issue.title,
    html_url: issue.html_url
  }));
  fs.writeFileSync('memanto-issues.json', JSON.stringify(list, null, 2));
  console.log('Saved memanto-issues.json');
}

run();
