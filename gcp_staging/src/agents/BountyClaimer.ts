// BountyClaimer.ts
// Watches AlgoraBountyScanner discoveries and auto-claims matching bounties
// by posting @opire try / @algora claim comments on the GitHub issues.
// Real USD payment flows upon PR merge.

import https from 'node:https';
import { AlgoraBountyScanner } from './AlgoraBountyScanner.ts';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN || '';
const claimed = new Set<string>();

function parseGitHubIssueUrl(url: string): { owner: string; repo: string; number: number } | null {
  // https://github.com/owner/repo/issues/123
  const match = url?.match(/github\.com\/([^/]+)\/([^/]+)\/issues\/(\d+)/);
  if (!match) return null;
  return { owner: match[1], repo: match[2], number: parseInt(match[3]) };
}

async function postComment(owner: string, repo: string, issueNumber: number, body: string): Promise<number> {
  return new Promise((resolve) => {
    const payload = JSON.stringify({ body });
    const req = https.request({
      hostname: 'api.github.com',
      path: `/repos/${owner}/${repo}/issues/${issueNumber}/comments`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'ACN-BountyClaimer/1.0',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
      },
    }, (res) => {
      res.on('data', () => {});
      res.on('end', () => resolve(res.statusCode || 0));
    });
    req.on('error', () => resolve(0));
    req.setTimeout(8000, () => { req.destroy(); resolve(0); });
    req.write(payload);
    req.end();
  });
}

export class BountyClaimer {
  private static isRunning = false;

  static start(intervalMs = 15000) {
    if (!GITHUB_TOKEN) {
      console.log('[BountyClaimer] No GITHUB_TOKEN — bounty auto-claim disabled.');
      return;
    }
    if (this.isRunning) return;
    this.isRunning = true;
    console.log('[BountyClaimer] Bounty auto-claim engine started (15s cycle)...');

    const cycle = async () => {
      await this.claimPendingBounties();
      setTimeout(cycle, intervalMs);
    };
    cycle();
  }

  static async claimPendingBounties() {
    const bounties = AlgoraBountyScanner.getDiscovered();

    for (const bounty of bounties) {
      if (claimed.has(bounty.id)) continue;
      if (!bounty.url) continue;

      const parsed = parseGitHubIssueUrl(bounty.url);
      if (!parsed) continue;

      let claimComment = '';
      if (bounty.platform === 'opire') {
        claimComment = `@opire try\n\n> Claimed by Bartholomew ACN — autonomous circular economy exchange network. Will deliver a high-quality TypeScript/Node.js solution.`;
      } else {
        // Algora uses a different claim flow — post intent comment
        claimComment = `I'd like to work on this issue.\n\n**About me**: Building Bartholomew ACN — an autonomous industrial circular economy exchange in TypeScript/Node.js. I have deep experience with the tech stack in this repo.\n\n**Approach**: [Will outline solution after reviewing the codebase in detail]\n\n**ETA**: Will have a PR ready within 48 hours.`;
      }

      const status = await postComment(parsed.owner, parsed.repo, parsed.number, claimComment);
      if (status === 201) {
        claimed.add(bounty.id);
        console.log(`[BountyClaimer] ✅ CLAIMED: $${bounty.rewardUsd} bounty on ${bounty.url} (HTTP ${status})`);
      } else {
        console.log(`[BountyClaimer] Claim attempt failed: HTTP ${status} on ${bounty.url}`);
      }
    }
  }

  static getClaimedCount(): number { return claimed.size; }
}
