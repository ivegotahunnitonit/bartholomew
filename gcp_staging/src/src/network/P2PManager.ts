import { db } from '../database/db.ts';
import { config } from '../config.ts';
import * as crypto from 'node:crypto';
import type { Listing } from '../engine/Matchmaker.ts';
import { verifyListingSignature, verifyMatchSignature, verifyTransactionSignature } from '../engine/CryptoUtils.ts';

function getAuthHeaders(bodyString: string): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (config.ACN_NETWORK_SECRET) {
    headers['x-acn-signature'] = crypto.createHmac('sha256', config.ACN_NETWORK_SECRET).update(bodyString).digest('hex');
  }
  return headers;
}

export interface PeerNode {
  url: string;
  node_id: string | null;
  lat: number | null;
  lng: number | null;
  last_seen: number | null;
  status: 'online' | 'offline';
  score?: number;
  uptime_count?: number;
  total_checks?: number;
}

export class P2PManager {
  /**
   * Fetch all peers stored in SQLite
   */
  static getPeers(): PeerNode[] {
    try {
      const stmt = db.prepare("SELECT * FROM peers");
      return stmt.all() as any[] as PeerNode[];
    } catch (err) {
      console.error('[P2P] Error fetching peers:', err);
      return [];
    }
  }

  /**
   * Save or update a peer node entry in SQLite
   */
  static upsertPeer(peer: Omit<PeerNode, 'status'> & { status?: 'online' | 'offline', score?: number, uptime_count?: number, total_checks?: number }) {
    const status = peer.status || 'online';
    const now = Date.now();
    
    // Prevent registering self
    const selfUrl = `http://localhost:${config.PORT}`;
    if (peer.url === selfUrl || peer.url === `http://127.0.0.1:${config.PORT}`) {
      return;
    }

    try {
      const stmt = db.prepare(`
        INSERT INTO peers (url, node_id, lat, lng, last_seen, status, score, uptime_count, total_checks)
        VALUES (?, ?, ?, ?, ?, ?, COALESCE(?, 1.0), COALESCE(?, 0), COALESCE(?, 0))
        ON CONFLICT(url) DO UPDATE SET
          node_id = COALESCE(excluded.node_id, peers.node_id),
          lat = COALESCE(excluded.lat, peers.lat),
          lng = COALESCE(excluded.lng, peers.lng),
          last_seen = excluded.last_seen,
          status = excluded.status,
          score = COALESCE(excluded.score, peers.score),
          uptime_count = COALESCE(excluded.uptime_count, peers.uptime_count),
          total_checks = COALESCE(excluded.total_checks, peers.total_checks)
      `);
      stmt.run(
        peer.url,
        peer.node_id,
        peer.lat,
        peer.lng,
        now,
        status,
        peer.score !== undefined ? peer.score : null,
        peer.uptime_count !== undefined ? peer.uptime_count : null,
        peer.total_checks !== undefined ? peer.total_checks : null
      );
      const displayScore = peer.score !== undefined ? peer.score : 1.0;
      console.log(`[P2P] Registered/Updated peer: ${peer.url} (${status}) | Score: ${displayScore.toFixed(2)}`);
    } catch (err) {
      console.error(`[P2P] Error writing peer ${peer.url}:`, err);
    }
  }

