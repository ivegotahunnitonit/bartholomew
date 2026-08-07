import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/contents/fixes/%5Bbug%5D_jwt_algorithm_.py');
  const data = await res.json();
  const content = Buffer.from(data.content, 'base64').toString('utf8');
  fs.writeFileSync('bug_jwt_algorithm.py', content);
  console.log('Saved bug_jwt_algorithm.py');
}

run();
