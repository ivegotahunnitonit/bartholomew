import fetch from 'node-fetch';

async function setup() {
  console.log('Activating automated Base USDC yield optimization...');
  try {
    const settleRes = await fetch('http://127.0.0.1:8080/api/settings/intake', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ auto_settle_on_match: true })
    });
    if (settleRes.ok) console.log('Auto-settle enabled successfully.');
    else console.error('Failed to enable auto-settle:', await settleRes.text());
  } catch(e) {
    console.error('Error enabling auto-settle:', e);
  }
  
  console.log('Spawning additional supernodes...');
  const ports = [8081, 8082, 8083];
  
  for (const port of ports) {
    try {
      const spawnRes = await fetch('http://127.0.0.1:8080/api/orchestrator/spawn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ port })
      });
      const data = await spawnRes.json();
      if (data.success) {
        console.log(`Successfully spawned cluster node on port ${port}.`);
      } else {
        console.error(`Failed to spawn node on port ${port}:`, data.error);
      }
    } catch(e) {
      console.error(`Error spawning node on port ${port}:`, e);
    }
  }
  
  console.log('Setup complete.');
}

setup();