  /**
   * Register our node with a remote peer
   */
  static async registerWithPeer(peerUrl: string): Promise<boolean> {
    const selfUrl = `http://localhost:${config.PORT}`;
    console.log(`[P2P] Registering our node with peer: ${peerUrl}...`);

    try {
      const bodyString = JSON.stringify({
        url: selfUrl,
        node_id: config.NODE_ID,
        lat: config.LAT,
        lng: config.LNG,
      });
      const res = await fetch(`${peerUrl}/p2p/register`, {
        method: 'POST',
        headers: getAuthHeaders(bodyString),
        body: bodyString,
      });

      if (res.ok) {
        const data = await res.json() as any;
        this.upsertPeer({
          url: peerUrl,
          node_id: data.node_id,
          lat: data.lat,
          lng: data.lng,
          last_seen: Date.now(),
          status: 'online',
        });
        return true;
      }
    } catch (err: any) {
      console.warn(`[P2P] Failed to register with ${peerUrl}: ${err.message}`);
    }

    // Set peer to offline on failure
    this.upsertPeer({
      url: peerUrl,
      node_id: null,
      lat: null,
      lng: null,
      last_seen: Date.now(),
      status: 'offline',
    });
    return false;
  }

  /**
   * Connect to bootstrap nodes configured in .env
   */
  static async bootstrap() {
    console.log('[P2P] Initializing network bootstrapping...');
    const defaultPeers = [
      'http://35.255.62.200:8080',
      'http://34.73.34.145:8080',
      'http://136.117.15.127:8080',
      'http://34.20.133.4:8080',    // acn-supernode-gateway-4 (us-west2-a / Los Angeles)
      'http://34.53.176.111:8080',  // acn-supernode-gateway-5 (europe-west1-b / Belgium)
      ...config.BOOTSTRAP_PEERS,
    ];
    for (const peerUrl of defaultPeers) {
      let nodeId = 'acn-supernode-gateway-local';
      if (peerUrl.includes('35.255'))    nodeId = 'acn-supernode-gateway';
      else if (peerUrl.includes('34.73')) nodeId = 'acn-supernode-gateway-2';
      else if (peerUrl.includes('136.117')) nodeId = 'acn-supernode-gateway-3';
      else if (peerUrl.includes('34.20'))  nodeId = 'acn-supernode-gateway-4';
      else if (peerUrl.includes('34.53'))  nodeId = 'acn-supernode-gateway-5';


      this.upsertPeer({
        url: peerUrl,
        node_id: nodeId,
        lat: 39.7392,
        lng: -104.9903,
        last_seen: Date.now(),
        status: 'online',
        score: 1.0,
      });
      await this.registerWithPeer(peerUrl);
    }
  }

  /**
   * Autonomously scans local ports 8080-8120 to discover sibling ACN nodes
   */
  static async scanLocalPortPeers() {
    console.log('[P2P] Starting local port scan (8080-8120) to discover active peers...');
    for (let port = 8080; port <= 8120; port++) {
      if (port === config.PORT) continue;
      const peerUrl = `http://localhost:${port}`;
      try {
        const res = await fetch(`${peerUrl}/api/status`, { signal: AbortSignal.timeout(500) });
        if (res.ok) {
          const data = await res.json() as any;
          if (data.node_id && data.node_id !== config.NODE_ID) {
            console.log(`[P2P] Autonomous discovery: found sibling node on port ${port}! Validating and registering...`);
            await this.registerWithPeer(peerUrl);
          }
        }
      } catch (_) {
        // Ignored - port is closed or not an ACN instance
      }
    }
  }

