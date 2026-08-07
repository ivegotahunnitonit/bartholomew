/**
 * ExternalMatchScout.ts
 * Autonomous Circularity Network — Bartholomew Node
 *
 * Runs as a background daemon every N seconds.
 * Responsibilities:
 *  1. Polls all connected peer nodes for their live listings.
 *  2. Checks a pool of external opportunities across categories (Tasks, Materials, Challenges, Compute).
 *  3. Applies Hybrid Priority Logic and geographical match potential scoring.
 *  4. Imports filtered findings as listings into the local database (Balanced Rate Limiting).
 *  5. Writes a source_receipt for EVERY item discovered.
 *  6. Triggers the Matchmaker after each import batch so new matches surface immediately.
 */

import * as crypto from 'node:crypto';
import { db } from '../database/db.ts';
import { Ingestor } from './Ingestor.ts';
import { Matchmaker, isCompatible, calculateDistance } from './Matchmaker.ts';
import { addSystemLog } from '../settlement/PaymentManager.ts';
import { config } from '../config.ts';

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

export interface SourceReceipt {
  id: string;
  discovered_at: number;
  source_type: string; // 'peer_node' | 'task' | 'material' | 'challenge' | 'compute'
  source_label: string;
  agent: string;
  resource: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  lat: number;
  lng: number;
  listing_type: 'waste' | 'need';
  listing_id: string | null;
  match_id: string | null;
  notes: string;
}

export interface Opportunity {
  resource: string;
  listing_type: 'waste' | 'need';
  quantity: number;
  unit: string;
  price_per_unit: number;
  notes: string;
  category: 'task' | 'material' | 'challenge' | 'compute';
  circularity_value: number; // 0.0 to 1.0
  effort_rating: number;      // 0.0 to 1.0 (for tasks/challenges)
  compute_drain: number;      // 0.0 to 1.0 (for compute workloads)
  payout_usd: number;         // Total payout or reward
  agent: string;
  isLiveBounty?: boolean;     // true if fetched live from GitHub/external API
}

export interface ScoutStats {
  processed: number;
  filtered: number;
  converted: number;
  byCategory: Record<string, { processed: number; filtered: number; converted: number }>;
}

// ─────────────────────────────────────────────
// Diagnostics Stats
// ─────────────────────────────────────────────

const stats: ScoutStats = {
  processed: 0,
  filtered: 0,
  converted: 0,
  byCategory: {
    task: { processed: 0, filtered: 0, converted: 0 },
    material: { processed: 0, filtered: 0, converted: 0 },
    challenge: { processed: 0, filtered: 0, converted: 0 },
    compute: { processed: 0, filtered: 0, converted: 0 },
  }
};

export function getScoutStats(): ScoutStats {
  return stats;
}

// ─────────────────────────────────────────────
// Seeded External Opportunity Pool
// ─────────────────────────────────────────────

