import fs from 'fs';

async function run() {
  const res = await fetch('https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/contents/BOUNTY_LEDGER.json');
  const data = await res.json();
  const content = Buffer.from(data.content, 'base64').toString('utf8');
  fs.writeFileSync('BOUNTY_LEDGER.json', content);
  console.log('Saved BOUNTY_LEDGER.json');
}

run();
