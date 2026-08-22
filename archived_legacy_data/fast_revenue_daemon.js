import fs from 'fs';
import { UNIVERSAL_WALLETS, getPayoutInstructions } from './universal_multi_asset_dispatcher.js';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const HEADERS = {
  'User-Agent': 'ACN-UniversalMultiAssetDaemon/9.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

const EXCLUDED_REPOS = [
  'zhangjiayang6835-cyber/bounty-plaza',
  'zhangjiayang6835-cyber/ai-research'
];

// 16 Universal Tradeable Currency Search Vectors
const GLOBAL_QUERIES = [
  'label:bounty "$"',
  'label:bounty USDC',
  'label:bounty USDT',
  'label:bounty ETH',
  'label:bounty SOL',
  'label:bounty BTC',
  'Algora bounty state:open',
  'BountyHub state:open',
  'Opire bounty state:open',
  'Gitcoin bounty state:open',
  'Superteam bounty state:open',
  'label:"help wanted" "$"',
  'label:"good first issue" "$"',
  '"bounty:" USDC state:open',
  '"bounty:" ETH state:open',
  '"reward:" USD state:open'
];

let cycleCount = 0;
const trackedBountiesMap = new Map();

async function runUniversalMultiAssetScan() {
  cycleCount++;
  const timestamp = new Date().toISOString();
  const currentQuery = GLOBAL_QUERIES[cycleCount % GLOBAL_QUERIES.length];

  console.log(`[Universal Multi-Asset Daemon Cycle #${cycleCount} @ ${timestamp}] Querying Vector: "${currentQuery}"...`);

  try {
    const res = await fetch(`https://api.github.com/search/issues?q=${encodeURIComponent(currentQuery + ' is:issue is:open')}&per_page=25`, {
      headers: HEADERS
    });

    if (res.ok) {
      const data = await res.json();
      if (data.items && Array.isArray(data.items)) {
        let newFound = 0;
        for (const item of data.items) {
          const repo = item.repository_url.replace('https://api.github.com/repos/', '');
          if (EXCLUDED_REPOS.includes(repo)) continue;

          if (!trackedBountiesMap.has(item.html_url)) {
            newFound++;
            let detectedAsset = 'USDC';
            const titleUpper = (item.title + ' ' + (item.body || '')).toUpperCase();
            if (titleUpper.includes('ETH')) detectedAsset = 'ETH';
            else if (titleUpper.includes('SOL')) detectedAsset = 'SOL';
            else if (titleUpper.includes('BTC')) detectedAsset = 'BTC';
            else if (titleUpper.includes('USDT')) detectedAsset = 'USDT';
            else if (titleUpper.includes('AKT')) detectedAsset = 'AKT';

            trackedBountiesMap.set(item.html_url, {
              id: item.id,
              number: item.number,
              title: item.title,
              url: item.html_url,
              repo: repo,
              accepted_asset: detectedAsset,
              query_vector: currentQuery,
              payout_instruction: getPayoutInstructions(detectedAsset),
              discovered_at: timestamp,
              outgoing_cost: 0.00
            });
          }
        }

        const allBounties = Array.from(trackedBountiesMap.values());

        fs.writeFileSync('FAST_DAEMON_STATUS.json', JSON.stringify({
          mode: 'UNIVERSAL_MULTI_ASSET_CASH_HUNTER',
          last_cycle: cycleCount,
          last_scanned: timestamp,
          active_vector: currentQuery,
          interval_seconds: 10,
          total_bounties_tracked: allBounties.length,
          new_this_cycle: newFound,
          zero_cost_policy: '$0.00 Outgoing. 100% Retained Revenue.',
          wallets: UNIVERSAL_WALLETS,
          latest_bounties: allBounties.slice(-8).reverse()
        }, null, 2));

        console.log(`[Universal Daemon Cycle #${cycleCount}] Complete. Total tracked: ${allBounties.length} multi-asset cash opportunities (+${newFound} new).`);
      }
    }
  } catch (err) {
    console.error(`[Universal Daemon Error]:`, err.message);
  }
}

console.log(' ACN UNIVERSAL MULTI-ASSET DAEMON v9.0 LAUNCHED — POLLING ALL CRYPTO ASSETS 24/7');
runUniversalMultiAssetScan();
setInterval(runUniversalMultiAssetScan, 10000); // 10s loop