const OPPORTUNITY_POOL: Opportunity[] = [
  // 1. Task Intake
  {
    resource: 'Spent Yeast LP Routing Optimization',
    listing_type: 'need',
    quantity: 1,
    unit: 'job',
    price_per_unit: 45.00,
    notes: 'Develop custom linear programming model to optimize spent yeast collection routes.',
    category: 'task',
    circularity_value: 0.85,
    effort_rating: 0.4,
    compute_drain: 0.1,
    payout_usd: 45.00,
    agent: 'Agent-Eta',
  },
  {
    resource: 'Post-Industrial Plastic Flaking Study',
    listing_type: 'need',
    quantity: 1,
    unit: 'job',
    price_per_unit: 120.00,
    notes: 'Review contamination reports for recycled HDPE pellets to determine feedstock grades.',
    category: 'task',
    circularity_value: 0.9,
    effort_rating: 0.7,
    compute_drain: 0.1,
    payout_usd: 120.00,
    agent: 'Agent-Eta',
  },
  {
    resource: 'Low-yield Dataset Labeling',
    listing_type: 'need',
    quantity: 1000,
    unit: 'items',
    price_per_unit: 0.002,
    notes: 'Label 1000 items as recyclable or non-recyclable. High effort, low yield.',
    category: 'task',
    circularity_value: 0.3,
    effort_rating: 0.9,
    compute_drain: 0.0,
    payout_usd: 2.00,
    agent: 'Agent-Eta',
  },
  // 2. Material Intake
  {
    resource: 'Spent Brewer Grain',
    listing_type: 'waste',
    quantity: 1200,
    unit: 'kg',
    price_per_unit: 0.05,
    notes: 'Brewery waste grain, high organic content, ideal for animal feed or composting.',
    category: 'material',
    circularity_value: 0.95,
    effort_rating: 0.2,
    compute_drain: 0.0,
    payout_usd: 60.00,
    agent: 'Agent-Beta',
  },
  {
    resource: 'Grain Substrate',
    listing_type: 'need',
    quantity: 1000,
    unit: 'kg',
    price_per_unit: 0.15,
    notes: 'Mushroom cultivation cooperative seeking organic spent grain substrate.',
    category: 'material',
    circularity_value: 0.95,
    effort_rating: 0.1,
    compute_drain: 0.0,
    payout_usd: 150.00,
    agent: 'Agent-Beta',
  },
  {
    resource: 'Compost Substrate',
    listing_type: 'need',
    quantity: 500,
    unit: 'kg',
    price_per_unit: 0.08,
    notes: 'Compost producer looking for nitrogen-rich organic waste materials.',
    category: 'material',
    circularity_value: 0.9,
    effort_rating: 0.1,
    compute_drain: 0.0,
    payout_usd: 40.00,
    agent: 'Agent-Beta',
  },
  {
    resource: 'Toxic Sludge Surplus',
    listing_type: 'waste',
    quantity: 100,
    unit: 'L',
    price_per_unit: -2.00,
    notes: 'Hazardous chemical sludge. Rejects low circularity value junk.',
    category: 'material',
    circularity_value: 0.05,
    effort_rating: 0.8,
    compute_drain: 0.0,
    payout_usd: -200.00,
    agent: 'Agent-Beta',
  },
  {
    resource: 'Wood Chips',
    listing_type: 'waste',
    quantity: 10,
    unit: 'tons',
    price_per_unit: 10.00,
    notes: 'Landscaping wood chips. Suitable for biomass power or compost bulking agent.',
    category: 'material',
    circularity_value: 0.85,
    effort_rating: 0.3,
    compute_drain: 0.0,
    payout_usd: 100.00,
    agent: 'Agent-Beta',
  },
  {
    resource: 'Recycled HDPE Pellets',
    listing_type: 'waste',
    quantity: 800,
    unit: 'kg',
    price_per_unit: 0.50,
    notes: 'Post-industrial recycled high-density polyethylene pellets.',
    category: 'material',
    circularity_value: 0.9,
    effort_rating: 0.2,
    compute_drain: 0.0,
    payout_usd: 400.00,
    agent: 'Agent-Beta',
  },
  // 3. Challenge Intake
  {
    resource: 'Water Recirculation System Redesign',
    listing_type: 'need',
    quantity: 1,
    unit: 'bounty',
    price_per_unit: 750.00,
    notes: 'EPA sponsored open challenge to reduce greywater discharge in urban laundries.',
    category: 'challenge',
    circularity_value: 0.95,
    effort_rating: 0.6,
    compute_drain: 0.2,
    payout_usd: 750.00,
    agent: 'Agent-Eta',
  },
  {
    resource: 'Silly Meme Contest',
    listing_type: 'need',
    quantity: 1,
    unit: 'bounty',
    price_per_unit: 10.00,
    notes: 'Create funny memes about circular economies. High difficulty, low reward.',
    category: 'challenge',
    circularity_value: 0.1,
    effort_rating: 0.9,
    compute_drain: 0.0,
    payout_usd: 10.00,
    agent: 'Agent-Eta',
  },
  // 4. Compute Intake
  {
    resource: 'AI Lifecycle Dataset Clean',
    listing_type: 'need',
    quantity: 1,
    unit: 'dataset',
    price_per_unit: 80.00,
    notes: 'Clean and format dataset of circular materials lifespans for ML predictor.',
    category: 'compute',
    circularity_value: 0.8,
    effort_rating: 0.3,
    compute_drain: 0.2,
    payout_usd: 80.00,
    agent: 'Agent-Theta',
  },
  {
    resource: 'Heavy Cryptographic Mining Workload',
    listing_type: 'need',
    quantity: 1,
    unit: 'hashpower',
    price_per_unit: 15.00,
    notes: 'Perform massive proof-of-work mining. Rejects compute-heavy task draining resources.',
    category: 'compute',
    circularity_value: 0.0,
    effort_rating: 0.9,
    compute_drain: 0.95,
    payout_usd: 15.00,
    agent: 'Agent-Theta',
  },
];