  /**
   * Verify peer's integrity by checking signatures on its listings, matches, and transactions.
   * Returns true if peer is valid, false otherwise.
   */
  private static async verifyPeerDataIntegrity(peerUrl: string): Promise<boolean> {
    try {
      // 1. Fetch and verify listings
      const listingsRes = await fetch(`${peerUrl}/api/listings`, { signal: AbortSignal.timeout(3000) });
      if (listingsRes.ok) {
        const listings = await listingsRes.json() as any[];
        if (Array.isArray(listings)) {
          for (const listing of listings) {
            // Verify signature if listing is not local to that node (or check all signatures)
            if (listing.signature && listing.signer_address) {
              const isValid = verifyListingSignature(listing);
              if (!isValid) {
                console.warn(`[P2P] [SECURITY] Peer ${peerUrl} provided an invalid listing signature!`);
                return false;
              }
            }
          }
        } else {
          return false; // Bad response format
        }
      }

      // 2. Fetch and verify matches
      const matchesRes = await fetch(`${peerUrl}/api/matches`, { signal: AbortSignal.timeout(3000) });
      if (matchesRes.ok) {
        const matches = await matchesRes.json() as any[];
        if (Array.isArray(matches)) {
          for (const match of matches) {
            if (match.signature && match.signer_address) {
              const isValid = verifyMatchSignature(match);
              if (!isValid) {
                console.warn(`[P2P] [SECURITY] Peer ${peerUrl} provided an invalid match signature!`);
                return false;
              }
            }
          }
        } else {
          return false;
        }
      }

      // 3. Fetch and verify transactions
      const txsRes = await fetch(`${peerUrl}/api/transactions`, { signal: AbortSignal.timeout(3000) });
      if (txsRes.ok) {
        const txs = await txsRes.json() as any[];
        if (Array.isArray(txs)) {
          for (const tx of txs) {
            if (tx.signature && tx.signer_address) {
              const isValid = verifyTransactionSignature(tx);
              if (!isValid) {
                console.warn(`[P2P] [SECURITY] Peer ${peerUrl} provided an invalid transaction signature!`);
                return false;
              }
            }
          }
        } else {
          return false;
        }
      }

      return true;
    } catch (err: any) {
      console.warn(`[P2P] Integrity checks failed for peer ${peerUrl}:`, err.message);
      return false;
    }
  }

  /**
   * Ping all known peers, updates status and exchanges new peer lists
   */
  static async pingPeers() {
    const peers = this.getPeers();
    console.log(`[P2P] Running peer health and validation checks for ${peers.length} known peers...`);

    for (const peer of peers) {
      const totalChecks = (peer.total_checks || 0) + 1;
      let uptimeCount = peer.uptime_count || 0;
      
      try {
        const res = await fetch(`${peer.url}/api/status`, { signal: AbortSignal.timeout(3000) });
        if (res.ok) {
          const statusData = await res.json() as any;

          // Perform strict integrity verification of peer data
          const isIntegral = await this.verifyPeerDataIntegrity(peer.url);
          if (!isIntegral) {
            console.warn(`[P2P] Peer ${peer.url} failed integrity checks. Rejecting connection.`);
            this.upsertPeer({
              url: peer.url,
              node_id: statusData.node_id,
              lat: statusData.lat,
              lng: statusData.lng,
              last_seen: Date.now(),
              status: 'offline',
              score: 0.0,
              uptime_count: uptimeCount,
              total_checks: totalChecks,
            });
            continue;
          }

          uptimeCount++;
          const score = uptimeCount / totalChecks;

          this.upsertPeer({
            url: peer.url,
            node_id: statusData.node_id,
            lat: statusData.lat,
            lng: statusData.lng,
            last_seen: Date.now(),
            status: 'online',
            score,
            uptime_count: uptimeCount,
            total_checks: totalChecks,
          });

          // Fetch peer's routing table (other peers they know)
          await this.syncPeerRoutingTable(peer.url);
        } else {
          throw new Error('Non-200 status');
        }
      } catch (err: any) {
        console.warn(`[P2P] Ping failed for ${peer.url}: ${err.message}`);
        const score = uptimeCount / totalChecks;
        this.upsertPeer({
          url: peer.url,
          node_id: peer.node_id,
          lat: peer.lat,
          lng: peer.lng,
          last_seen: peer.last_seen,
          status: 'offline',
          score,
          uptime_count: uptimeCount,
          total_checks: totalChecks,
        });
      }
    }

    // Maintain a minimum of active online peers
    let onlinePeers = this.getPeers().filter(p => p.status === 'online');
    if (onlinePeers.length < config.MIN_PEERS_TARGET) {
      console.log(`[P2P] Online peers (${onlinePeers.length}) below target of ${config.MIN_PEERS_TARGET}. Attempting active discovery...`);
      await this.scanLocalPortPeers();
      
      // Re-query online peers list after scanning local ports
      onlinePeers = this.getPeers().filter(p => p.status === 'online');
    }

    // Recursive gossip discovery up to 3 levels deep to find more peers
    let depth = 0;
    while (onlinePeers.length < config.MIN_PEERS_TARGET && depth < 3) {
      console.log(`[P2P] [Supernode Discovery] Level ${depth + 1}: current peers ${onlinePeers.length}/${config.MIN_PEERS_TARGET}. Querying neighbors...`);
      const currentOnline = [...onlinePeers];
      let discoveredCount = 0;
      
      for (const peer of currentOnline) {
        try {
          const res = await fetch(`${peer.url}/p2p/peers`, { signal: AbortSignal.timeout(3000) });
          if (res.ok) {
            const remotePeers = await res.json() as PeerNode[];
            for (const remotePeer of remotePeers) {
              const allPeers = this.getPeers();
              const exists = allPeers.some(p => p.url === remotePeer.url);
              if (!exists && remotePeer.url !== `http://localhost:${config.PORT}` && remotePeer.url !== `http://127.0.0.1:${config.PORT}`) {
                console.log(`[P2P] [Supernode Discovery] Discovered peer: ${remotePeer.url}`);
                await this.registerWithPeer(remotePeer.url);
                discoveredCount++;
              }
            }
          }
        } catch (_) {
          // Ignore fetch errors during discovery
        }
      }
      
      onlinePeers = this.getPeers().filter(p => p.status === 'online');
      if (discoveredCount === 0) {
        // No new peers discovered, break out early
        break;
      }
      depth++;
    }

    if (onlinePeers.length < config.MIN_PEERS_TARGET && config.BOOTSTRAP_PEERS.length > 0) {
      console.log(`[P2P] Still below target. Retrying bootstrap nodes...`);
      await this.bootstrap();
    }
  }

