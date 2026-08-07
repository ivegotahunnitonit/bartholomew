// AlgoraBountyScanner.ts
// Scans Algora.io and Opire for REAL funded open-source issues
// matching our TypeScript/Node.js/Python skill set.
// Real USD paid via Stripe upon PR merge.

import https from 'node:https';

interface BountyIssue {
  id: string;
  title: string;
  url: string;
  rewardUsd: number;
  repo: string;
  language: string;
  platform: 'algora' | 'opire';
  claimedAt?: number;
}

const SKILL_KEYWORDS = [
  'typescript', 'node', 'nodejs', 'javascript', 'api',
  'rest', 'websocket', 'sqlite', 'performance', 'bug fix',
  'refactor', 'test', 'docker', 'python', 'fastapi', 'openapi'
];

const discovered: BountyIssue[] = [];
let totalDiscoveredValue = 0;

function httpsGet(url: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const req = https.get(url, {
      headers: {
        'User-Agent': 'ACN-BountyScanner/1.0',
        'Accept': 'application/json',
      }
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => resolve(data));
    });
    req.on('error', reject);
    req.setTimeout(8000, () => { req.destroy(); reject(new Error('timeout')); });
  });
}

export class AlgoraBountyScanner {
  private static isRunning = false;

  static start(intervalMs = 120000) {
    if (this.isRunning) return;
    this.isRunning = true;
    console.log('[AlgoraBountyScanner] Real bounty discovery engine started (scan every 2min)...');
    this.scan(); // immediate first scan
    setInterval(() => this.scan(), intervalMs);
  }

  static async scan() {
    try {
      await this.scanAlgora();
    } catch (err: any) {
      console.warn('[AlgoraBountyScanner] Algora scan:', err.message);
    }
    try {
      await this.scanOpire();
    } catch (err: any) {
      console.warn('[AlgoraBountyScanner] Opire scan:', err.message);
    }
  }

  static async scanAlgora() {
    // Algora public API: list funded bounties
    const raw = await httpsGet('https://algora.io/api/bounties?status=open&limit=50');
    const data = JSON.parse(raw);
    const issues: any[] = data.data || data.bounties || data || [];

    for (const issue of issues) {
      const title = (issue.title || issue.name || '').toLowerCase();
      const lang = (issue.language || issue.repo?.language || '').toLowerCase();
      const reward = parseFloat(issue.reward_usd || issue.amount || issue.value || 0);

      if (reward < 50) continue; // Only pursue $50+ bounties
      const isMatch = SKILL_KEYWORDS.some(kw => title.includes(kw) || lang.includes(kw));
      if (!isMatch) continue;

      const alreadyFound = discovered.find(d => d.url === (issue.url || issue.html_url));
      if (alreadyFound) continue;

      const bounty: BountyIssue = {
        id: String(issue.id || issue.number),
        title: issue.title || issue.name,
        url: issue.url || issue.html_url,
        rewardUsd: reward,
        repo: issue.repo?.full_name || issue.repository || 'unknown',
        language: lang,
        platform: 'algora',
      };
      discovered.push(bounty);
      totalDiscoveredValue += reward;
      console.log(`[AlgoraBountyScanner] 🎯 REAL BOUNTY FOUND: $${reward} | ${bounty.title} | ${bounty.url}`);
    }
  }

  static async scanOpire() {
    // Opire public issues endpoint
    const raw = await httpsGet('https://api.opire.dev/v1/rewards?status=created&limit=50');
    const data = JSON.parse(raw);
    const issues: any[] = data.data || data.rewards || data || [];

    for (const issue of issues) {
      const title = (issue.title || '').toLowerCase();
      const reward = parseFloat(issue.amount_usd || issue.amount || 0);

      if (reward < 50) continue;
      const isMatch = SKILL_KEYWORDS.some(kw => title.includes(kw));
      if (!isMatch) continue;

      const alreadyFound = discovered.find(d => d.id === String(issue.id));
      if (alreadyFound) continue;

      const bounty: BountyIssue = {
        id: String(issue.id),
        title: issue.title,
        url: issue.issue_url || issue.url,
        rewardUsd: reward,
        repo: issue.repo || 'unknown',
        language: 'unknown',
        platform: 'opire',
      };
      discovered.push(bounty);
      totalDiscoveredValue += reward;
      console.log(`[AlgoraBountyScanner] 🎯 OPIRE BOUNTY: $${reward} | ${bounty.title} | ${bounty.url}`);
    }
  }

  static getDiscovered(): BountyIssue[] { return discovered; }
  static getTotalValue(): number { return totalDiscoveredValue; }
}
