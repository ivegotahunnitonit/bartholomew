import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/contents/fixes/jwt_algorithm_key_confusion_fix.py');
  const data = await res.json();
  const content = Buffer.from(data.content, 'base64').toString('utf8');
  fs.writeFileSync('jwt_algorithm_key_confusion_fix.py', content);
  console.log('Saved jwt_algorithm_key_confusion_fix.py');
}

run();