  /**
   * Fetches peer's peer list and merges it locally (Gossip Discovery)
   */
  private static async syncPeerRoutingTable(peerUrl: string) {
    try {
      const res = await fetch(`${peerUrl}/p2p/peers`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const remotePeers = await res.json() as PeerNode[];
        for (const remotePeer of remotePeers) {
          // Register any peer we don't know yet
          const exists = this.getPeers().some(p => p.url === remotePeer.url);
          if (!exists) {
            console.log(`[P2P] Discovered new peer ${remotePeer.url} via gossip from ${peerUrl}`);
            await this.registerWithPeer(remotePeer.url);
          }
        }
      }
    } catch (err: any) {
      console.warn(`[P2P] Failed to fetch routing table from ${peerUrl}: ${err.message}`);
    }
  }

  /**
   * Gossip a listing to all active online peers
   */
  static async gossipListing(listing: Listing) {
    const peers = this.getPeers().filter(p => p.status === 'online');
    if (peers.length === 0) {
      return;
    }

    console.log(`[P2P] Gossiping listing: ${listing.resource} to ${peers.length} peers...`);
    for (const peer of peers) {
      try {
        const bodyString = JSON.stringify(listing);
        fetch(`${peer.url}/p2p/gossip`, {
          method: 'POST',
          headers: getAuthHeaders(bodyString),
          body: bodyString,
        }).catch(err => {
          console.warn(`[P2P] Gossip send failed for peer ${peer.url}:`, err.message);
        });
      } catch (err: any) {
        // Suppress print to avoid clogging logs
      }
    }
  }

  /**
   * Return number of online connected peers
   */
  static getConnectedPeerCount(): number {
    try {
      const stmt = db.prepare("SELECT COUNT(*) as count FROM peers WHERE status = 'online'");
      const row = stmt.get() as any;
      return row ? row.count : 0;
    } catch (err) {
      return 0;
    }
  }
}

