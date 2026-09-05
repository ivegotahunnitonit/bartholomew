"""
============================================================================
STRIPE CONNECT V2 PLATFORM INTEGRATION (Python / FastAPI / StripeClient)
============================================================================

Flow Overview:
  1. Initialize unified StripeClient with API key validation.
  2. Create Connected Accounts using Stripe V2 Core Accounts API.
  3. Generate Stripe V2 Account Onboarding Links & query live account status.
  4. Listen & parse V2 "Thin" Webhook Events.
  5. Create platform-level Products and map them to connected creators.
  6. Process Destination Charges with application fee monetization via Checkout Sessions.
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, Header, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import stripe
from stripe import StripeClient

# ============================================================================
# STEP 1: INITIALIZE THE STRIPE CLIENT
# ============================================================================
# PLACEHOLDER: Set your Stripe Secret Key here or via os.environ["STRIPE_SECRET_KEY"].
# Obtain this from https://dashboard.stripe.com/test/apikeys
# Format: sk_test_... (or sk_live_... in production)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_PLACEHOLDER_REPLACE_WITH_YOUR_STRIPE_SECRET_KEY")

# PLACEHOLDER: Set your Stripe Webhook Signing Secret here or via os.environ["STRIPE_WEBHOOK_SECRET"].
# Obtain this from Stripe Dashboard -> Developers -> Webhooks or via `stripe listen` CLI output.
# Format: whsec_...
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_PLACEHOLDER_REPLACE_WITH_YOUR_WEBHOOK_SECRET")


def validate_stripe_key():
    """Validates that the Stripe API key is configured before dispatching SDK requests."""
    if not STRIPE_SECRET_KEY or "PLACEHOLDER" in STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "Missing Stripe Secret Key! Please set the STRIPE_SECRET_KEY environment variable "
                "or replace the placeholder in server.py with your real key from https://dashboard.stripe.com/test/apikeys"
            ),
        )


# Single unified Stripe Client instance used for all requests across the application.
stripe_client = StripeClient(STRIPE_SECRET_KEY)

app = FastAPI(title="Bartholomew Stripe Connect V2 Platform")

# In-memory database mapping stores for demo:
users_db: Dict[str, Dict[str, Any]] = {}
products_db: Dict[str, Dict[str, Any]] = {}
webhook_events_log: List[Dict[str, Any]] = []


# ============================================================================
# STEP 2: CREATING CONNECTED ACCOUNTS (V2 CORE ACCOUNTS API)
# ============================================================================
@app.post("/api/connect/accounts")
async def create_connected_account(request: Request):
    """
    Creates a connected account where the platform is responsible for pricing
    and fee collection, requesting stripe_transfers capability.

    IMPORTANT: In the V2 Core API:
      - Never pass `type` at the top level (do NOT use type: 'express', 'standard', or 'custom').
      - Use `dashboard: 'express'`.
      - Responsibilities for fees and losses are assigned to 'application'.
    """
    validate_stripe_key()
    body = await request.json()
    display_name = body.get("displayName")
    contact_email = body.get("contactEmail")
    user_id = body.get("userId") or f"user_{int(time.time())}_{len(users_db)}"

    if not display_name or not contact_email:
        raise HTTPException(status_code=400, detail="displayName and contactEmail are required.")

    try:
        # Call Stripe V2 Core Accounts API with exact specified schema
        account = stripe_client.v2.core.accounts.create(
            params={
                "display_name": display_name,
                "contact_email": contact_email,
                "identity": {
                    "country": "us",
                },
                "dashboard": "express",
                "defaults": {
                    "responsibilities": {
                        "fees_collector": "application",
                        "losses_collector": "application",
                    },
                },
                "configuration": {
                    "recipient": {
                        "capabilities": {
                            "stripe_balance": {
                                "stripe_transfers": {
                                    "requested": True,
                                },
                            },
                        },
                    },
                },
            }
        )

        user_record = {
            "userId": user_id,
            "displayName": display_name,
            "contactEmail": contact_email,
            "stripeAccountId": account.id,
        }
        users_db[user_id] = user_record

        return {
            "success": True,
            "account": {
                "id": account.id,
                "displayName": account.display_name,
                "contactEmail": account.contact_email,
                "userId": user_id,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STEP 3: ONBOARDING CONNECTED ACCOUNTS & RETRIEVING LIVE STATUS
# ============================================================================
@app.post("/api/connect/account-links")
async def create_account_link(request: Request):
    """Creates a V2 Account Link to launch the Stripe-hosted onboarding flow."""
    validate_stripe_key()
    body = await request.json()
    account_id = body.get("accountId")
    if not account_id:
        raise HTTPException(status_code=400, detail="accountId is required.")

    base_url = str(request.base_url).rstrip("/")
    refresh_url = f"{base_url}/?onboarding=refresh&accountId={account_id}"
    return_url = f"{base_url}/?onboarding=complete&accountId={account_id}"

    try:
        # Use V2 Core Account Links API for account onboarding
        account_link = stripe_client.v2.core.account_links.create(
            params={
                "account": account_id,
                "use_case": {
                    "type": "account_onboarding",
                    "account_onboarding": {
                        "configurations": ["recipient"],
                        "refresh_url": refresh_url,
                        "return_url": return_url,
                    },
                },
            }
        )
        return {"success": True, "url": account_link.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/connect/accounts/{account_id}/status")
async def get_account_status(account_id: str):
    """
    Queries live status directly from the Stripe V2 Core Accounts API.
    Per specification: Status is ALWAYS fetched directly from the API, never stored in DB.
    """
    validate_stripe_key()
    try:
        # Retrieve account with configuration.recipient and requirements expanded
        account = stripe_client.v2.core.accounts.retrieve(
            account_id,
            params={"include": ["configuration.recipient", "requirements"]},
        )

        config_recip = getattr(getattr(account, "configuration", None), "recipient", None)
        caps = getattr(config_recip, "capabilities", None)
        stripe_bal = getattr(caps, "stripe_balance", None)
        transfers = getattr(stripe_bal, "stripe_transfers", None)
        transfer_status = getattr(transfers, "status", None)
        ready_to_receive = transfer_status == "active"

        reqs = getattr(account, "requirements", None)
        summary = getattr(reqs, "summary", None)
        deadline = getattr(summary, "minimum_deadline", None)
        req_status = getattr(deadline, "status", None)
        onboarding_complete = req_status not in ["currently_due", "past_due"]

        return {
            "success": True,
            "accountId": account.id,
            "displayName": getattr(account, "display_name", ""),
            "readyToReceivePayments": ready_to_receive,
            "onboardingComplete": onboarding_complete,
            "requirementsStatus": req_status or "completed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/connect/accounts")
def list_connected_accounts():
    """Lists all registered users and their associated connected account IDs."""
    return {"success": True, "accounts": list(users_db.values())}


# ============================================================================
# STEP 4: LISTEN FOR REQUIREMENTS CHANGES (THIN WEBHOOKS)
# ============================================================================
@app.post("/api/webhooks/thin")
async def handle_thin_webhook(request: Request, stripe_signature: Optional[str] = Header(None)):
    """
    Receives V2 Thin Events from Stripe, verifies signature, retrieves full event details,
    and handles requirements / capability status updates.
    """
    if not STRIPE_WEBHOOK_SECRET or "PLACEHOLDER" in STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail="Webhook secret not configured.")

    raw_body = await request.body()
    try:
        # 1. Parse thin event with signature verification
        thin_event = stripe_client.parse_thin_event(raw_body, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook Signature Verification Failed: {str(e)}")

    try:
        # 2. Fetch full event data from Stripe V2 Core Events API
        event = stripe_client.v2.core.events.retrieve(thin_event.id)
        account_id = getattr(getattr(event, "related_object", None), "id", "Platform")

        webhook_events_log.insert(
            0,
            {
                "id": event.id,
                "type": event.type,
                "accountId": account_id,
            },
        )
        return {"received": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/webhooks/events")
def get_webhook_events():
    return {"success": True, "events": webhook_events_log[:20]}


# ============================================================================
# STEP 5: CREATE PRODUCTS (PLATFORM LEVEL WITH CONNECTED MAPPING)
# ============================================================================
@app.post("/api/products")
async def create_product(request: Request):
    """
    Creates a product at the platform level (NOT on the connected account),
    and stores the mapping between the product and the connected account ID.
    """
    validate_stripe_key()
    body = await request.json()
    name = body.get("name")
    description = body.get("description", "Bartholomew Protected Agent Product")
    price_in_cents = body.get("priceInCents")
    currency = (body.get("currency") or "usd").lower()
    connected_account_id = body.get("connectedAccountId")

    if not name or not price_in_cents or not connected_account_id:
        raise HTTPException(status_code=400, detail="name, priceInCents, and connectedAccountId are required.")

    try:
        # Create product at the platform level
        product = stripe_client.products.create(
            params={
                "name": name,
                "description": description,
                "default_price_data": {
                    "unit_amount": int(price_in_cents),
                    "currency": currency,
                },
                "metadata": {
                    "connected_account_id": connected_account_id,
                },
            }
        )

        record = {
            "productId": product.id,
            "name": product.name,
            "description": product.description,
            "priceInCents": int(price_in_cents),
            "currency": currency,
            "connectedAccountId": connected_account_id,
        }
        products_db[product.id] = record
        return {"success": True, "product": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products")
def list_products():
    return {"success": True, "products": list(products_db.values())}


# ============================================================================
# STEP 6: PROCESS CHARGES (DESTINATION CHARGES WITH APPLICATION FEE)
# ============================================================================
@app.post("/api/checkout/create-session")
async def create_checkout_session(request: Request):
    """
    Initiates a Stripe Checkout Session using a Destination Charge with an
    application fee to monetize the transaction.
    """
    validate_stripe_key()
    body = await request.json()
    product_id = body.get("productId")
    product = products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    connected_account_id = product["connectedAccountId"]
    base_url = str(request.base_url).rstrip("/")
    fee_in_cents = int(product["priceInCents"] * 0.10)  # 10% platform application fee

    try:
        session = stripe_client.checkout.sessions.create(
            params={
                "line_items": [
                    {
                        "price_data": {
                            "currency": product["currency"],
                            "product_data": {
                                "name": product["name"],
                                "description": product["description"],
                            },
                            "unit_amount": product["priceInCents"],
                        },
                        "quantity": 1,
                    }
                ],
                "payment_intent_data": {
                    "application_fee_amount": fee_in_cents,
                    "transfer_data": {
                        "destination": connected_account_id,
                    },
                },
                "mode": "payment",
                "success_url": f"{base_url}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
                "cancel_url": f"{base_url}/?checkout=cancel",
            }
        )
        return {"success": True, "checkoutUrl": session.url, "sessionId": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount public static assets
static_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=4242, reload=True)
