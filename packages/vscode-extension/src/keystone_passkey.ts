/**
 * Bartholomew Keystone (BTP Passkey Protocol v1.0.0)
 * ===================================================
 * Ephemeral, cryptographically signed capability tokens granting
 * autonomous AI agents fine-grained clearance across IDEs, programs, and web searches.
 */

declare const process: any;
declare const require: any;
const crypto = require('crypto');

export interface KeystoneScope {
  files?: {
    allow_read?: string[];
    allow_write?: string[];
    deny?: string[];
  };
  commands?: {
    allow_exec?: string[];
    deny_exec?: string[];
  };
  network?: {
    allow_domains?: string[];
    allow_search?: boolean;
    deny_domains?: string[];
  };
  budget?: {
    max_spend_usd?: number;
    max_tokens?: number;
  };
}

export interface KeystonePasskey {
  passkey_id: string;
  agent_id: string;
  issuer: string;
  issued_at: string;
  expires_at: string;
  scopes: KeystoneScope;
  payload_hash: string;
  signature: string;
}

export interface ClearanceResult {
  verdict: 'ALLOW' | 'DENY';
  status: 'CLEARANCE_GRANTED' | 'OUT_OF_SCOPE' | 'PASSKEY_EXPIRED' | 'INVALID_SIGNATURE';
  reason: string;
  latency_us: number;
  rule_id: string;
}

export class KeystoneEngine {
  private signingSecret: string;

  constructor(signingSecret?: string) {
    this.signingSecret = signingSecret || 'keystone-root-dev-authority';
  }

  /**
   * Issues a signed capability passkey for an autonomous agent.
   */
  public issuePasskey(
    agentId: string,
    scopes: KeystoneScope,
    ttlMinutes: number = 60
  ): KeystonePasskey {
    const passkeyId = 'key_' + crypto.randomBytes(8).toString('hex');
    const now = new Date();
    const issuedAt = now.toISOString();
    const expiresAt = new Date(now.getTime() + ttlMinutes * 60 * 1000).toISOString();

    const canonicalData = JSON.stringify({
      passkey_id: passkeyId,
      agent_id: agentId,
      issuer: 'Bartholomew-Keystone-Authority',
      issued_at: issuedAt,
      expires_at: expiresAt,
      scopes: scopes
    });

    const payloadHash = crypto.createHash('sha256').update(canonicalData).digest('hex');
    const signature = crypto.createHmac('sha256', this.signingSecret)
      .update(payloadHash)
      .digest('hex');

    return {
      passkey_id: passkeyId,
      agent_id: agentId,
      issuer: 'Bartholomew-Keystone-Authority',
      issued_at: issuedAt,
      expires_at: expiresAt,
      scopes: scopes,
      payload_hash: payloadHash,
      signature: signature
    };
  }

  /**
   * Verifies the cryptographic signature and timestamp of a passkey.
   */
  public verifyPasskey(passkey: KeystonePasskey): boolean {
    const now = new Date().getTime();
    const expiry = new Date(passkey.expires_at).getTime();
    if (now > expiry) return false;

    const canonicalData = JSON.stringify({
      passkey_id: passkey.passkey_id,
      agent_id: passkey.agent_id,
      issuer: passkey.issuer,
      issued_at: passkey.issued_at,
      expires_at: passkey.expires_at,
      scopes: passkey.scopes
    });

    const expectedHash = crypto.createHash('sha256').update(canonicalData).digest('hex');
    const expectedSig = crypto.createHmac('sha256', this.signingSecret)
      .update(expectedHash)
      .digest('hex');

    return passkey.signature === expectedSig;
  }

