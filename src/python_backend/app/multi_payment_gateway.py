import os
from typing import Dict, Any
from pydantic import BaseModel

class PaymentInvoiceRequest(BaseModel):
    amount_usd: float
    currency: str = "USDC" # USDC, SOL, BTC, ETH, AKT, STRIPE, PAYPAL
    service: str = "inference" # inference, notary, compute, bounty
    customer_ref: str = "client_default"

class MultiPaymentGateway:
    """
    Multi-Currency Direct Payment Engine.
    Processes payments across 7 direct chains/gateways without intermediary relays.
    """
    def __init__(self):
        self.wallets = {
            "BASE_USDC": os.getenv("BASE_USDC_WALLET", "0xaD38221a686318aB1049fa5D60fA5b15DBB73ba4"),
            "SOLANA_USDC": os.getenv("SOLANA_WALLET", "4k3Dyjzvzp8eMZWUXbB4Q6dG65k5BvT8R5p9"),
            "BITCOIN": os.getenv("BTC_ADDRESS", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
            "ETHEREUM": os.getenv("ETH_WALLET", "0xaD38221a686318aB1049fa5D60fA5b15DBB73ba4"),
            "AKASH_AKT": os.getenv("AKASH_WALLET", "akash1y557yjut3zxlfpd3p0elet4t2w5hermd69p8k7"),
            "STRIPE": "STRIPE_DIRECT_MERCHANT",
            "PAYPAL": "PAYPAL_DIRECT_RECEIVER"
        }

    def generate_invoice(self, req: PaymentInvoiceRequest) -> Dict[str, Any]:
        cur = req.currency.upper()
        dest = self.wallets.get(cur, self.wallets["BASE_USDC"])
        
        return {
            "success": True,
            "invoice_id": f"INV-{os.urandom(4).hex().upper()}",
            "amount_usd": req.amount_usd,
            "currency": cur,
            "payment_address": dest,
            "instructions": f"Directly transfer ${req.amount_usd} in {cur} to {dest}",
            "relay_needed": False,
            "zero_cost_retention": "100%"
        }

payment_gateway = MultiPaymentGateway()
