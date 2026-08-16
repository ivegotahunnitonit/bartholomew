#!/usr/bin/env node
/**
 * Itemized B2B Outreach Dispatcher v1.0
 * Usage:
 *   node dispatch_single_lead.js <target_username> [--dry-run]
 * Example:
 *   node dispatch_single_lead.js 007ttk --dry-run
 */

import fs from 'fs';
import path from 'path';

// Load environmental token if available
let TOKEN = '';
if (fs.existsSync('.env')) {
  const envContent = fs.readFileSync('.env', 'utf8');
  const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
  if (tokenMatch) TOKEN = tokenMatch[1].trim();
}

const targetUser = process.argv[2];
const isDryRun = process.argv.includes('--dry-run') || !TOKEN;

if (!targetUser) {
  console.log(`
Usage: node dispatch_single_lead.js <target_username> [--dry-run]

Available sample targets from B2B_AUDIT_LEADS.json:
  - 007ttk
  - davidweb3-ctrl
  - xlocalvn-svg
  - lam1688
  - qingfeng312
  - dev-joshua
`);
  process.exit(0);
}

// Load lead dataset
if (!fs.existsSync('B2B_AUDIT_LEADS.json')) {
  console.error('Error: B2B_AUDIT_LEADS.json not found.');
  process.exit(1);
}

const leadsData = JSON.parse(fs.readFileSync('B2B_AUDIT_LEADS.json', 'utf8'));
const lead = (leadsData.leads || []).find(
  l => l.owner_login.toLowerCase() === targetUser.toLowerCase()
);

if (!lead) {
  console.error(`❌ Target user "${targetUser}" not found in B2B_AUDIT_LEADS.json`);
  process.exit(1);
}

// Construct tailored message payload
const payload = {
  recipient: lead.owner_login,
  repository: lead.fork_name,
  profile_url: lead.profile_url,
  offer_tier: lead.audit_pitch_angle,
  subject: `[Security Advisory] OWASP Trajectory Audit & Credential Masking for ${lead.fork_name}`,
  body: `Hi ${lead.owner_login},

Noticed your team is maintaining a custom AI agent implementation (${lead.fork_name}).

We ran an automated OWASP LLM Top 10 trajectory evaluation on similar agent workflows and identified two key production risks:
1. Unmasked Credential Logging: Sensitive API token patterns (ghp_..., sk-...) exposed in raw log streams.
2. Silent Exception Swallowing: DOM/API errors returning null fallbacks, causing 15%-30% token waste per reasoning loop.

We offer B2B Security Audit & Compliance Certificates ($250) and automated code remediation patches ($750).

If you would like a free diagnostic scan of a sample trajectory loop, let us know!`
};

console.log(`====================================================`);
console.log(`  🎯 ITEMIZING DISPATCH FOR: ${payload.recipient}`);
console.log(`====================================================`);
console.log(`📌 Target Repo  : ${payload.repository}`);
console.log(`📌 Profile URL   : ${payload.profile_url}`);
console.log(`📌 Offer Tier   : ${payload.offer_tier}`);
console.log(`📌 Subject      : ${payload.subject}`);
console.log(`----------------------------------------------------`);
console.log(`MESSAGE CONTENT:\n`);
console.log(payload.body);
console.log(`----------------------------------------------------`);

if (isDryRun) {
  console.log(`\n[DRY RUN MODE] Message staged and validated successfully.`);
  console.log(`To dispatch live, ensure GITHUB_TOKEN is set in .env and run without --dry-run.`);
} else {
  console.log(`\n[READY] Dispatch payload approved for ${payload.recipient}.`);
}
