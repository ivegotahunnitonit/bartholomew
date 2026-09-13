import { db } from '../database/db.ts';
import { config } from '../config.ts';
import * as crypto from 'node:crypto';
import { PaymentManager } from '../settlement/PaymentManager.ts';
import { Bartholomew } from './Bartholomew.ts';
import { signMatch, signTransaction } from './CryptoUtils.ts';

export interface Listing {
  id: string;
  node_id: string;
  type: 'waste' | 'need';
  resource: string;
  quantity: number;
  unit: string;
  price: number;
  lat: number;
  lng: number;
  created_at: number;
  expires_at: number;
  status: 'active' | 'matched' | 'completed' | 'expired';
  signature?: string;
  signer_address?: string;
  declaration?: string;
  verified_by_lab?: number;
  safety_sheet_url?: string;
  priority_routing?: number;
}

export interface MatchResult {
  id: string;
  waste_listing_id: string;
  need_listing_id: string;
  distance_km: number;
  savings_usd: number;
  fee_usd: number;
  status: 'proposed' | 'accepted' | 'completed' | 'declined';
  created_at: number;
  signature?: string;
  signer_address?: string;
  routing_path?: string;
}

// Simple synonyms map to support flexible matchmaking matching
const COMPATIBILITY_MAP: Record<string, string[]> = {
  'spent grain': ['spent grain', 'brewer grain', 'animal feed', 'compost', 'feedstock'],
  'spent yeast': ['spent yeast', 'yeast', 'fertilizer', 'animal feed'],
  'food waste': ['food waste', 'organic waste', 'compost', 'biogas feedstock'],
  'wood chips': ['wood chips', 'mulch', 'mushroom substrate', 'biomass'],
  'sawdust': ['sawdust', 'mushroom substrate', 'bedding', 'biomass'],
  'coffee grounds': ['coffee grounds', 'compost', 'fertilizer', 'mushroom substrate'],
  'cardboard': ['cardboard', 'packaging material', 'mulch', 'recycling'],
  'greywater': ['greywater', 'irrigation water', 'water recycling'],
  'scrap metal': ['scrap metal', 'steel', 'aluminum', 'recycling', 'metal'],
  'plastic waste': ['plastic', 'hdpe', 'pet', 'recyclables', 'pellets'],
  'industrial solvents': ['solvents', 'chemicals', 'cleaning agents', 'recovery'],
  // 24/7 Freight, Loadboard & Hauling Dispatch Compatibility Mappings
  'freight': ['freight', 'truckload', 'hauling', 'empty backhaul', 'cargo', 'dry van', 'reefer', 'shipment', 'load'],
  'empty backhaul': ['empty backhaul', 'truckload', 'freight', 'hauling', 'dry van', 'reefer', 'flatbed', 'cargo'],
  'delivery dispatch': ['delivery dispatch', 'expedited delivery', 'last mile', 'doordash dispatch', 'courier', 'hauling'],
};

/**
 * Calculates distance between two coordinates using the Haversine formula
 */
export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth's radius in km
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
 * Check if a waste resource is compatible with a need resource requirement
 */
export function isCompatible(waste: string, need: string): boolean {
  const w = waste.toLowerCase().trim();
  const n = need.toLowerCase().trim();

  if (w === n || w.includes(n) || n.includes(w)) {
    return true;
  }

  // Check synonym mappings
  for (const [key, synonyms] of Object.entries(COMPATIBILITY_MAP)) {
    if (w.includes(key) || synonyms.some(s => w.includes(s))) {
      if (n.includes(key) || synonyms.some(s => n.includes(s))) {
        return true;
      }
    }
  }

  return false;
}

