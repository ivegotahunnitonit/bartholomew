import { OAuthStateManager } from './oauth_state_security.js';
import assert from 'assert';

console.log('=== Running OAuth State Manager Tests (Issue #1476) ===');

const manager = new OAuthStateManager(2); // 2 second TTL for testing

// Test 1: Generate valid 32-byte (64 hex char) token
const token = manager.generateState('session_123');
assert.strictEqual(typeof token, 'string');
assert.strictEqual(token.length, 64);
console.log(' Test 1 Passed: Generates 32-byte secure hex token');

// Test 2: Valid token passes validation
const isValid = manager.validateAndConsumeState('session_123', token);
assert.strictEqual(isValid, true);
console.log(' Test 2 Passed: Valid token consumes successfully');

// Test 3: Token is single-use (replay attack fails)
const isReplayed = manager.validateAndConsumeState('session_123', token);
assert.strictEqual(isReplayed, false);
console.log(' Test 3 Passed: Replay attempt fails (single-use enforced)');

// Test 4: Mismatched session fails
const token2 = manager.generateState('session_abc');
const isWrongSession = manager.validateAndConsumeState('session_xyz', token2);
assert.strictEqual(isWrongSession, false);
console.log(' Test 4 Passed: Mismatched session fails validation');

// Test 5: Invalid/tampered token fails
const token3 = manager.generateState('session_tamper');
const tamperedToken = token3.substring(0, 63) + (token3[63] === '0' ? '1' : '0');
const isTampered = manager.validateAndConsumeState('session_tamper', tamperedToken);
assert.strictEqual(isTampered, false);
console.log(' Test 5 Passed: Tampered token fails timing-safe check');

console.log('All 5 unit tests passed successfully!');
