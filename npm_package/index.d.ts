/**
 * TypeScript Type Definitions for btp-guard (BTP v2.4)
 */

export interface VerificationResult {
  ok: boolean;
  msg: string;
}

export interface ScrubResult {
  data: any;
  redactionCount: number;
}

export interface BtpAttestation {
  protocol_version: string;
  authority: string;
  authority_pubkey: string;
  nonce: string;
  issued_at_unix: number;
  expires_at_unix: number;
  originating_agent: string;
  target_recipient: string;
  action_type: string;
  action_payload_hash: string;
  policy_id: string;
  policy_hash: string;
  capability_scope: string[];
  verdict: "ALLOW" | "DENY";
  reason: string;
  sandbox_receipt?: any;
  evaluation_latency_us?: number;
}

export interface BtpReceiptPacket {
  attestation: BtpAttestation;
  signature: string;
}

export interface BtpTurnReceipt {
  protocol: string;
  turn_index: number;
  parent_receipt_hash: string;
  receipt_hash: string;
  tool_name: string;
  action_payload_hash: string;
  scrubbed_secrets_count: number;
  transaction_state: "COMMITTED" | "ROLLED_BACK";
  timestamp_unix: number;
  authority_pubkey: string;
  signature: string;
}

/**
 * Encodes a JSON-serializable value into RFC 8785 canonical UTF-8 bytes.
 */
export function rfc8785Canonicalize(val: any): Buffer;

/**
 * 100% Offline independent BTP receipt verifier.
 */
export function verifyBtpReceipt(
  receiptPacket: BtpReceiptPacket | string,
  candidatePayload: any,
  trustedPubkeys: string | string[],
  expectedRecipient?: string,
  evalTimestamp?: number,
  requiredPolicyHash?: string,
  allowedCapabilities?: string[]
): VerificationResult;

/**
 * Verifies BTP v2.4 Chained Merkle Turn Receipt.
 */
export function verifyTurnReceiptChaining(
  parentReceiptHash: string,
  turnReceipt: BtpTurnReceipt | string,
  trustedPubkeys?: string | string[]
): VerificationResult;

/**
 * In-flight sensitive credential scrubber for Model Context Protocol payloads.
 */
export function scrubSensitiveCredentials(data: any): ScrubResult;

/**
 * Runs the formal conformance test suite.
 */
export function runNodeJsConformance(): boolean;
