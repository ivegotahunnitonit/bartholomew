import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { rfc8785Canonicalize, verifyBtpReceipt, verifyTurnReceiptChaining, scrubSensitiveCredentials } from './index.js';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function runTests() {
  console.log("==========================================================");
  console.log("  BTP v2.4 Node.js Verifier Self-Test Suite");
  console.log("==========================================================");

  let vectorPath = path.join(__dirname, "..", "btp_test_vectors.json");
  if (!fs.existsSync(vectorPath)) {
    vectorPath = path.join(__dirname, "btp_test_vectors.json");
  }

  const tv = JSON.parse(fs.readFileSync(vectorPath, "utf8"));
  
  // 1. Canonicalize payload
  const canonBytes = rfc8785Canonicalize(tv.candidate_payload_raw);
  const canonHex = canonBytes.toString("hex");
  const canonHash = crypto.createHash("sha256").update(canonBytes).digest("hex");

  console.log(`[01/05] Payload RFC 8785 Canonicalization: ${canonHex === tv.canonical_payload_utf8_hex ? "PASS" : "FAIL"}`);
  console.log(`[02/05] SHA-256 Hash Calculation:          ${canonHash === tv.canonical_payload_sha256 ? "PASS" : "FAIL"}`);

  // 2. Verify Attestation
  const res = verifyBtpReceipt(
    tv.attestation_packet,
    tv.candidate_payload_raw,
    [tv.trusted_root_pubkey_hex],
    "Agent-AutoGen-02",
    1755648100
  );

  console.log(`[03/05] Ed25519 Cryptographic Verification: ${res.ok === tv.expected_verification_result ? "PASS" : "FAIL"}`);

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
  console.log(`[04/05] In-Flight Multi-Key Scrubber:      ${scrubOk ? "PASS" : "FAIL"}`);

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
  console.log(`[05/05] Merkle Turn Receipt Hash Chaining: ${chainOk ? "PASS" : "FAIL"}`);

  console.log("==========================================================");

  if (canonHex === tv.canonical_payload_utf8_hex && 
      canonHash === tv.canonical_payload_sha256 && 
      res.ok === tv.expected_verification_result && 
      scrubOk && 
      chainOk) {
    console.log("ALL 5 NODE.JS TESTS PASSED (100.00%)");
    process.exit(0);
  } else {
    console.error("TEST FAILED");
    process.exit(1);
  }
}

runTests();
