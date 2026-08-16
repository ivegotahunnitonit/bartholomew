import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/readme');
  const data = await res.json();
  const content = Buffer.from(data.content, 'base64').toString('utf8');
  fs.writeFileSync('ai-research-readme.md', content);
  console.log('Saved ai-research-readme.md');
}

run();
