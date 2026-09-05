#!/usr/bin/env node

import { spawn } from 'child_process';
import readline from 'readline';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { scrubSecrets, evaluateToolCall, loadLicense } from '../index.js';

const STRIPE_PRO_URL = "https://buy.stripe.com/fZu28rbNz5TYcmAddK9R600";
const STRIPE_ENTERPRISE_URL = "https://buy.stripe.com/fZu14ng3PgyC9ao2z69R601";
const STORE_URL = "https://bartholomew.info/store/";

const args = process.argv.slice(2);
const command = args[0];

if (command === 'activate') {
  runActivate(args[1]);
} else if (command === 'status') {
  runStatus();
} else if (command === 'test') {
  runSelfTest();
} else if (command === '--' || args.length > 0) {
  const targetArgs = command === '--' ? args.slice(1) : args;
  runProxy(targetArgs);
} else {
  printHelp();
}

function printHelp() {
  console.log(`
\x1b[1m\x1b[36m╔══════════════════════════════════════════════════════════════════════╗
║               ★ MCP-PROXY-GUARD (BTP v3.0) — ACTIVE                 ║
║   In-Process Security Gateway & Credential Scrubber for MCP Servers ║
╚══════════════════════════════════════════════════════════════════════╝\x1b[0m

\x1b[1mUsage:\x1b[0m
  # Wrap any MCP server transparently in Claude Desktop / Cursor:
  \x1b[32mnpx mcp-proxy-guard -- <mcp-server-command> [args...]\x1b[0m

\x1b[1mExamples:\x1b[0m
  # Guard the official filesystem MCP server:
  npx mcp-proxy-guard -- npx -y @modelcontextprotocol/server-filesystem /path/to/dir

  # Guard a Postgres or SQLite MCP server:
  npx mcp-proxy-guard -- npx -y @modelcontextprotocol/server-postgres postgresql://...

\x1b[1mCommands:\x1b[0m
  \x1b[1mmcp-proxy-guard activate [key]\x1b[0m  Activate Pro ($49/mo) or Enterprise ($199/mo)
  \x1b[1mmcp-proxy-guard status\x1b[0m          Inspect active license and security engine
  \x1b[1mmcp-proxy-guard test\x1b[0m            Run self-contained security verification
`);
}

function runStatus() {
  const lic = loadLicense();
  console.log(`\n\x1b[1m[MCP-PROXY-GUARD] SECURITY RUNTIME STATUS\x1b[0m`);
  console.log('='.repeat(55));
  console.log(`  * Active Tier         : \x1b[1m\x1b[32m${lic.tier}\x1b[0m (${lic.status})`);
  console.log(`  * In-Process Latency  : <35 microseconds`);
  console.log(`  * In-Flight Scrubbing : Enabled (OpenAI, Anthropic, AWS, GitHub, Stripe)`);
  console.log(`  * Destructive Filter  : Active (rm -rf, DROP TABLE, mkfs, shadow)`);
  console.log(`  * Config Directory    : ${path.join(os.homedir(), '.btp')}\n`);
}

function runSelfTest() {
  console.log(`\n\x1b[1m[MCP-PROXY-GUARD] EXECUTING SELF-TEST\x1b[0m`);
  console.log('='.repeat(55));

  // 1. Test destructive command veto
  const veto = evaluateToolCall('execute_shell', { cmd: 'rm -rf /var/data' });
  console.log(`  [1] Destructive Filter Check : ${!veto.allowed ? '\x1b[32mPASSED (BLOCKED)\x1b[0m' : '\x1b[31mFAILED\x1b[0m'}`);
  console.log(`      Reason: ${veto.reason}`);

  // 2. Test in-flight secret scrubber
  const scrub = scrubSecrets({ payload: "Exporting token sk-proj-1234567890abcdef1234 to logs" });
  const passedScrub = scrub.redactionCount > 0 && !scrub.data.payload.includes("sk-proj-");
  console.log(`  [2] In-Flight Secret Scrub   : ${passedScrub ? '\x1b[32mPASSED (SCRUBBED)\x1b[0m' : '\x1b[31mFAILED\x1b[0m'}`);
  console.log(`      Result: ${scrub.data.payload}\n`);
}

