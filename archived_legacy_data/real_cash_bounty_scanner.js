import fs from 'fs';
import { getPayoutInstructions, TARGET_WALLETS } from './auto_revenue_dispatcher.js';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const HEADERS = {
  'User-Agent': 'ACN-RealProfitHunter/5.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

async function searchGlobalCashBounties() {
  console.log('====================================================');
  console.log('   REAL-CASH BOUNTY SCANNER & AUTO-PAYOUT DISPATCHER');
  console.log('====================================================\n');
  console.log(` Primary Payout Destination: Base USDC (${TARGET_WALLETS.BASE_USDC})`);
  console.log(` Crypto Payout Destination: Akash AKT (${TARGET_WALLETS.AKASH_AKT})\n`);

  const EXCLUDED_REPOS = [
    'zhangjiayang6835-cyber/bounty-plaza',
    'zhangjiayang6835-cyber/ai-research'
  ];

  const queries = [
    'label:bounty "$"',
    'label:bounty USD',
    'label:bounty USDC',
    'Algora bounty state:open',
    'BountyHub state:open'
  ];

  const foundBounties = [];

  for (const q of queries) {
    try {
      const res = await fetch(`https://api.github.com/search/issues?q=${encodeURIComponent(q + ' is:issue is:open')}&per_page=20`, {
        headers: HEADERS
      });
      const data = await res.json();

      if (data.items && Array.isArray(data.items)) {
        for (const item of data.items) {
          const repoFullName = item.repository_url.replace('https://api.github.com/repos/', '');
          if (EXCLUDED_REPOS.includes(repoFullName)) continue;

          const titleBody = `${item.title} ${item.body || ''}`;
          const dollarMatch = titleBody.match(/\$(\d+[\d,]*)/) || titleBody.match(/(\d+)\s*(USD|USDC|EUR)/i);
          const rewardAmount = dollarMatch ? `$${dollarMatch[1]}` : 'Cash/USDC';

          foundBounties.push({
            id: item.id,
            number: item.number,
            title: item.title,
            repo: repoFullName,
            html_url: item.html_url,
            reward: rewardAmount,
            created_at: item.created_at,
            payout_destination: TARGET_WALLETS.BASE_USDC,
            labels: item.labels.map(l => l.name)
          });
        }
      }
    } catch (err) {
      console.error(`Error querying "${q}":`, err.message);
    }
  }

  const uniqueBounties = Array.from(new Map(foundBounties.map(b => [b.html_url, b])).values());

  const outputData = {
    last_updated: new Date().toISOString(),
    total_found: uniqueBounties.length,
    payout_wallets: TARGET_WALLETS,
    bounties: uniqueBounties
  };

  fs.writeFileSync('REAL_PROFIT_BOUNTIES.json', JSON.stringify(outputData, null, 2));

  console.log(`====================================================`);
  console.log(`   DISPATCHER AUDIT — ${uniqueBounties.length} CASH BOUNTIES FOUND`);
  console.log(`  All payout instructions linked to: ${TARGET_WALLETS.BASE_USDC}`);
  console.log(`====================================================\n`);
}

searchGlobalCashBounties().catch(console.error);
