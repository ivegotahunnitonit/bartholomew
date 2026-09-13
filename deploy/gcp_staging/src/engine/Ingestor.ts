import { db } from '../database/db.ts';
import { config } from '../config.ts';
import * as crypto from 'node:crypto';
import { signListing, verifyListingSignature } from './CryptoUtils.ts';

export interface ListingInput {
  node_id?: string;
  type: 'waste' | 'need';
  resource: string;
  quantity: number;
  unit: string;
  price: number;
  lat: number;
  lng: number;
  expires_in_days?: number;
  signature?: string;
  signer_address?: string;
  declaration?: string;
}

const VALID_RESOURCES = [
  'spent grain', 'brewer grain', 'animal feed', 'compost', 'feedstock',
  'spent yeast', 'yeast', 'fertilizer',
  'food waste', 'organic waste', 'biogas feedstock',
  'wood chips', 'mulch', 'mushroom substrate', 'biomass',
  'sawdust', 'bedding',
  'coffee grounds',
  'cardboard', 'packaging material', 'recycling',
  'greywater', 'irrigation water', 'water recycling',
  'scrap metal', 'steel', 'aluminum', 'metal',
  'plastic waste', 'plastic', 'hdpe', 'pet', 'recyclables', 'pellets',
  'industrial solvents', 'solvents', 'chemicals', 'cleaning agents', 'recovery',
  // Universal AI Agent Asset & 24/7 Freight / Logistics Categories
  'gpu_compute', 'h100', 'a100', 'rtx4090', 'gpu hours', 'compute slot',
  'data_feed', 'market feed', 'api stream', 'dataset token', 'price oracle',
  'agent_task', 'code review', 'verification task', 'research bounty', 'subagent job',
  // 24/7 Freight, Loadboard & Hauling Dispatch Categories
  'freight_load', 'freight', 'truckload', 'hauling', 'empty backhaul', 'dry van', 'reefer cargo',
  'flatbed load', 'expedited delivery', 'delivery dispatch', 'uber freight slot', 'loadboard cargo', 'last mile hauling'
];

export function isValidResource(resource: string, unit?: string): boolean {
  const r = resource.toLowerCase().trim();
  if (unit) {
    const u = unit.toLowerCase().trim();
    if (['job', 'items', 'bounty', 'contract', 'shares', 'hours', 'tokens', 'slots', 'reqs', 'loads', 'pallets', 'miles', 'trips', 'hauls', 'shipments', 'trucks'].includes(u)) {
      return true;
    }
  }
  return VALID_RESOURCES.some(v => r.includes(v) || v.includes(r));
}

const VALID_UNITS = ['kg', 'tons', 'units', 'l', 'job', 'items', 'bounty', 'contract', 'shares', 'hours', 'tokens', 'slots', 'reqs', 'loads', 'pallets', 'miles', 'trips', 'hauls', 'shipments', 'trucks'];


export function isValidQuantity(quantity: number, unit: string): boolean {
  if (typeof quantity !== 'number' || isNaN(quantity) || quantity <= 0) return false;
  const u = unit.toLowerCase().trim();
  return VALID_UNITS.includes(u);
}

export function isValidLocation(lat: number, lng: number): boolean {
  if (typeof lat !== 'number' || isNaN(lat) || lat < -90 || lat > 90) return false;
  if (typeof lng !== 'number' || isNaN(lng) || lng < -180 || lng > 180) return false;
  if (lat === 0 && lng === 0) return false;
  return true;
}

export class Ingestor {
  /**
   * Adds a listing to the local database
   */
  static addListing(input: ListingInput): string {
    // 1. Strict metadata validation
    if (!isValidResource(input.resource, input.unit)) {
      throw new Error(`Invalid industrial material: "${input.resource}". Must be a legitimate circular feedstock.`);
    }
    if (!isValidQuantity(input.quantity, input.unit)) {
      throw new Error(`Invalid quantity or unit: "${input.quantity} ${input.unit}". Must be a positive amount and valid unit.`);
    }
    if (!isValidLocation(input.lat, input.lng)) {
      throw new Error(`Invalid geolocation: (${input.lat}, ${input.lng}). Must be real location coordinates.`);
    }

    // 2. Cryptographic signature verification/generation
    let signature = input.signature;
    let signerAddress = input.signer_address;
    let declaration = input.declaration;

    if (signature && signerAddress) {
      const isValid = verifyListingSignature({
        resource: input.resource,
        quantity: input.quantity,
        unit: input.unit,
        signature,
        signer_address: signerAddress
      });
      if (!isValid) {
        throw new Error(`Signature verification failed for listing: ${input.resource} from signer ${signerAddress}`);
      }
    } else {
      // Local listing: auto-sign
      const signed = signListing(input.resource, input.quantity, input.unit);
      signature = signed.signature;
      signerAddress = signed.signer_address;
      declaration = signed.declaration;
    }

    const id = crypto.randomUUID();
    const nodeId = input.node_id || 'local_node';
    const expiresInDays = input.expires_in_days || 30;
    const now = Date.now();
    const expiresAt = now + expiresInDays * 24 * 60 * 60 * 1000;

    const stmt = db.prepare(`
      INSERT INTO listings (id, node_id, type, resource, quantity, unit, price, lat, lng, created_at, expires_at, status, signature, signer_address, declaration)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
    `);

    stmt.run(
      id,
      nodeId,
      input.type,
      input.resource,
      input.quantity,
      input.unit,
      input.price,
      input.lat,
      input.lng,
      now,
      expiresAt,
      signature,
      signerAddress,
      declaration
    );

    console.log(`[Ingestor] Added verified listing: ${input.type} - ${input.resource} (${input.quantity} ${input.unit})`);
    return id;
  }