  /**
   * Validates whether a proposed agent action falls within its signed passkey clearance (<15µs).
   */
  public evaluateAction(
    passkey: KeystonePasskey,
    actionType: 'FILE_READ' | 'FILE_WRITE' | 'COMMAND_EXEC' | 'NETWORK_REQUEST' | 'FINANCIAL_SPEND',
    target: string,
    spendAmountUsd?: number
  ): ClearanceResult {
    const start = process.hrtime.bigint();

    // 1. Signature & Expiration Check
    if (!this.verifyPasskey(passkey)) {
      const end = process.hrtime.bigint();
      return {
        verdict: 'DENY',
        status: 'INVALID_SIGNATURE',
        reason: 'Passkey signature is invalid or clearance has expired.',
        latency_us: Number(Number(end - start) / 1000).toFixed(2) as any,
        rule_id: 'KEYSTONE-001'
      };
    }

    const scopes = passkey.scopes;
    const targetNorm = target.toLowerCase();

    // 2. File Scopes
    if (actionType === 'FILE_READ' || actionType === 'FILE_WRITE') {
      const fileScope = scopes.files || {};
      const denyList = fileScope.deny || ['.env', 'secrets', 'credentials.json', 'id_rsa'];
      for (const denied of denyList) {
        if (targetNorm.includes(denied.toLowerCase())) {
          const end = process.hrtime.bigint();
          return {
            verdict: 'DENY',
            status: 'OUT_OF_SCOPE',
            reason: `Access to protected target '${target}' is denied by passkey policy.`,
            latency_us: Number(Number(end - start) / 1000).toFixed(2) as any,
            rule_id: 'KEYSTONE-FILE-DENIED'
          };
        }
      }

      if (actionType === 'FILE_WRITE' && fileScope.allow_write && fileScope.allow_write.length > 0) {
        const allowed = fileScope.allow_write.some(pat => targetNorm.includes(pat.toLowerCase()));
        if (!allowed) {
          const end = process.hrtime.bigint();
          return {
            verdict: 'DENY',
            status: 'OUT_OF_SCOPE',
            reason: `Write target '${target}' falls outside authorized write scopes [${fileScope.allow_write.join(', ')}].`,
            latency_us: Number(Number(end - start) / 1000).toFixed(2) as any,
            rule_id: 'KEYSTONE-WRITE-SCOPE'
          };
        }
      }
    }

    // 3. Command Execution Scopes
    if (actionType === 'COMMAND_EXEC') {
      const cmdScope = scopes.commands || {};
      const denyCmds = cmdScope.deny_exec || ['rm', 'curl', 'wget', 'sudo', 'mkfs', 'dd'];
      for (const dc of denyCmds) {
        const regex = new RegExp(`\\b${dc}\\b`, 'i');
        if (regex.test(targetNorm)) {
          const end = process.hrtime.bigint();
          return {
            verdict: 'DENY',
            status: 'OUT_OF_SCOPE',
            reason: `Execution of restricted command '${dc}' blocked by passkey clearance.`,
            latency_us: Number(Number(end - start) / 1000).toFixed(2) as any,
            rule_id: 'KEYSTONE-CMD-DENIED'
          };
        }
      }
    }

    // 4. Network / Search Scopes
    if (actionType === 'NETWORK_REQUEST') {
      const netScope = scopes.network || {};
      if (netScope.allow_domains && netScope.allow_domains.length > 0) {
        const isAllowedDomain = netScope.allow_domains.some(dom => targetNorm.includes(dom.toLowerCase()));
        if (!isAllowedDomain) {
          const end = process.hrtime.bigint();
          return {
            verdict: 'DENY',
            status: 'OUT_OF_SCOPE',
            reason: `Network destination '${target}' is not in authorized domain whitelist.`,
            latency_us: Number(Number(end - start) / 1000).toFixed(2) as any,
            rule_id: 'KEYSTONE-NET-WHITELIST'
          };
        }
      }
    }

    // 5. Budget Scopes
    if (actionType === 'FINANCIAL_SPEND' || (spendAmountUsd && spendAmountUsd > 0)) {
      const maxSpend = scopes.budget?.max_spend_usd ?? 50.0;
      const spend = spendAmountUsd || 0;
      if (spend > maxSpend) {
        const end = process.hrtime.bigint();
        return {
          verdict: 'DENY',
          status: 'OUT_OF_SCOPE',
          reason: `Requested transaction spend $${spend.toFixed(2)} exceeds passkey authorization ceiling $${maxSpend.toFixed(2)}.`,
          latency_us: Number(Number(end - start) / 1000).toFixed(2) as any,
          rule_id: 'KEYSTONE-BUDGET-CAP'
        };
      }
    }

    const end = process.hrtime.bigint();
    return {
      verdict: 'ALLOW',
      status: 'CLEARANCE_GRANTED',
      reason: 'Action verified within active passkey clearance boundaries.',
      latency_us: Number(Number(end - start) / 1000).toFixed(2) as any,
      rule_id: 'KEYSTONE-PASS-000'
    };
  }
}
