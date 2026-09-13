export interface ListingParams {
  type: 'waste' | 'need';
  material: string;
  quantityKg: number;
  lat?: number;
  lng?: number;
  pricePerKg?: number;
}

export interface EscrowInitParams {
  dealId: string;
  amountUsd: number;
  buyerAddress: string;
}

export class ACNClient {
  private baseUrl: string;

  constructor(baseUrl = 'http://localhost:8090') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async getHealth() {
    const res = await fetch(`${this.baseUrl}/api/v1/health`);
    return res.json();
  }

  async getListings() {
    const res = await fetch(`${this.baseUrl}/api/v1/listings`);
    return res.json();
  }

  async addListing(params: ListingParams) {
    const res = await fetch(`${this.baseUrl}/api/v1/listings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    return res.json();
  }

  async triggerMatching() {
    const res = await fetch(`${this.baseUrl}/api/v1/match`, {
      method: 'POST',
    });
    return res.json();
  }

  async initiateEscrow(params: EscrowInitParams) {
    const res = await fetch(`${this.baseUrl}/api/v1/escrow/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    return res.json();
  }
}
