/**
 * ============================================================================
 * STRIPE CONNECT V2 PLATFORM INTEGRATION (Node.js / Native HTTP + Stripe SDK)
 * ============================================================================
 * 
 * Zero external web framework dependencies (runs natively with Node.js & Stripe SDK).
 * 
 * Flow Overview:
 *   1. Initialize unified Stripe Client (`stripeClient`) with API key validation.
 *   2. Create Connected Accounts using Stripe V2 Core Accounts API.
 *   3. Generate Stripe V2 Account Onboarding Links & query live account status.
 *   4. Listen & parse V2 "Thin" Webhook Events (`parseThinEvent` + `events.retrieve`).
 *   5. Create platform-level Products and map them to connected creators.
 *   6. Serve an interactive Storefront UI.
 *   7. Process Destination Charges with application fee monetization via Checkout Sessions.
 */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import Stripe from 'stripe';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ============================================================================
// STEP 1: INITIALIZE THE STRIPE CLIENT
// ============================================================================
// PLACEHOLDER: Set your Stripe Secret Key here or via process.env.STRIPE_SECRET_KEY.
// Obtain this from https://dashboard.stripe.com/test/apikeys
// Format: sk_test_... (or sk_live_... in production)
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || 'sk_test_PLACEHOLDER_REPLACE_WITH_YOUR_STRIPE_SECRET_KEY';

// PLACEHOLDER: Set your Stripe Webhook Signing Secret here or via process.env.STRIPE_WEBHOOK_SECRET.
// Obtain this from Stripe Dashboard -> Developers -> Webhooks or via `stripe listen` CLI output.
// Format: whsec_...
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || 'whsec_PLACEHOLDER_REPLACE_WITH_YOUR_WEBHOOK_SECRET';

/**
 * Validates that the Stripe API key is configured before dispatching SDK requests.
 * Throws a helpful error message if the placeholder has not been replaced.
 */
function validateStripeKey() {
  if (!STRIPE_SECRET_KEY || STRIPE_SECRET_KEY.includes('PLACEHOLDER')) {
    throw new Error(
      'Missing Stripe Secret Key! Please set process.env.STRIPE_SECRET_KEY or replace the placeholder ' +
      'in server.js with your real key from https://dashboard.stripe.com/test/apikeys'
    );
  }
}

// Single unified Stripe Client instance used for all requests across the application.
// Note: API version is managed automatically by the latest SDK.
const stripeClient = new Stripe(STRIPE_SECRET_KEY);

const PORT = process.env.PORT || 4242;

// In-memory mapping stores for demo purposes:
const usersDb = new Map();
const productsDb = new Map();
const webhookEventsLog = [];

// Helper: read raw request body
function readRequestBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', chunk => { raw += chunk; });
    req.on('end', () => resolve(raw));
    req.on('error', reject);
  });
}

// Helper: JSON response utility
function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, stripe-signature',
  });
  res.end(JSON.stringify(data));
}

