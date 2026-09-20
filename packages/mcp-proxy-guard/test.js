import assert from 'assert';
import { scrubSecrets, evaluateToolCall, loadLicense } from './index.js';

console.log("Running mcp-proxy-guard verification suite...");

// Test 1: Destructive shell command blocked
const vetoShell = evaluateToolCall('run_shell', { command: 'rm -rf /' });
assert.strictEqual(vetoShell.allowed, false, "Should block rm -rf");
console.log("✓ Test 1 Passed: Intercepted destructive shell command");

// Test 2: Destructive SQL dropped
const vetoSql = evaluateToolCall('query_db', { sql: 'DROP TABLE users CASCADE;' });
assert.strictEqual(vetoSql.allowed, false, "Should block DROP TABLE");
console.log("✓ Test 2 Passed: Intercepted destructive SQL mutation");

// Test 3: Safe tool allowed
const safeTool = evaluateToolCall('query_db', { sql: 'SELECT id, email FROM users LIMIT 10;' });
assert.strictEqual(safeTool.allowed, true, "Should allow safe SELECT query");
console.log("✓ Test 3 Passed: Allowed safe tool execution");

// Test 4: Secret scrubbing
const secretPayload = {
  openai: ["sk-proj", "synthetic_test_token_1234567890"].join("-"),
  aws: ["AKIA", "IOSFODNN7EXAMPLE"].join(""),
  message: "Normal message"
};
const scrubbed = scrubSecrets(secretPayload);
assert.strictEqual(scrubbed.redactionCount, 2, "Should redact 2 credentials");
assert.ok(!JSON.stringify(scrubbed.data).includes("sk-proj-"), "OpenAI token must be scrubbed");
assert.ok(!JSON.stringify(scrubbed.data).includes("AKIA"), "AWS token must be scrubbed");
console.log("✓ Test 4 Passed: Scrubbed in-flight secrets");

console.log("\nALL MCP-PROXY-GUARD TESTS PASSED 100% CLEAN!");
