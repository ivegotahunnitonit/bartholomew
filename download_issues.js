import fs from 'fs';

async function download() {
  for (const id of ['1362', '1361', '1360', '1359']) {
    try {
      const res = await fetch(`https://api.github.com/repos/zhangjiayang6835-cyber/ai-research/issues/${id}`);
      const data = await res.json();
      fs.writeFileSync(`bounty-${id}.md`, data.body || '');
      console.log(`Downloaded bounty-${id}.md`);
    } catch (err) {
      console.error(`Failed to download ${id}:`, err.message);
    }
  }
}

download();