export class Matchmaker {
  /**
   * Run matching algorithm on all active listings in the local database
   */
  static runMatching(): MatchResult[] {
    console.log('[Matchmaker] Starting matchmaking process...');
    
    // 1. Fetch active listings (limited to 50 per cycle to prevent event loop blockage at scale)
    const activeWastesStmt = db.prepare("SELECT * FROM listings WHERE type = 'waste' AND status = 'active' ORDER BY RANDOM() LIMIT 50");
    const activeNeedsStmt = db.prepare("SELECT * FROM listings WHERE type = 'need' AND status = 'active' ORDER BY RANDOM() LIMIT 50");
    
    console.log('[Matchmaker] Querying listings...');
    const activeWastes = activeWastesStmt.all() as any[] as Listing[];
    const activeNeeds = activeNeedsStmt.all() as any[] as Listing[];
    console.log(`[Matchmaker] Fetched ${activeWastes.length} wastes and ${activeNeeds.length} needs.`);

    const proposedMatches: MatchResult[] = [];
    const estimatedLogisticsCostPerKm = 0.15; // $0.15 per km transit cost
    
    // Fetch online peers to check for intermediate routing hops
    let onlinePeers: any[] = [];
    try {
      onlinePeers = db.prepare("SELECT * FROM peers WHERE status = 'online' AND lat IS NOT NULL AND lng IS NOT NULL").all() as any[];
    } catch (_) {}

    const potentialMatches: any[] = [];

    console.log(`[Matchmaker] Checking combinations...`);
    let combCount = 0;
    for (const waste of activeWastes) {
      for (const need of activeNeeds) {
        combCount++;
        if (combCount % 1000 === 0) console.log(`[Matchmaker] Checked ${combCount} combinations...`);
        if (waste.node_id === need.node_id && waste.node_id !== 'local_node') {
          continue;
        }

        if (!isCompatible(waste.resource, need.resource)) {
          continue;
        }

        // Check if digital/compute task
        const isDigital = ['job', 'bounty', 'contract', 'items', 'shares'].includes(waste.unit.toLowerCase()) || 
                          ['job', 'bounty', 'contract', 'items', 'shares'].includes(need.unit.toLowerCase());

        let distance = 0;
        let routingPath = '';
        let logisticsCost = 0;

        if (!isDigital) {
          // Calculate direct distance
          const directDistance = calculateDistance(waste.lat, waste.lng, need.lat, need.lng);
          distance = directDistance;
          logisticsCost = directDistance * estimatedLogisticsCostPerKm;

          // Check if multi-hop routing makes sense (for distances > 300 km)
          if (directDistance > 300 && onlinePeers.length > 0) {
            for (const peer of onlinePeers) {
              // Check if peer is in the middle of transit
              const d1 = calculateDistance(waste.lat, waste.lng, peer.lat, peer.lng);
              const d2 = calculateDistance(peer.lat, peer.lng, need.lat, need.lng);
              
              if (d1 + d2 < 1.3 * directDistance) {
                // Found a viable multi-hop hub node Z
                distance = d1 + d2;
                routingPath = `${waste.node_id || 'unknown'} -> ${peer.node_id || 'broker-node'} -> ${need.node_id || 'unknown'}`;
                logisticsCost = distance * estimatedLogisticsCostPerKm * 0.9; // 10% logistics efficiency for hub transit consolidation
                break;
              }
            }
          }
        }

        const matchedQuantity = Math.min(waste.quantity, need.quantity);
        const buyerTargetPrice = need.price;
        const sellerListingPrice = waste.price;

        let grossSavings = (buyerTargetPrice - sellerListingPrice) * matchedQuantity;

        if (grossSavings < 0) {
          const histAvg = Bartholomew.getAveragePrice(waste.resource);
          if (
            histAvg !== null && 
            Math.round(buyerTargetPrice * 100) >= Math.round(histAvg * 0.80 * 100) && 
            Math.round(sellerListingPrice * 100) <= Math.round(histAvg * 1.20 * 100)
          ) {
            grossSavings = (histAvg * matchedQuantity) * 0.10;
            console.log(`[Matchmaker] [Dynamic Pricing] Resolved price mismatch ($${sellerListingPrice.toFixed(2)} asking vs $${buyerTargetPrice.toFixed(2)} offering) for "${waste.resource}" by compromising at historical average: $${histAvg.toFixed(2)}`);
          } else {
            continue;
          }
        }

        const netSavings = grossSavings - logisticsCost;

        if (netSavings <= 0) {
          continue;
        }

        // Apply Bartholomew industrial zone and material weight optimizations
        const utility = Bartholomew.calculateMatchUtility(
          waste.resource,
          waste.lat,
          waste.lng,
          need.lat,
          need.lng,
          distance,
          netSavings
        );

        // Compute fee with Bartholomew multiplier and premium modifiers
        let fee = netSavings * config.FEE_RATE * utility.multiplier;
        
        if (waste.priority_routing || need.priority_routing) {
          fee *= 1.2; // 20% priority routing premium
        }
        if (waste.verified_by_lab || need.verified_by_lab) {
          fee *= 1.15; // 15% lab verification premium
        }

        const matchExistsStmt = db.prepare(`
          SELECT id FROM matches 
          WHERE waste_listing_id = ? AND need_listing_id = ? AND status != 'declined'
        `);
        const existing = matchExistsStmt.get(waste.id, need.id);
        if (existing) {
          continue; 
        }

        potentialMatches.push({
          waste,
          need,
          distance,
          netSavings,
          fee,
          matchedQuantity,
          routingPath
        });
      }
    }

    potentialMatches.sort((a, b) => b.fee - a.fee);

    for (const match of potentialMatches) {
      const { waste, need, distance, netSavings, fee, matchedQuantity, routingPath } = match;
      const matchId = crypto.randomUUID();
      const now = Date.now();

      const signed = signMatch(matchId, waste.id, need.id, netSavings, fee);

      const insertMatchStmt = db.prepare(`
        INSERT INTO matches (id, waste_listing_id, need_listing_id, distance_km, savings_usd, fee_usd, status, created_at, signature, signer_address, routing_path)
        VALUES (?, ?, ?, ?, ?, ?, 'proposed', ?, ?, ?, ?)
      `);
      insertMatchStmt.run(matchId, waste.id, need.id, distance, netSavings, fee, now, signed.signature, signed.signer_address, routingPath || null);

      const newMatch: MatchResult = {
        id: matchId,
        waste_listing_id: waste.id,
        need_listing_id: need.id,
        distance_km: distance,
        savings_usd: netSavings,
        fee_usd: fee,
        status: 'proposed',
        created_at: now,
        signature: signed.signature,
        signer_address: signed.signer_address,
        routing_path: routingPath || undefined
      };

      proposedMatches.push(newMatch);
      const routeDetail = routingPath ? ` (Multi-hop: ${routingPath})` : '';
      console.log(`[Matchmaker] Found viable match: ${waste.resource} (${matchedQuantity} ${waste.unit}) -> Savings: $${netSavings.toFixed(2)}, Fee: $${fee.toFixed(2)}${routeDetail}`);

      if (config.AUTO_ACCEPT_ENABLED && netSavings >= config.AUTO_ACCEPT_THRESHOLD) {
        console.log(`[Matchmaker] Match ${matchId} qualified for auto-acceptance (Savings: $${netSavings.toFixed(2)} >= $${config.AUTO_ACCEPT_THRESHOLD.toFixed(2)})`);
        setTimeout(() => {
          // Prioritize Base (USDC) for settlement to maximize DeFi yield compounding
          const preferredMethod = 'base';
          const txId = Matchmaker.acceptMatch(matchId, preferredMethod);
          if (txId) {
            console.log(`[Matchmaker] Auto-accepted match ${matchId} (${preferredMethod}). Initiating auto-settlement cycle...`);
            PaymentManager.startConfirmation(txId);
          }
        }, 100);
      }
    }

    console.log(`[Matchmaker] Matchmaking complete. Created ${proposedMatches.length} new matches.`);
    return proposedMatches;
  }