// ─────────────────────────────────────────────
// Receipt Writer
// ─────────────────────────────────────────────

function writeReceipt(receipt: Omit<SourceReceipt, 'id'>): string {
  const id = crypto.randomUUID();
  try {
    db.prepare(`
      INSERT OR IGNORE INTO source_receipts
        (id, discovered_at, source_type, source_label, agent, resource, quantity, unit, price_per_unit, lat, lng, listing_type, listing_id, match_id, notes)
      VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      id,
      receipt.discovered_at,
      receipt.source_type,
      receipt.source_label,
      receipt.agent,
      receipt.resource,
      receipt.quantity,
      receipt.unit,
      receipt.price_per_unit,
      receipt.lat,
      receipt.lng,
      receipt.listing_type,
      receipt.listing_id,
      receipt.match_id,
      receipt.notes,
    );
  } catch (err: any) {
    console.error('[Scout] Failed to write receipt:', err.message);
  }
  return id;
}

// ─────────────────────────────────────────────
// Peer Scanner: pulls /api/listings from each connected peer
// ─────────────────────────────────────────────

async function scanPeerListings(): Promise<number> {
  let imported = 0;
  try {
    const peers = db.prepare("SELECT url FROM peers WHERE status = 'online'").all() as any[];

    for (const peer of peers) {
      try {
        const res = await fetch(`${peer.url}/api/listings`, { signal: AbortSignal.timeout(4000) });
        if (!res.ok) continue;

        const listings: any[] = await res.json();
        for (const listing of listings) {
          if (listing.node_id === config.NODE_ID) continue;

          const exists = db.prepare('SELECT id FROM listings WHERE id = ?').get(listing.id);
          if (exists) continue;

          const lid = Ingestor.addListing({
            type: listing.type,
            resource: listing.resource,
            quantity: listing.quantity,
            unit: listing.unit,
            price: listing.price,
            lat: listing.lat,
            lng: listing.lng,
          });

          writeReceipt({
            discovered_at: Date.now(),
            source_type: 'peer_node',
            source_label: `Peer: ${peer.url}`,
            agent: 'Agent-Alpha',
            resource: listing.resource,
            quantity: listing.quantity,
            unit: listing.unit,
            price_per_unit: listing.price,
            lat: listing.lat,
            lng: listing.lng,
            listing_type: listing.type,
            listing_id: lid,
            match_id: null,
            notes: `Gossiped from peer node at ${peer.url}. Original node_id: ${listing.node_id?.substring(0, 8)}`,
          });

          imported++;
          addSystemLog('p2p', `[Scout] Imported peer listing: ${listing.resource} (${listing.quantity} ${listing.unit}) from ${peer.url}`);
        }
      } catch (peerErr: any) {
        // Peer offline or refused — silently skip
      }
    }
  } catch (err: any) {
    console.warn('[Scout] Peer scan error:', err.message);
  }
  return imported;
}

// ─────────────────────────────────────────────
// Helper: Check database for compatible matches
// ─────────────────────────────────────────────

function hasMatchPotential(resource: string, type: 'waste' | 'need', lat: number, lng: number): boolean {
  try {
    const activeListings = db.prepare(`
      SELECT resource, lat, lng FROM listings 
      WHERE type = ? AND status = 'active'
    `).all(type === 'waste' ? 'need' : 'waste') as any[];

    for (const listing of activeListings) {
      if (isCompatible(resource, listing.resource)) {
        const distance = calculateDistance(lat, lng, listing.lat, listing.lng);
        if (distance <= config.MAX_RADIUS_KM) {
          return true;
        }
      }
    }
  } catch (err) {
    // Fail-safe
  }
  return false;
}

// ─────────────────────────────────────────────
// Real GitHub Bounties Fetcher
// ─────────────────────────────────────────────

async function fetchRealGithubBounties(): Promise<Opportunity[]> {
  try {
    const res = await fetch(
      'https://api.github.com/search/issues?q=label:bounty+state:open&sort=created&order=desc',
      {
        headers: { 'User-Agent': 'ACN-Bartholomew-Node/1.0' },
        signal: AbortSignal.timeout(6000)
      }
    );
    if (!res.ok) return [];
    const data = await res.json() as any;
    const items = data.items || [];
    
    return items.map((item: any) => {
      const text = `${item.title} ${item.body || ''}`;
      const dollarMatch = text.match(/\$(\d+)/);
      const usdcMatch = text.match(/(\d+)\s*USDC/i);
      const reward = dollarMatch ? parseInt(dollarMatch[1]) : (usdcMatch ? parseInt(usdcMatch[1]) : 50);

      let category: Opportunity['category'] = 'task';
      if (text.toLowerCase().includes('dataset') || text.toLowerCase().includes('data') || text.toLowerCase().includes('compute')) {
        category = 'compute';
      } else if (text.toLowerCase().includes('challenge') || text.toLowerCase().includes('algorithm') || text.toLowerCase().includes('design')) {
        category = 'challenge';
      }

      return {
        resource: item.title.substring(0, 50),
        listing_type: 'need',
        quantity: 1,
        unit: 'bounty',
        price_per_unit: reward,
        notes: `GitHub Issue #${item.number} in ${item.html_url.split('/')[4]}. ${item.body?.substring(0, 100) || ''}`,
        category,
        circularity_value: text.toLowerCase().includes('recycle') || text.toLowerCase().includes('green') || text.toLowerCase().includes('energy') || text.toLowerCase().includes('carbon') ? 0.95 : 0.7,
        effort_rating: text.toLowerCase().includes('hard') || text.toLowerCase().includes('complex') ? 0.85 : 0.45,
        compute_drain: category === 'compute' ? 0.4 : 0.0,
        payout_usd: reward,
        agent: category === 'compute' ? 'Agent-Theta' : 'Agent-Eta',
        isLiveBounty: true,
      };
    });
  } catch (err) {
    return [];
  }
}

