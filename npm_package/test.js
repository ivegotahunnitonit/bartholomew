import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { rfc8785Canonicalize, verifyBtpReceipt } from './index.js';
import crypto from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function runTests() {
  console.log("==========================================================");
  console.log("  BTP Node.js Verifier Self-Test Suite");
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

  console.log(`[01/03] Payload RFC 8785 Canonicalization: ${canonHex === tv.canonical_payload_utf8_hex ? "PASS" : "FAIL"}`);
  console.log(`[02/03] SHA-256 Hash Calculation:          ${canonHash === tv.canonical_payload_sha256 ? "PASS" : "FAIL"}`);

  // 2. Verify Attestation
  const res = verifyBtpReceipt(
    tv.attestation_packet,
    tv.candidate_payload_raw,
    [tv.trusted_root_pubkey_hex],
    "Agent-AutoGen-02",
    1755648100
  );

  console.log(`[03/03] Ed25519 Cryptographic Verification: ${res.ok === tv.expected_verification_result ? "PASS" : "FAIL"}`);
  console.log("==========================================================");

  if (canonHex === tv.canonical_payload_utf8_hex && canonHash === tv.canonical_payload_sha256 && res.ok === tv.expected_verification_result) {
    console.log("ALL TESTS PASSED (100.00%)");
    process.exit(0);
  } else {
    console.error("TEST FAILED");
    process.exit(1);
  }
}

runTests();
