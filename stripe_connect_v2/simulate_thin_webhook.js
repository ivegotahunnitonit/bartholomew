/**
 * ============================================================================
 * STRIPE CONNECT V2 THIN WEBHOOK SIMULATOR
 * ============================================================================
 * 
 * Simulates Stripe V2 thin events for local testing without requiring the Stripe CLI.
 * 
 * Usage:
 *   node stripe_connect_v2/simulate_thin_webhook.js [requirements|capability]
 */

import http from 'node:http';
import crypto from 'node:crypto';

const TARGET_PORT = process.env.PORT || 4242;
const WEBHOOK_PATH = '/api/webhooks/thin';
const WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || 'whsec_test_simulation_secret_12345';

const eventType = process.argv[2] || 'requirements';

// Construct simulated V2 Thin Event payload
const thinEventPayload = {
  id: `evt_test_thin_${Date.now()}`,
  object: 'event',
  type: eventType === 'capability' 
    ? 'v2.core.account[.recipient].capability_status_updated'
    : 'v2.core.account[requirements].updated',
  created: Math.floor(Date.now() / 1000),
  livemode: false,
  related_object: {
    id: 'acct_test_simulated_001',
    type: 'account',
    url: '/v2/core/accounts/acct_test_simulated_001',
  },
  context: 'connect',
};

const payloadString = JSON.stringify(thinEventPayload);
const timestamp = Math.floor(Date.now() / 1000);

// Generate valid Stripe signature header: t=timestamp,v1=HMAC_SHA256(timestamp.payload, secret)
const signedPayload = `${timestamp}.${payloadString}`;
const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
hmac.update(signedPayload);
const signature = hmac.digest('hex');
const stripeSignatureHeader = `t=${timestamp},v1=${signature}`;

console.log('='.repeat(70));
console.log('⚡ SIMULATING STRIPE V2 THIN EVENT DISPATCH');
console.log('='.repeat(70));
console.log(`• Event Type  : ${thinEventPayload.type}`);
console.log(`• Event ID    : ${thinEventPayload.id}`);
console.log(`• Target Acct : ${thinEventPayload.related_object.id}`);
console.log(`• Endpoint    : http://localhost:${TARGET_PORT}${WEBHOOK_PATH}`);
console.log('='.repeat(70));

const options = {
  hostname: 'localhost',
  port: TARGET_PORT,
  path: WEBHOOK_PATH,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payloadString),
    'stripe-signature': stripeSignatureHeader,
  },
};

const req = http.request(options, (res) => {
  let responseData = '';
  res.on('data', (chunk) => { responseData += chunk; });
  res.on('end', () => {
    console.log(`[Response] HTTP ${res.statusCode}: ${responseData}`);
    if (res.statusCode === 200) {
      console.log('✓ Thin event successfully parsed and processed by server!');
    } else {
      console.log('! Note: If using real Stripe verification, start server with STRIPE_WEBHOOK_SECRET matching the test secret.');
    }
  });
});

req.on('error', (err) => {
  console.error(`! Connection error (is the server running on port ${TARGET_PORT}?):`, err.message);
});

req.write(payloadString);
req.end();