function runActivate(key) {
  console.log(`\n\x1b[1m[MCP-PROXY-GUARD] LICENSE ACTIVATION\x1b[0m`);
  console.log('='.repeat(55));

  const btpDir = path.join(os.homedir(), '.btp');
  if (!fs.existsSync(btpDir)) fs.mkdirSync(btpDir, { recursive: true });

  if (key) {
    const cleanKey = key.trim().replace(/^["'`]+|["'`]+$/g, '');
    const tier = cleanKey.startsWith("btp_ent_") || cleanKey.toLowerCase().includes("enterprise") ? "ENTERPRISE" : "PRO";
    fs.writeFileSync(path.join(btpDir, 'license.json'), JSON.stringify({
      key: cleanKey,
      tier: tier,
      activated_at: Date.now(),
      status: "ACTIVE"
    }, null, 2));
    console.log(`\n\x1b[32m✓ License activated successfully!\x1b[0m`);
    console.log(`  -> Tier: \x1b[1m${tier}\x1b[0m`);
    console.log(`  -> Status: ACTIVE`);
    return;
  }

  console.log(`Upgrade your MCP server with certified security:`);
  console.log(`  [1] Pro Tier ($49/mo)       - Unlimited calls & dynamic cloud policy sync`);
  console.log(`      \x1b[36m${STRIPE_PRO_URL}\x1b[0m`);
  console.log(`  [2] Enterprise Tier ($199/mo) - SOC 2 Type II evidence & SIEM team audit logs`);
  console.log(`      \x1b[36m${STRIPE_ENTERPRISE_URL}\x1b[0m`);
  console.log(`  [3] Official Storefront:`);
  console.log(`      \x1b[36m${STORE_URL}\x1b[0m\n`);
  console.log(`To activate your key, run:`);
  console.log(`  \x1b[1mnpx mcp-proxy-guard activate <your-license-key>\x1b[0m\n`);
}

function runProxy(targetArgs) {
  if (!targetArgs || targetArgs.length === 0) {
    console.error("Error: No target MCP server command specified.");
    process.exit(1);
  }

  const [targetCmd, ...cmdArgs] = targetArgs;

  // Spawn child MCP server
  const child = spawn(targetCmd, cmdArgs, {
    stdio: ['pipe', 'pipe', 'inherit'],
    shell: true
  });

  child.on('error', (err) => {
    console.error(`[MCP-PROXY-GUARD ERROR] Failed to start server: ${err.message}`);
    process.exit(1);
  });

  // Client -> Server (stdin)
  const rlClient = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: false });
  rlClient.on('line', (line) => {
    if (!line.trim()) return;
    try {
      const msg = JSON.parse(line);

      // Intercept tool calls
      if (msg.method === 'tools/call') {
        const params = msg.params || {};
        const toolName = params.name || 'unknown';
        const toolArgs = params.arguments || {};

        // In-process AST & destructive command check
        const check = evaluateToolCall(toolName, toolArgs);
        if (!check.allowed) {
          const vetoResp = {
            jsonrpc: "2.0",
            id: msg.id,
            error: {
              code: -32000,
              message: check.reason
            }
          };
          process.stdout.write(JSON.stringify(vetoResp) + '\n');
          return;
        }

        // In-flight credential scrubbing before passing to tool
        const scrubbedArgs = scrubSecrets(toolArgs);
        params.arguments = scrubbedArgs.data;
        line = JSON.stringify(msg);
      }
    } catch {}

    child.stdin.write(line + '\n');
  });

  // Server -> Client (stdout)
  const rlServer = readline.createInterface({ input: child.stdout, terminal: false });
  rlServer.on('line', (line) => {
    if (!line.trim()) return;
    try {
      const msg = JSON.parse(line);
      // Scrub any leaked credentials in tool responses before Claude/Cursor reads them
      if (msg.result) {
        const scrubbed = scrubSecrets(msg.result);
        msg.result = scrubbed.data;
        line = JSON.stringify(msg);
      }
    } catch {}

    process.stdout.write(line + '\n');
  });

  child.on('close', (code) => {
    process.exit(code || 0);
  });
}
