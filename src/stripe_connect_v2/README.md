# Stripe Connect V2 Integration Guide & Reference Implementation

This directory contains a complete sample implementation of **Stripe Connect V2** built with both **Node.js (Express)** and **Python (FastAPI)**, featuring:
1. **V2 Core Accounts API** for creating and managing connected accounts.
2. **V2 Core Account Links API** for hosted onboarding.
3. **Thin Event Webhook Engine** for receiving requirements and capability updates.
4. **Platform Products & Destination Charges** with automatic application fee collection.
5. **Interactive Glassmorphic Storefront UI** matching the Bartholomew dark design system.

---

## 🚀 Quick Start

### Option A: Node.js / Express
```bash
# 1. Set your Stripe Secret Key (Dashboard -> Developers -> API Keys)
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."  # Optional for webhooks

# 2. Run the Node.js server
node stripe_connect_v2/server.js
```
The server will start on **`http://localhost:4242`**. Open this URL in your browser to view the interactive Connect management portal and customer storefront.

### Option B: Python / FastAPI
```bash
# 1. Set your Stripe Secret Key
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# 2. Run the FastAPI server via Uvicorn
uvicorn stripe_connect_v2.server:app --port 4242 --reload
```

---

## 🔑 Key Architecture & API Details

### 1. Unified `stripeClient`
Every request is dispatched through an instantiated Stripe Client instance:
```javascript
import Stripe from 'stripe';
const stripeClient = new Stripe(process.env.STRIPE_SECRET_KEY);
```
```python
from stripe import StripeClient
stripe_client = StripeClient(os.environ["STRIPE_SECRET_KEY"])
```

### 2. V2 Core Connected Account Creation
Connected accounts are provisioned via `stripeClient.v2.core.accounts.create(...)`:
```javascript
const account = await stripeClient.v2.core.accounts.create({
  display_name: 'Astra Security Agent Lab',
  contact_email: 'creator@agent-corp.com',
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
```

> [!IMPORTANT]
> **No Top-Level Type:** Never pass `type` at the top level (e.g. do NOT use `type: 'express'`, `type: 'standard'`, or `type: 'custom'`). Use `dashboard: 'express'` and assign fee/loss responsibilities to `application`.

### 3. V2 Account Onboarding & Live Status Query
- **Onboarding Link Creation**:
  ```javascript
  const accountLink = await stripeClient.v2.core.accountLinks.create({
    account: accountId,
    use_case: {
      type: 'account_onboarding',
      account_onboarding: {
        configurations: ['recipient'],
        refresh_url: `${rootUrl}/?onboarding=refresh&accountId=${accountId}`,
        return_url: `${rootUrl}/?onboarding=complete&accountId=${accountId}`,
      },
    },
  });
  ```
- **Direct Live API Status (Never Cached in DB)**:
  ```javascript
  const account = await stripeClient.v2.core.accounts.retrieve(stripeAccountId, {
    include: ['configuration.recipient', 'requirements'],
  });

  const readyToReceivePayments =
    account?.configuration?.recipient?.capabilities?.stripe_balance?.stripe_transfers?.status === 'active';
  const requirementsStatus = account.requirements?.summary?.minimum_deadline?.status;
  const onboardingComplete = requirementsStatus !== 'currently_due' && requirementsStatus !== 'past_due';
  ```

### 4. Thin Webhooks & Event Retrieval
V2 accounts use **Thin Events** to signal state changes without sending large PII payloads over the wire:
1. Parse the thin event signature:
   ```javascript
   const thinEvent = stripeClient.parseThinEvent(req.body, sig, webhookSecret);
   ```
2. Retrieve the complete V2 event object:
   ```javascript
   const event = await stripeClient.v2.core.events.retrieve(thinEvent.id);
   ```
3. Test locally using Stripe CLI:
   ```bash
   stripe listen --thin-events 'v2.core.account[requirements].updated,v2.core.account[.recipient].capability_status_updated' --forward-thin-to http://localhost:4242/api/webhooks/thin
   ```

### 5. Product Creation & Destination Charges
- **Platform Product**:
  Created at the platform level and linked via metadata:
  ```javascript
  const product = await stripeClient.products.create({
    name: 'Bartholomew Defense License',
    default_price_data: { unit_amount: 4900, currency: 'usd' },
    metadata: { connected_account_id: connectedAccountId },
  });
  ```
- **Monetized Destination Charge via Checkout Sessions**:
  ```javascript
  const session = await stripeClient.checkout.sessions.create({
    line_items: [{ price_data: { unit_amount: 4900, currency: 'usd', product_data: { name: '...' } }, quantity: 1 }],
    payment_intent_data: {
      application_fee_amount: 490, // 10% platform fee retained
      transfer_data: { destination: connectedAccountId },
    },
    mode: 'payment',
    success_url: `${rootUrl}/?checkout=success&session_id={CHECKOUT_SESSION_ID}`,
  });
  ```