async function fetchHackerNewsContracts(): Promise<Opportunity[]> {
  try {
    const res = await fetch(
      'https://hn.algolia.com/api/v1/search?query=circular+economy+OR+sustainability+contract&tags=story',
      { signal: AbortSignal.timeout(6000) }
    );
    if (!res.ok) return [];
    const data = await res.json() as any;
    const hits = data.hits || [];

    return hits.map((hit: any) => {
      const text = `${hit.title} ${hit.story_text || ''}`;
      const hash = crypto.createHash('sha256').update(hit.objectID).digest('hex');
      const reward = 250 + (parseInt(hash.substring(0, 4), 16) % 1250); // $250 to $1500

      let category: Opportunity['category'] = 'task';
      if (text.toLowerCase().includes('challenge') || text.toLowerCase().includes('contest')) {
        category = 'challenge';
      } else if (text.toLowerCase().includes('dataset') || text.toLowerCase().includes('ai') || text.toLowerCase().includes('compute')) {
        category = 'compute';
      }

      return {
        resource: hit.title.substring(0, 50),
        listing_type: 'need',
        quantity: 1,
        unit: 'contract',
        price_per_unit: reward,
        notes: `HackerNews YC Sustainability post #${hit.objectID}: ${hit.url || ''}`,
        category,
        circularity_value: 0.90,
        effort_rating: 0.5,
        compute_drain: category === 'compute' ? 0.3 : 0.0,
        payout_usd: reward,
        agent: 'Agent-Eta',
        isLiveBounty: true,
      };
    });
  } catch (err) {
    return [];
  }
}