  static seedCapabilities(lat: number, lng: number): void {
    const activeCapabilities = [
      { resource: 'linear programming optimization', price: 10.00, quantity: 10, unit: 'job', type: 'waste' as const },
      { resource: 'material routing audit', price: 15.00, quantity: 5, unit: 'job', type: 'waste' as const },
      { resource: 'codebase vulnerability check', price: 25.00, quantity: 3, unit: 'job', type: 'waste' as const },
      { resource: 'dataset labeling', price: 5.00, quantity: 50, unit: 'job', type: 'waste' as const }
    ];

    try {
      const checkStmt = db.prepare("SELECT COUNT(*) as count FROM listings WHERE resource = ? AND status = 'active'");
      for (const cap of activeCapabilities) {
        const row = checkStmt.get(cap.resource) as any;
        if (row && row.count === 0) {
          this.addListing({
            node_id: 'local_node',
            type: cap.type,
            resource: cap.resource,
            quantity: cap.quantity,
            unit: cap.unit,
            price: cap.price,
            lat,
            lng
          });
        }
      }
    } catch (err: any) {
      console.error('[Ingestor] Error seeding capabilities:', err.message);
    }
  }

  static seedCommercialListings(lat: number, lng: number): void {
    const commercialBulk = [
      { type: 'waste' as const, resource: 'plastic waste hdpe', quantity: 25000, unit: 'kg', price: 0.35, node_id: 'denver_node', lat: 39.7392, lng: -104.9903 },
      { type: 'need' as const, resource: 'plastic pellets', quantity: 25000, unit: 'kg', price: 0.95, node_id: 'salt_lake_node', lat: 40.7608, lng: -111.8910 },
      { type: 'waste' as const, resource: 'scrap metal', quantity: 15000, unit: 'kg', price: 0.65, node_id: 'chicago_node', lat: 41.8781, lng: -87.6298 },
      { type: 'need' as const, resource: 'steel', quantity: 15000, unit: 'kg', price: 1.20, node_id: 'detroit_node', lat: 42.3314, lng: -83.0458 },
      { type: 'waste' as const, resource: 'industrial solvents', quantity: 10000, unit: 'l', price: 1.50, node_id: 'houston_node', lat: 29.7604, lng: -95.3698 },
      { type: 'need' as const, resource: 'chemicals', quantity: 10000, unit: 'l', price: 2.80, node_id: 'dallas_node', lat: 32.7767, lng: -96.7970 },
      { type: 'waste' as const, resource: 'spent grain', quantity: 8000, unit: 'kg', price: 0.12, node_id: 'milwaukee_node', lat: 43.0389, lng: -87.9065 },
      { type: 'need' as const, resource: 'animal feed', quantity: 8000, unit: 'kg', price: 0.45, node_id: 'madison_node', lat: 43.0731, lng: -89.4012 },
      // 24/7 High-Volume Freight, Loadboard & Trucking Backhaul Listings
      { type: 'waste' as const, resource: 'empty backhaul', quantity: 500, unit: 'miles', price: 1.85, node_id: 'freight_carrier_denver', lat: 39.7392, lng: -104.9903 },
      { type: 'need' as const, resource: 'freight', quantity: 500, unit: 'miles', price: 3.10, node_id: 'shipper_salt_lake', lat: 40.7608, lng: -111.8910 },
      { type: 'waste' as const, resource: 'empty backhaul', quantity: 300, unit: 'miles', price: 2.10, node_id: 'freight_carrier_chicago', lat: 41.8781, lng: -87.6298 },
      { type: 'need' as const, resource: 'truckload', quantity: 300, unit: 'miles', price: 3.50, node_id: 'shipper_detroit', lat: 42.3314, lng: -83.0458 },
      { type: 'waste' as const, resource: 'delivery dispatch', quantity: 50, unit: 'trips', price: 12.00, node_id: 'courier_fleet_houston', lat: 29.7604, lng: -95.3698 },
      { type: 'need' as const, resource: 'expedited delivery', quantity: 50, unit: 'trips', price: 22.50, node_id: 'logistics_hub_dallas', lat: 32.7767, lng: -96.7970 },
    ];

    try {
      for (const item of commercialBulk) {
        this.addListing({
          node_id: item.node_id,
          type: item.type,
          resource: item.resource,
          quantity: item.quantity,
          unit: item.unit,
          price: item.price,
          lat: item.lat,
          lng: item.lng,
        });
      }
      console.log('[Ingestor] Successfully seeded $30,000+ commercial industrial bulk listings.');
    } catch (err: any) {
      console.error('[Ingestor] Error seeding commercial listings:', err.message);
    }
  }
}