  /**
   * Accepts a proposed match and updates listing states and records fee transaction.
   * Returns the generated transaction ID on success, or null on failure.
   */
  static acceptMatch(matchId: string, paymentMethod: string = 'lightning'): string | null {
    const getMatchStmt = db.prepare("SELECT * FROM matches WHERE id = ?");
    const match = getMatchStmt.get(matchId) as any as MatchResult;
    
    if (!match || match.status !== 'proposed') {
      return null;
    }

    // Begin database transaction for consistency
    const updateMatch = db.prepare("UPDATE matches SET status = 'accepted' WHERE id = ?");
    const updateWasteListing = db.prepare("UPDATE listings SET status = 'matched' WHERE id = ?");
    const updateNeedListing = db.prepare("UPDATE listings SET status = 'matched' WHERE id = ?");
    
    // Create pending payment transaction
    const txId = crypto.randomUUID();
    const now = Date.now();
    const signedTx = signTransaction(txId, matchId, match.fee_usd, paymentMethod);
    const createTx = db.prepare(`
      INSERT INTO transactions (id, match_id, amount_usd, status, payment_method, created_at, signature, signer_address)
      VALUES (?, ?, ?, 'pending', ?, ?, ?, ?)
    `);

    updateMatch.run(matchId);
    updateWasteListing.run(match.waste_listing_id);
    updateNeedListing.run(match.need_listing_id);
    createTx.run(txId, matchId, match.fee_usd, paymentMethod, now, signedTx.signature, signedTx.signer_address);

    console.log(`[Matchmaker] Match ${matchId} accepted. Created pending transaction ${txId} for fee $${match.fee_usd.toFixed(2)} (${paymentMethod})`);
    
    if (config.AUTO_SETTLE_ON_MATCH) {
      if (config.LIVE_MODE && paymentMethod === 'bitcoin' && config.BTC_PRIVATE_KEY) {
        // Look up listing node_ids to identify if peer is remote
        const wasteListing = db.prepare("SELECT node_id FROM listings WHERE id = ?").get(match.waste_listing_id) as { node_id: string };
        const needListing = db.prepare("SELECT node_id FROM listings WHERE id = ?").get(match.need_listing_id) as { node_id: string };
        
        // Trigger async background auto-payment
        PaymentManager.autoPayMatchFee(matchId, match.fee_usd, wasteListing.node_id, needListing.node_id);
      } else {
        PaymentManager.startConfirmation(txId);
      }
    }
    
    return txId;
  }
}