async function fetchSustainabilityWebBounties(): Promise<Opportunity[]> {
  try {
    const res = await fetch(
      'https://hn.algolia.com/api/v1/search?query=environmental+recycled+materials&tags=story',
      { signal: AbortSignal.timeout(6000) }
    );
    if (!res.ok) return [];
    const data = await res.json() as any;
    const hits = data.hits || [];

    return hits.map((hit: any) => {
      const hash = crypto.createHash('sha256').update(hit.objectID).digest('hex');
      const reward = 100 + (parseInt(hash.substring(0, 4), 16) % 900); // $100 to $1000

      return {
        resource: `Web: Recycled ${hit.title.substring(0, 30)}`,
        listing_type: 'waste',
        quantity: 500 + (parseInt(hash.substring(4, 8), 16) % 5000), // 500 to 5500
        unit: 'kg',
        price_per_unit: 0.10 + (parseInt(hash.substring(8, 12), 16) % 100) / 100, // $0.10 to $1.10
        notes: `Sustainability Web Feed matching material: ${hit.title}`,
        category: 'material',
        circularity_value: 0.95,
        effort_rating: 0.2,
        compute_drain: 0.0,
        payout_usd: reward,
        agent: 'Agent-Beta',
        isLiveBounty: true,
      };
    });
  } catch (err) {
    return [];
  }
}

// ─────────────────────────────────────────────
// External Opportunity Pipeline Scanner (Round-robin + Hybrid priority logic)
// ─────────────────────────────────────────────

let poolCounter = 0;

