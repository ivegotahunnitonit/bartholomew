import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/contents/jwt_poc.py');
  const data = await res.json();
  const content = Buffer.from(data.content, 'base64').toString('utf8');
  fs.writeFileSync('jwt_poc.py', content);
  console.log('Saved jwt_poc.py');
}

run();