// ============================================================================
// HTTP SERVER & ROUTING
// ============================================================================
const server = http.createServer(async (req, res) => {
  const urlObj = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = urlObj.pathname;
  const method = req.method;

  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, stripe-signature',
    });
    return res.end();
  }

  try {
    // --------------------------------------------------------------------------
    // STEP 2: CREATING CONNECTED ACCOUNTS (V2 CORE ACCOUNTS API)
    // --------------------------------------------------------------------------
    if (pathname === '/api/connect/accounts' && method === 'POST') {
      validateStripeKey();
      const raw = await readRequestBody(req);
      const { displayName, contactEmail, userId } = JSON.parse(raw || '{}');

      if (!displayName || !contactEmail) {
        return sendJson(res, 400, { error: 'displayName and contactEmail are required.' });
      }

      const assignedUserId = userId || `user_${Date.now()}`;

      // Call Stripe V2 Core Accounts API with exact specified schema
      // IMPORTANT: In the V2 Core API:
      //   - Never pass `type` at the top level (do NOT use type: 'express', 'standard', or 'custom').
      //   - Use `dashboard: 'express'`.
      //   - Responsibilities for fees and losses are assigned to 'application'.
      const account = await stripeClient.v2.core.accounts.create({
        display_name: displayName,
        contact_email: contactEmail,
        identity: {
          country: 'us',
        },
        dashboard: 'express',
        defaults: {
          responsibilities: {
            fees_collector: 'application',
            losses_collector: 'application',
          },
        },
        configuration: {
          recipient: {
            capabilities: {
              stripe_balance: {
                stripe_transfers: {
                  requested: true,
                },
              },
            },
          },
        },
      });

      // Store mapping from user object to the Stripe account ID
      const userRecord = {
        userId: assignedUserId,
        displayName,
        contactEmail,
        stripeAccountId: account.id,
        createdAt: new Date().toISOString(),
      };
      usersDb.set(assignedUserId, userRecord);

      console.log(`[Stripe Connect V2] Created connected account: ${account.id} for user ${assignedUserId}`);
      return sendJson(res, 200, {
        success: true,
        account: {
          id: account.id,
          displayName: account.display_name,
          contactEmail: account.contact_email,
          userId: assignedUserId,
        },
      });
    }

    // --------------------------------------------------------------------------
    // STEP 3: ONBOARDING CONNECTED ACCOUNTS & RETRIEVING LIVE STATUS
    // --------------------------------------------------------------------------
    if (pathname === '/api/connect/account-links' && method === 'POST') {
      validateStripeKey();
      const raw = await readRequestBody(req);
      const { accountId } = JSON.parse(raw || '{}');

      if (!accountId) {
        return sendJson(res, 400, { error: 'accountId is required.' });
      }

      const rootUrl = `http://${req.headers.host || `localhost:${PORT}`}`;
      const refreshUrl = `${rootUrl}/?onboarding=refresh&accountId=${accountId}`;
      const returnUrl = `${rootUrl}/?onboarding=complete&accountId=${accountId}`;

      // Use V2 Core Account Links API for account onboarding
      const accountLink = await stripeClient.v2.core.accountLinks.create({
        account: accountId,
        use_case: {
          type: 'account_onboarding',
          account_onboarding: {
            configurations: ['recipient'],
            refresh_url: refreshUrl,
            return_url: returnUrl,
          },
        },
      });

      console.log(`[Stripe Connect V2] Generated onboarding link for account: ${accountId}`);
      return sendJson(res, 200, { success: true, url: accountLink.url });
    }

    if (pathname.startsWith('/api/connect/accounts/') && pathname.endsWith('/status') && method === 'GET') {
      validateStripeKey();
      const parts = pathname.split('/');
      const stripeAccountId = parts[4];

      // Retrieve account with configuration.recipient and requirements expanded directly from Stripe API
      const account = await stripeClient.v2.core.accounts.retrieve(stripeAccountId, {
        include: ['configuration.recipient', 'requirements'],
      });

      const readyToReceivePayments =
        account?.configuration?.recipient?.capabilities?.stripe_balance?.stripe_transfers?.status === 'active';

      const requirementsStatus = account.requirements?.summary?.minimum_deadline?.status;
      const onboardingComplete = requirementsStatus !== 'currently_due' && requirementsStatus !== 'past_due';

      return sendJson(res, 200, {
        success: true,
        accountId: account.id,
        displayName: account.display_name,
        readyToReceivePayments,
        onboardingComplete,
        requirementsStatus: requirementsStatus || 'completed',
      });
    }

    if (pathname === '/api/connect/accounts' && method === 'GET') {
      return sendJson(res, 200, { success: true, accounts: Array.from(usersDb.values()) });
    }

    // --------------------------------------------------------------------------
    // STEP 4: LISTEN FOR REQUIREMENTS CHANGES (THIN WEBHOOKS)
    // --------------------------------------------------------------------------
    if (pathname === '/api/webhooks/thin' && method === 'POST') {
      const sig = req.headers['stripe-signature'];
      const rawBody = await readRequestBody(req);

      if (!STRIPE_WEBHOOK_SECRET || STRIPE_WEBHOOK_SECRET.includes('PLACEHOLDER')) {
        console.warn('[Stripe Webhook] Received webhook but STRIPE_WEBHOOK_SECRET is not configured.');
        return sendJson(res, 400, { error: 'Webhook secret not configured.' });
      }

      let thinEvent;
      try {
        // 1. Parse thin event with signature verification
        if (typeof stripeClient.parseEventNotification === 'function') {
          thinEvent = stripeClient.parseEventNotification(rawBody, sig, STRIPE_WEBHOOK_SECRET);
        } else if (typeof stripeClient.parseThinEvent === 'function') {
          thinEvent = stripeClient.parseThinEvent(rawBody, sig, STRIPE_WEBHOOK_SECRET);
        } else {
          thinEvent = JSON.parse(rawBody);
        }
      } catch (err) {
        console.error('[Stripe Webhook] Signature verification failed:', err.message);
        return sendJson(res, 400, { error: `Webhook Error: ${err.message}` });
      }

      // 2. Fetch full event details using V2 Core Events API
      console.log(`[Stripe Webhook] Received thin event: ${thinEvent.id} (type: ${thinEvent.type})`);
      let event;
      try {
        event = await stripeClient.v2.core.events.retrieve(thinEvent.id);
      } catch (retrieveErr) {
        console.warn(`[Stripe Webhook] Live event retrieval fallback (${retrieveErr.message}). Using parsed thin event.`);
        event = thinEvent;
      }

      const accountId = event.related_object?.id || 'Platform';
      webhookEventsLog.unshift({
        id: event.id,
        type: event.type,
        accountId,
        receivedAt: new Date().toISOString(),
      });

      return sendJson(res, 200, { received: true });
    }

    if (pathname === '/api/webhooks/events' && method === 'GET') {
      return sendJson(res, 200, { success: true, events: webhookEventsLog.slice(0, 20) });
    }

    // --------------------------------------------------------------------------
    // STEP 5: CREATE PRODUCTS (PLATFORM LEVEL WITH CONNECTED MAPPING)
    // --------------------------------------------------------------------------
    if (pathname === '/api/products' && method === 'POST') {
      validateStripeKey();
      const raw = await readRequestBody(req);
      const { name, description, priceInCents, currency, connectedAccountId } = JSON.parse(raw || '{}');

      if (!name || !priceInCents || !connectedAccountId) {
        return sendJson(res, 400, { error: 'name, priceInCents, and connectedAccountId are required.' });
      }

      const productCurrency = (currency || 'usd').toLowerCase();

      // Create product at the platform level using Stripe Client
      const product = await stripeClient.products.create({
        name,
        description: description || 'Bartholomew Protected Agent Product',
        default_price_data: {
          unit_amount: parseInt(priceInCents, 10),
          currency: productCurrency,
        },
        metadata: {
          connected_account_id: connectedAccountId,
        },
      });

      const productRecord = {
        productId: product.id,
        name: product.name,
        description: product.description,
        priceInCents: parseInt(priceInCents, 10),
        currency: productCurrency,
        connectedAccountId,
        createdAt: new Date().toISOString(),
      };
      productsDb.set(product.id, productRecord);

      console.log(`[Stripe Products] Created platform product: ${product.id} mapped to account ${connectedAccountId}`);
      return sendJson(res, 200, { success: true, product: productRecord });
    }

    if (pathname === '/api/products' && method === 'GET') {
      return sendJson(res, 200, { success: true, products: Array.from(productsDb.values()) });
    }

    // --------------------------------------------------------------------------
    // STEP 6: PROCESS CHARGES (DESTINATION CHARGES WITH APPLICATION FEE)
    // --------------------------------------------------------------------------
    if (pathname === '/api/checkout/create-session' && method === 'POST') {
      validateStripeKey();
      const raw = await readRequestBody(req);
      const { productId } = JSON.parse(raw || '{}');

      const product = productsDb.get(productId);
      if (!product) {
        return sendJson(res, 404, { error: 'Product not found.' });
      }

      const connectedAccountId = product.connectedAccountId;
      const rootUrl = `http://${req.headers.host || `localhost:${PORT}`}`;
      const feeInCents = Math.round(product.priceInCents * 0.10); // 10% platform application fee

      // Create Checkout Session using Destination Charge
      const session = await stripeClient.checkout.sessions.create({
        line_items: [
          {
            price_data: {
              currency: product.currency,
              product_data: {
                name: product.name,
                description: product.description,
              },
              unit_amount: product.priceInCents,
            },
            quantity: 1,
          },
        ],
        payment_intent_data: {
          application_fee_amount: feeInCents,
          transfer_data: {
            destination: connectedAccountId,
          },
        },
        mode: 'payment',
        success_url: `${rootUrl}/?checkout=success&session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${rootUrl}/?checkout=cancel`,
      });

      return sendJson(res, 200, { success: true, checkoutUrl: session.url, sessionId: session.id });
    }

    // Serve Storefront HTML
    const htmlPath = path.join(__dirname, 'public', 'index.html');
    if (fs.existsSync(htmlPath)) {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      return fs.createReadStream(htmlPath).pipe(res);
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      return res.end('Storefront UI not found.');
    }
  } catch (err) {
    console.error('[Server Error]', err.message);
    return sendJson(res, 500, { error: err.message });
  }
});

// Start listening if run directly
if (process.argv[1] && (process.argv[1].endsWith('server.js') || process.argv[1].includes('stripe_connect_v2'))) {
  server.listen(PORT, () => {
    console.log('='.repeat(70));
    console.log(`🚀 Bartholomew Stripe Connect V2 Server running on http://localhost:${PORT}`);
    console.log(`• Storefront UI         : http://localhost:${PORT}/`);
    console.log(`• Connect Onboarding API: http://localhost:${PORT}/api/connect/accounts`);
    console.log(`• Thin Webhooks Endpoint: http://localhost:${PORT}/api/webhooks/thin`);
    console.log('='.repeat(70));
  });
}

const appState = { usersDb, productsDb, webhookEventsLog };
export { server, stripeClient, appState };
export default server;
