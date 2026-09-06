/**
 * Cookbook Recipe: TypeScript / Node.js Autonomous Agent Guard
 * ==============================================================
 * Demonstrates guarding Node.js / TypeScript autonomous agent runtimes
 * using the official 'btp-guard' npm module.
 * 
 * Install:
 *   npm install btp-guard
 */

import { BartholomewVerifier } from './btp_verifier.js';

interface AgentToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

export class TypeScriptAgentGuard {
  private verifier: BartholomewVerifier;

  constructor(trustedAuthorityPubkey: string) {
    this.verifier = new BartholomewVerifier([trustedAuthorityPubkey]);
  }

  /**
   * Pre-flight invariant check for TypeScript agent tool calls.
   */
  public async guardToolCall(toolCall: AgentToolCall): Promise<{ allowed: boolean; reason?: string }> {
    const serializedArgs = JSON.stringify(toolCall.arguments).toLowerCase();

    // 1. Detect destructive shell injection
    if (serializedArgs.includes('rm -rf') || serializedArgs.includes('drop table')) {
      return {
        allowed: false,
        reason: `BTP-TS-001: Destructive payload pattern detected in tool '${toolCall.name}'`
      };
    }

    // 2. Detect secret exfiltration attempts
    if (serializedArgs.includes('/etc/shadow') || serializedArgs.includes('aws_secret_access_key')) {
      return {
        allowed: false,
        reason: `BTP-TS-002: Secret exfiltration attempt detected in tool '${toolCall.name}'`
      };
    }

    return { allowed: true };
  }
}

// Example usage
async function runExample() {
  console.log('================================================================');
  console.log('  BTP Global Cookbook: TypeScript / Node.js Agent Guard Demo');
  console.log('================================================================');

  const guard = new TypeScriptAgentGuard('dummy_trusted_pubkey_hex');

  // 1. Safe tool call
  const safeCall: AgentToolCall = {
    name: 'fetch_stock_quote',
    arguments: { ticker: 'AAPL', timeframe: '1D' }
  };
  const res1 = await guard.guardToolCall(safeCall);
  console.log(`[Safe Tool] Allowed: ${res1.allowed}`);

  // 2. Dangerous tool call
  const maliciousCall: AgentToolCall = {
    name: 'run_analysis',
    arguments: { query: 'AAPL; rm -rf /var/data' }
  };
  const res2 = await guard.guardToolCall(maliciousCall);
  console.log(`[Malicious Tool] Allowed: ${res2.allowed}, Reason: ${res2.reason}`);
}

if (require.main === module) {
  runExample();
}
