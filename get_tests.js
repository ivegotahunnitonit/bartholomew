import fs from 'fs';

async function run() {
  for (const name of ['test_jwt_algorithm_key_confusion_fix.py', 'test_sso_federation.py']) {
    try {
      const res = await fetch(`https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/contents/tests/${name}`);
      const data = await res.json();
      const content = Buffer.from(data.content, 'base64').toString('utf8');
      fs.writeFileSync(name, content);
      console.log(`Saved ${name}`);
    } catch (err) {
      console.error(`Failed to download ${name}:`, err.message);
    }
  }
}

run();
