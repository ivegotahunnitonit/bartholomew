import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { rfc8785Canonicalize, verifyBtpReceipt, verifyTurnReceiptChaining, scrubSensitiveCredentials, evaluateIntent, verifyReceipt } from './index.js';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function runTests() {
  console.log("==========================================================");
  console.log("  BTP v5.4.10 Node.js Verifier Self-Test Suite");
  console.log("==========================================================");

  let vectorPath = path.join(__dirname, "btp_test_vectors.json");
  if (!fs.existsSync(vectorPath)) {
    vectorPath = path.join(__dirname, "..", "btp_test_vectors.json");
  }

  const tv = JSON.parse(fs.readFileSync(vectorPath, "utf8"));
  
  // 1. Canonicalize payload
  const canonBytes = rfc8785Canonicalize(tv.candidate_payload_raw);
  const canonHex = canonBytes.toString("hex");
  const canonHash = crypto.createHash("sha256").update(canonBytes).digest("hex");

  console.log(`[01/07] Payload RFC 8785 Canonicalization: ${canonHex === tv.canonical_payload_utf8_hex ? "PASS" : "FAIL"}`);
  console.log(`[02/07] SHA-256 Hash Calculation:          ${canonHash === tv.canonical_payload_sha256 ? "PASS" : "FAIL"}`);

  // 2. Verify Attestation
  const res = verifyBtpReceipt(
    tv.attestation_packet,
    tv.candidate_payload_raw,
    [tv.trusted_root_pubkey_hex],
    "Agent-AutoGen-02",
    1755648100
  );

  console.log(`[03/07] Ed25519 Cryptographic Verification: ${res.ok === tv.expected_verification_result ? "PASS" : "FAIL"}`);

  // 3. Test In-Flight Sensitive Credential Scrubber
  const samplePayload = {
    user: "alice",
    api_key: "sk-proj-00000000000000000000000000000000",
    anthropic: "sk-ant-123456789012345678901234567890",
    aws: "AKIAIOSFODNN7EXAMPLE"
  };
  const scrubRes = scrubSensitiveCredentials(samplePayload);
  const scrubOk = scrubRes.redactionCount === 3 && 
                  scrubRes.data.api_key === "[REDACTED_OPENAI_KEY_BTP]" &&
                  scrubRes.data.anthropic === "[REDACTED_ANTHROPIC_KEY_BTP]" &&
                  scrubRes.data.aws === "[REDACTED_AWS_KEY_BTP]";
  console.log(`[04/07] In-Flight Multi-Key Scrubber:      ${scrubOk ? "PASS" : "FAIL"}`);

  // 4. Test Chained Merkle Turn Receipt Verification
  const parentHash = "029807446fb2b9ada32c113e93926b39029807446fb2b9ada32c113e93926b39";
  const mockReceipt = {
    turn_receipt: {
      protocol: "BTP/2.4",
      turn_index: 2,
      parent_receipt_hash: parentHash,
      receipt_hash: "952abfb3eee25017f2d751ceb91d2cc9952abfb3eee25017f2d751ceb91d2cc9",
      transaction_state: "COMMITTED"
    }
  };
  const chainRes = verifyTurnReceiptChaining(parentHash, mockReceipt);
  const chainTampered = verifyTurnReceiptChaining("wrong_parent_hash", mockReceipt);
  const chainOk = chainRes.ok && !chainTampered.ok;
  console.log(`[05/07] Merkle Turn Receipt Hash Chaining: ${chainOk ? "PASS" : "FAIL"}`);

  // 5. Test evaluateIntent allowed query
  const safeIntent = evaluateIntent({
    agentId: "agent-007",
    actionType: "EXECUTE_SQL",
    payload: { query: "SELECT id, name FROM users WHERE active = 1" }
  });
  const safeIntentOk = safeIntent.allowed === true && safeIntent.verdict === "ALLOW" && safeIntent.latencyUs < 50000;
  console.log(`[06/07] In-Process Intent Gate (Safe):     ${safeIntentOk ? "PASS" : "FAIL"} (${safeIntent.latencyUs.toFixed(2)} µs)`);

  // 6. Test evaluateIntent blocked destructive query + receipt verification
  const blockedIntent = evaluateIntent({
    agentId: "agent-malicious",
    actionType: "EXECUTE_BASH",
    payload: { cmd: "rm -rf / --no-preserve-root" }
  });
  const receiptValid = verifyReceipt(blockedIntent);
  const blockedIntentOk = blockedIntent.allowed === false && blockedIntent.verdict === "DENY" && receiptValid === true;
  console.log(`[07/07] In-Process Intent Gate (Blocked):  ${blockedIntentOk ? "PASS" : "FAIL"} (Signature Valid: ${receiptValid})`);

  console.log("==========================================================");

  if (canonHex === tv.canonical_payload_utf8_hex && 
      canonHash === tv.canonical_payload_sha256 && 
      res.ok === tv.expected_verification_result && 
      scrubOk && 
      chainOk &&
      safeIntentOk &&
      blockedIntentOk) {
    console.log("ALL 7 NODE.JS TESTS PASSED (100.00%)");
    process.exit(0);
  } else {
    console.error("TEST FAILED");
    process.exit(1);
  }
}

runTests();