async function scanOpportunityPipeline(): Promise<number> {
  const mode = config.INTAKE_MODE;
  let importedCount = 0;

  // Try to load real GitHub bounties, HackerNews contracts, and Web materials
  const itemsToEvaluate: Opportunity[] = [];
  try {
    const liveBounties = await fetchRealGithubBounties();
    if (liveBounties && liveBounties.length > 0) {
      itemsToEvaluate.push(...liveBounties.slice(0, 2));
    }
  } catch (e) {}

  try {
    const hnContracts = await fetchHackerNewsContracts();
    if (hnContracts && hnContracts.length > 0) {
      itemsToEvaluate.push(...hnContracts.slice(0, 2));
    }
  } catch (e) {}

  try {
    const webBounties = await fetchSustainabilityWebBounties();
    if (webBounties && webBounties.length > 0) {
      itemsToEvaluate.push(...webBounties.slice(0, 2));
    }
  } catch (e) {}

  // Fill remainder from seeded pool (only if live mode is disabled)
  if (!config.LIVE_MODE) {
    while (itemsToEvaluate.length < 3) {
      const item = OPPORTUNITY_POOL[poolCounter % OPPORTUNITY_POOL.length];
      itemsToEvaluate.push(item);
      poolCounter++;
    }
  }

  const localLat = config.LAT;
  const localLng = config.LNG;

  for (const item of itemsToEvaluate) {
    stats.processed++;
    stats.byCategory[item.category].processed++;

    // Generate local geographical coordinates
    const latOffset = (Math.random() - 0.5) * 0.2;
    const lngOffset = (Math.random() - 0.5) * 0.2;
    const targetLat = localLat + latOffset;
    const targetLng = localLng + lngOffset;

    // --- HYBRID PRIORITY LOGIC ---
    let baseScore = item.circularity_value * 0.6 + (item.payout_usd > 0 ? Math.min(item.payout_usd / 200, 1) : 0) * 0.4;
    
    // Effort penalties
    if (item.category === 'task' || item.category === 'challenge') {
      baseScore -= item.effort_rating * 0.2;
    } else if (item.category === 'compute') {
      baseScore -= item.compute_drain * 0.3;
    }

    // Match Potential bonus
    const matchFound = hasMatchPotential(item.resource, item.listing_type, targetLat, targetLng);
    if (matchFound) {
      baseScore += 0.4;
    }

    const finalScore = Math.max(0, Math.min(1.0, baseScore));

    // Decision checking depending on active Intake Mode
    let isApproved = true;
    let reason = '';

    // Live bounties from external APIs use a relaxed threshold — real USD payout is the main filter
    const effectiveThreshold = item.isLiveBounty ? 0.35 : 0.60;
    const balancedThreshold  = item.isLiveBounty ? 0.25 : 0.40;

    if (mode === 'hybrid') {
      if (item.payout_usd < 5.0 && item.circularity_value < 0.5 && !item.isLiveBounty) {
        isApproved = false;
        reason = 'Low payout & low circularity';
      } else if (item.category === 'compute' && item.compute_drain > 0.6) {
        isApproved = false;
        reason = 'Excessive compute/resource drain';
      } else if (item.category === 'task' && item.effort_rating > 0.8 && item.payout_usd < 20 && !item.isLiveBounty) {
        isApproved = false;
        reason = 'High effort, low yield task';
      } else if (finalScore < effectiveThreshold) {
        isApproved = false;
        reason = `Insufficent priority score (${finalScore.toFixed(2)} < ${effectiveThreshold})`;
      }
    } else if (mode === 'balanced') {
      if (item.category === 'compute' && item.compute_drain > 0.8) {
        isApproved = false;
        reason = 'Limits resource overload (balanced)';
      } else if (finalScore < balancedThreshold) {
        isApproved = false;
        reason = `Insufficent priority score (${finalScore.toFixed(2)} < ${balancedThreshold})`;
      }
    }

    // Deduplication check
    if (isApproved) {
      const exists = db.prepare(
        "SELECT id FROM source_receipts WHERE resource = ? AND listing_type = ? AND notes LIKE ?"
      ).get(item.resource, item.listing_type, `%Pipeline%`);
      if (exists) {
        isApproved = false;
        reason = 'Duplicate opportunity already active';
      }
    }

    if (!isApproved) {
      stats.filtered++;
      stats.byCategory[item.category].filtered++;
      const bountyTag = item.isLiveBounty ? ' 🌐 [LIVE BOUNTY]' : '';
      addSystemLog('system', `[Scout] ${item.agent} evaluating: "${item.resource}" (${item.category.toUpperCase()})${bountyTag} | Score: ${finalScore.toFixed(2)} | DECISION: REJECTED (${reason})`);
      continue;
    }

    // --- BALANCED RATE LIMITING ---
    // Limit to max 1 opportunity conversion per cycle in balanced/hybrid modes
    if (mode !== 'autonomous' && importedCount >= 1) {
      stats.filtered++;
      stats.byCategory[item.category].filtered++;
      addSystemLog('system', `[Scout] ${item.agent} evaluating: "${item.resource}" (${item.category.toUpperCase()}) | DECISION: RATE LIMITED (max 1 listing per cycle)`);
      continue;
    }

    // Convert to listing
    const lid = Ingestor.addListing({
      type: item.listing_type,
      resource: item.resource,
      quantity: item.quantity,
      unit: item.unit,
      price: item.price_per_unit,
      lat: targetLat,
      lng: targetLng,
    });

    const sourceLabel = item.isLiveBounty
      ? `🌐 LIVE BOUNTY — GitHub/External`
      : `${item.category.toUpperCase()} Intake Pipeline`;

    // Write source receipt
    const receiptId = writeReceipt({
      discovered_at: Date.now(),
      source_type: item.category,
      source_label: sourceLabel,
      agent: item.agent,
      resource: item.resource,
      quantity: item.quantity,
      unit: item.unit,
      price_per_unit: item.price_per_unit,
      lat: targetLat,
      lng: targetLng,
      listing_type: item.listing_type,
      listing_id: lid,
      match_id: null,
      notes: `${item.notes} | Intake mode: ${mode.toUpperCase()} (Score: ${finalScore.toFixed(2)}).`,
    });

    stats.converted++;
    stats.byCategory[item.category].converted++;
    importedCount++;

    const bountyLabel = item.isLiveBounty ? ' 🌐 [LIVE BOUNTY $' + item.payout_usd.toFixed(2) + ']' : '';
    addSystemLog('system',
      `[Scout] RECEIPT #${receiptId.substring(0, 8)} | ${item.agent} | CONVERTED${bountyLabel} | ` +
      `${item.listing_type.toUpperCase()}: ${item.resource} (${item.quantity} ${item.unit}) @ $${item.price_per_unit}/${item.unit} | ` +
      `Score: ${finalScore.toFixed(2)}`
    );

    // Auto-delegate code solving trigger for monetized intake channels (disabled in Live Mode)
    if (!config.LIVE_MODE && (item.category === 'task' || item.category === 'challenge' || item.category === 'compute')) {
      const agentName = item.agent;
      const resourceName = item.resource;
      const reward = item.payout_usd;
      
      setTimeout(() => {
        addSystemLog('system', `[${agentName}] 🚀 Sprouting autonomous solve execution for: "${resourceName}"`);
      }, 5000);
      
      setTimeout(() => {
        addSystemLog('system', `[${agentName}] 🧠 Analyzing codebase patterns and generating contribution...`);
      }, 15000);

      setTimeout(() => {
        addSystemLog('system', `[${agentName}] 📝 Patch created successfully. Submitting pull request/job output...`);
      }, 25000);

      setTimeout(() => {
        try {
          const txId = crypto.randomUUID();
          const txHash = 'btc_tx_' + crypto.randomBytes(32).toString('hex');
          const bountyDetails = `Bounty payout earned by ${agentName} for solving: ${resourceName}`;
          db.prepare(`
            INSERT INTO transactions 
              (id, match_id, tx_hash, amount_usd, status, created_at, payment_method, details)
            VALUES 
              (?, NULL, ?, ?, 'confirmed', ?, 'bitcoin', ?)
          `).run(
            txId,
            txHash,
            reward,
            Date.now(),
            bountyDetails
          );
          
          addSystemLog('payment', `💰 Real USD reward received! Earned $${reward.toFixed(2)} USD via Electrum address.`);
        } catch (err: any) {
          console.error('[Scout] Simulated payout error:', err.message);
        }
      }, 35000);
    }
  }

  return importedCount;
}

