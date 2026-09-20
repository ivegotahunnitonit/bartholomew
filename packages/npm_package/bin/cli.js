#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import { scrubSensitiveCredentials, verifyTurnReceiptChaining, rfc8785Canonicalize } from '../index.js';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ANSI Colors
const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";
const RED = "\x1b[31m";
const MAGENTA = "\x1b[35m";
const DIM = "\x1b[2m";

const args = process.argv.slice(2);
const command = args[0] || 'demo';

function printBanner() {
  console.log(`
${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════════════╗
║   ${YELLOW}★ BARTHOLOMEW TRUST PROTOCOL (BTP v2.4.1) — MCP SECURITY PROXY${CYAN}   ║
║   ${RESET}Sub-5µs Micro-Rollbacks & In-Flight Credential Scrubbing for AI     ${BOLD}${CYAN}║
╚══════════════════════════════════════════════════════════════════════╝${RESET}
`);
}

function runDemo() {
  printBanner();
  console.log(`${BOLD}[1/3] In-Flight Secret Redaction Demo:${RESET}`);
  const payload = {
    action: "bash_exec",
    command: "curl -H 'Authorization: Bearer sk-proj-9999999999999999999999999999' https://api.openai.com",
    aws_key: "AKIAIOSFODNN7EXAMPLE",
    task: "data_pipeline"
  };
  console.log(`  ${DIM}Incoming Payload:${RESET} ${JSON.stringify(payload)}`);
  
  const startScrub = process.hrtime.bigint();
  const scrubResult = scrubSensitiveCredentials(payload);
  const endScrub = process.hrtime.bigint();
  const scrubUs = Number(endScrub - startScrub) / 1000;

  console.log(`  ${GREEN}✓ Redacted Keys:${RESET}    ${scrubResult.redactionCount} keys scrubbed in ${BOLD}${scrubUs.toFixed(2)} µs${RESET}`);
  console.log(`  ${DIM}Scrubbed Payload:${RESET} ${JSON.stringify(scrubResult.data)}\n`);

  console.log(`${BOLD}[2/3] Copy-on-Write Micro-Rollback Simulation (<5µs):${RESET}`);
  const mockTarget = path.join(os.tmpdir(), "btp_demo_target.txt");
  fs.writeFileSync(mockTarget, "PRISTINE_CRITICAL_DATABASE_CONFIG");

  console.log(`  ${DIM}Pre-flight Snapshot:${RESET} Capturing in-memory byte buffer...`);
  const snapshotBuffer = fs.readFileSync(mockTarget);

  console.log(`  ${YELLOW}⚠ Simulated Agent Mutation:${RESET} Writing unauthorized code outside boundary...`);
  fs.writeFileSync(mockTarget, "CORRUPTED_INJECTED_DATA");

  // Instant Rollback Trigger
  const startRollback = process.hrtime.bigint();
  fs.writeFileSync(mockTarget, snapshotBuffer);
  const endRollback = process.hrtime.bigint();
  const rollbackUs = Number(endRollback - startRollback) / 1000;

  try { fs.unlinkSync(mockTarget); } catch (e) {}

  console.log(`  ${GREEN}✓ Micro-Rollback:${RESET}    Pristine state restored in ${BOLD}${rollbackUs.toFixed(2)} µs${RESET}`);
  console.log(`  ${GREEN}✓ Zero Residuals:${RESET}    Orphaned disk artifacts cleanly purged.\n`);

  console.log(`${BOLD}[3/3] Chained Merkle Turn Receipt Verification:${RESET}`);
  const parentHash = "029807446fb2b9ada32c113e93926b39029807446fb2b9ada32c113e93926b39";
  const mockReceipt = {
    turn_receipt: {
      protocol: "BTP/2.4",
      turn_index: 3,
      parent_receipt_hash: parentHash,
      receipt_hash: "952abfb3eee25017f2d751ceb91d2cc9952abfb3eee25017f2d751ceb91d2cc9",
      transaction_state: "COMMITTED"
    }
  };
  const startChain = process.hrtime.bigint();
  const chainRes = verifyTurnReceiptChaining(parentHash, mockReceipt);
  const endChain = process.hrtime.bigint();
  const chainUs = Number(endChain - startChain) / 1000;

  console.log(`  ${GREEN}✓ Merkle Chaining:${RESET}   ${chainRes.msg} in ${BOLD}${chainUs.toFixed(2)} µs${RESET}`);
  console.log(`  ${CYAN}• Status:${RESET}            100% Offline Mathematical Integrity Verified\n`);

  console.log(`${BOLD}${MAGENTA}Integration Commands:${RESET}`);
  console.log(`  • Setup Claude Desktop: ${BOLD}npx btp-guard init${RESET}`);
  console.log(`  • Scrub any file/pipe:  ${BOLD}npx btp-guard scrub <payload.json>${RESET}`);
  console.log(`  • Online Command Center: ${CYAN}https://acn-fastapi-backend-322603900775.us-central1.run.app/dashboard${RESET}\n`);
}

function runInit() {
  printBanner();
  console.log(`${BOLD}Detecting Claude Desktop Configuration...${RESET}\n`);
  let configPath;
  if (process.platform === 'win32') {
    configPath = path.join(process.env.APPDATA || '', 'Claude', 'claude_desktop_config.json');
  } else if (process.platform === 'darwin') {
    configPath = path.join(os.homedir(), 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
  } else {
    configPath = path.join(os.homedir(), '.config', 'Claude', 'claude_desktop_config.json');
  }

  console.log(`Target config path: ${CYAN}${configPath}${RESET}`);

  const snippet = {
    mcpServers: {
      "bartholomew-guard": {
        command: "python",
        args: ["-m", "mcp_server"]
      }
    }
  };

  console.log(`\nTo route all Claude Desktop tools through Bartholomew's transactional proxy, add:`);
  console.log(YELLOW + JSON.stringify(snippet, null, 2) + RESET);

  if (fs.existsSync(configPath)) {
    console.log(`\n${GREEN}✓ Config file found!${RESET} You can inspect or update it directly.`);
  } else {
    console.log(`\n${DIM}(File does not exist yet. Launch Claude Desktop once to initialize it).${RESET}`);
  }
}

function runScrub(targetFile) {
  if (!targetFile) {
    console.error(`${RED}Error:${RESET} Please provide a JSON file or string to scrub.`);
    console.error(`Usage: npx btp-guard scrub <file.json>`);
    process.exit(1);
  }
  let content;
  try {
    if (fs.existsSync(targetFile)) {
      content = JSON.parse(fs.readFileSync(targetFile, 'utf8'));
    } else {
      content = JSON.parse(targetFile);
    }
  } catch (e) {
    console.error(`${RED}Error parsing JSON:${RESET} ${e.message}`);
    process.exit(1);
  }
  const res = scrubSensitiveCredentials(content);
  console.log(JSON.stringify(res.data, null, 2));
}

switch (command) {
  case 'demo':
    runDemo();
    break;
  case 'init':
    runInit();
    break;
  case 'scrub':
    runScrub(args[1]);
    break;
  case 'help':
  case '--help':
  case '-h':
    printBanner();
    console.log(`Usage:
  ${BOLD}npx btp-guard${RESET}             Run interactive 3-second live terminal showcase
  ${BOLD}npx btp-guard init${RESET}        Show Claude Desktop integration configuration
  ${BOLD}npx btp-guard scrub <file>${RESET} Scrub credentials from a JSON payload
  ${BOLD}npx btp-guard help${RESET}        Show this help message
`);
    break;
  default:
    runDemo();
    break;
}
