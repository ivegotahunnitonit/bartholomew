import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/contents/sso_federation.py');
  const data = await res.json();
  const content = Buffer.from(data.content, 'base64').toString('utf8');
  fs.writeFileSync('sso_federation.py', content);
  console.log('Saved sso_federation.py');
}

run();