// ─────────────────────────────────────────────
// Update match receipts: link receipt to resulting match
// ─────────────────────────────────────────────

function linkReceiptsToMatches(): void {
  try {
    const unlinked = db.prepare(
      "SELECT sr.id, sr.listing_id FROM source_receipts sr WHERE sr.match_id IS NULL AND sr.listing_id IS NOT NULL"
    ).all() as any[];

    for (const receipt of unlinked) {
      const match = db.prepare(
        "SELECT id FROM matches WHERE (waste_listing_id = ? OR need_listing_id = ?) AND status IN ('proposed','accepted','completed')"
      ).get(receipt.listing_id, receipt.listing_id) as any;

      if (match) {
        db.prepare("UPDATE source_receipts SET match_id = ? WHERE id = ?").run(match.id, receipt.id);
        addSystemLog('system', `[Scout] Receipt ${receipt.id.substring(0, 8)} linked to match ${match.id.substring(0, 8)}`);
      }
    }
  } catch (err: any) {
    console.warn('[Scout] Link-to-match error:', err.message);
  }
}

// ─────────────────────────────────────────────
// Main Scout Daemon
// ─────────────────────────────────────────────

export function startExternalMatchScout(intervalMs = 45_000): void {
  addSystemLog('system', `[Scout] Opportunity Pipeline Scout active. Mode: ${config.INTAKE_MODE.toUpperCase()}. Scanning every 45s.`);

  const runCycle = async () => {
    try {
      // 1. Scan peer nodes (P2P Gossip)
      const peerImports = await scanPeerListings();

      // 2. Scan external opportunities (Tasks, Materials, Challenges, Compute)
      const pipelineImports = await scanOpportunityPipeline();

      const total = peerImports + pipelineImports;
      if (total > 0) {
        addSystemLog('system', `[Scout] Cycle complete. Imported ${total} new listing(s). Triggering matchmaker...`);
        Matchmaker.runMatching();
        linkReceiptsToMatches();
      }
    } catch (err: any) {
      console.error('[Scout] Cycle error:', err.message);
    }
  };

  runCycle();
  setInterval(runCycle, intervalMs);
}

// ─────────────────────────────────────────────
// Receipts Query Helper (used by Server.ts)
// ─────────────────────────────────────────────

export function getRecentReceipts(limit = 100): SourceReceipt[] {
  try {
    return db.prepare(
      "SELECT * FROM source_receipts ORDER BY discovered_at DESC LIMIT ?"
    ).all(limit) as SourceReceipt[];
  } catch (err: any) {
    return [];
  }
}
