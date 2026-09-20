import { db } from '../database/db.ts';

// Major global industrial zones for proximity optimization
export interface IndustrialHub {
  name: string;
  lat: number;
  lng: number;
}

export const INDUSTRIAL_HUBS: IndustrialHub[] = [
  { name: 'Rotterdam Port (Europe)', lat: 51.9244, lng: 4.4777 },
  { name: 'Houston Ship Channel (US)', lat: 29.7604, lng: -95.3698 },
  { name: 'Chicago Industrial Corridor (US)', lat: 41.8781, lng: -87.6298 },
  { name: 'Ruhr Valley (Germany)', lat: 51.4556, lng: 7.0116 },
  { name: 'Shanghai Port Zone (China)', lat: 31.2304, lng: 121.4737 },
  { name: 'Denver Industrial Hub (US)', lat: 39.7392, lng: -104.9903 }
];

// High-value industrial circular materials for weight multipliers
export const MATERIAL_WEIGHTS: Record<string, number> = {
  'metal': 1.5,
  'steel': 1.5,
  'aluminum': 1.5,
  'copper': 1.6,
  'brass': 1.5,
  'scrap': 1.3,
  'plastic': 1.4,
  'hdpe': 1.4,
  'pet': 1.4,
  'e-waste': 1.8,
  'electronic': 1.7,
  'circuit': 1.8,
  'concrete': 1.2,
  'construction': 1.2,
  'solvent': 1.3,
  'chemical': 1.4,
  'wood': 1.1
};

export class Bartholomew {
  private static priceCache: Map<string, { price: number | null, expires: number }> = new Map();

  /**
   * Scans confirmed transactions to calculate the average pricing of matched resources.
   */
  static getAveragePrice(resource: string): number | null {
    const term = `%${resource.toLowerCase().trim()}%`;
    const now = Date.now();
    const cached = this.priceCache.get(term);
    if (cached && cached.expires > now) {
      return cached.price;
    }

    try {
      const stmt = db.prepare(`
        SELECT AVG(l.price) as avg_price
        FROM transactions t
        JOIN matches m ON t.match_id = m.id
        JOIN listings l ON m.waste_listing_id = l.id OR m.need_listing_id = l.id
        WHERE t.status = 'confirmed' AND LOWER(l.resource) LIKE ?
      `);
      const row = stmt.get(term) as any;
      const price = row?.avg_price || null;
      this.priceCache.set(term, { price, expires: now + 60000 }); // Cache for 60 seconds
      return price;
    } catch (err: any) {
      console.error('[Bartholomew] Ledger query error:', err.message);
      return null;
    }
  }

  /**
   * Helper to calculate distance between coordinates (Haversine formula)
   */
  private static calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // km
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLon = ((lon2 - lon1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Dynamically calculates match scoring utilities based on industrial hubs and material categories.
   */
  static calculateMatchUtility(
    resource: string,
    wasteLat: number,
    wasteLng: number,
    needLat: number,
    needLng: number,
    distanceKm: number,
    baseSavings: number
  ): { score: number; multiplier: number; details: string } {
    let multiplier = 1.0;
    let detailsList: string[] = [];

    // 1. Proximity optimization for industrial hubs
    let nearHub = false;
    let hubName = '';
    for (const hub of INDUSTRIAL_HUBS) {
      const d1 = this.calculateDistance(wasteLat, wasteLng, hub.lat, hub.lng);
      const d2 = this.calculateDistance(needLat, needLng, hub.lat, hub.lng);
      
      if (d1 < 100 || d2 < 100) {
        nearHub = true;
        hubName = hub.name;
        break;
      }
    }

    if (nearHub) {
      multiplier += 0.25; // 25% utility boost for being in/near major industrial hubs
      detailsList.push(`Proximity optimization: close to ${hubName} (+25%)`);
    }

    // 2. High-value circular material boosts
    const rLower = resource.toLowerCase();
    let matBoost = 0;
    let boostedMat = '';
    for (const [key, weight] of Object.entries(MATERIAL_WEIGHTS)) {
      if (rLower.includes(key)) {
        matBoost = weight - 1.0;
        boostedMat = key;
        break;
      }
    }

    if (matBoost > 0) {
      multiplier += matBoost;
      detailsList.push(`Material weight optimization: prioritized category "${boostedMat}" (+${(matBoost * 100).toFixed(0)}%)`);
    }

    const score = baseSavings * multiplier;
    const details = detailsList.length > 0 ? detailsList.join(', ') : 'Standard proximity routing';

    return { score, multiplier, details };
  }

  /**
   * Analyzes a listing and returns recommendations based on historical transactions.
   */
  static analyzeListing(resourceName: string, currentPrice: number, type: 'waste' | 'need'): {
    suggestedPrice: number;
    recommended: boolean;
    confidence: 'low' | 'medium' | 'high';
    message: string;
  } {
    const avgPrice = Bartholomew.getAveragePrice(resourceName);

    if (avgPrice === null) {
      return {
        suggestedPrice: currentPrice,
        recommended: false,
        confidence: 'low',
        message: `[BARTHOLOMEW] No historical ledger data found for resource matching "${resourceName}". Retaining current listing price of $${currentPrice.toFixed(2)}.`
      };
    }

    let recommendedPrice = avgPrice;
    let recommended = false;
    let message = '';

    if (type === 'waste') {
      if (currentPrice > avgPrice) {
        recommendedPrice = avgPrice * 0.95; // 5% discount to clear fast
        recommended = true;
        message = `[BARTHOLOMEW] Current price ($${currentPrice.toFixed(2)}) is HIGHER than historical average ($${avgPrice.toFixed(2)}). Recommend adjusting to $${recommendedPrice.toFixed(2)} to accelerate matching.`;
      } else {
        message = `[BARTHOLOMEW] Current price ($${currentPrice.toFixed(2)}) is competitive relative to historical average ($${avgPrice.toFixed(2)}). Retain current rate.`;
      }
    } else {
      if (currentPrice < avgPrice) {
        recommendedPrice = avgPrice * 1.05; // 5% premium to attract sellers
        recommended = true;
        message = `[BARTHOLOMEW] Current price ($${currentPrice.toFixed(2)}) is LOWER than historical average ($${avgPrice.toFixed(2)}). Recommend increasing to $${recommendedPrice.toFixed(2)} to secure matches.`;
      } else {
        message = `[BARTHOLOMEW] Current price ($${currentPrice.toFixed(2)}) is competitive relative to historical average ($${avgPrice.toFixed(2)}). Retain current rate.`;
      }
    }

    return {
      suggestedPrice: recommendedPrice,
      recommended,
      confidence: 'medium',
      message
    };
  }
}
