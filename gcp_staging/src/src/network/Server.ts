import * as http from 'node:http';
import * as fs from 'node:fs';
import * as crypto from 'node:crypto';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import { config, loadConfig, saveConfig } from '../config.ts';
import * as os from 'node:os';
import { db } from '../database/db.ts';
import { Ingestor } from '../engine/Ingestor.ts';
import type { ListingInput } from '../engine/Ingestor.ts';
import { Matchmaker } from '../engine/Matchmaker.ts';
import type { Listing } from '../engine/Matchmaker.ts';
import { P2PManager } from './P2PManager.ts';
import { PaymentManager } from '../settlement/PaymentManager.ts';
import { getRecentReceipts, getScoutStats } from '../engine/ExternalMatchScout.ts';
import { Bartholomew } from '../engine/Bartholomew.ts';
import { NodeOrchestrator } from './NodeOrchestrator.ts';
import { ArbitrageEngine } from '../settlement/ArbitrageEngine.ts';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ─── Security: only allow requests from localhost ───────────────────────────
const ALLOWED_ORIGINS = [
  'http://localhost',
  'http://127.0.0.1',
  'http://[::1]',
];

function getAllowedOrigin(req: any): string {
  const origin = req.headers['origin'] || '';
  const host   = req.headers['host']  || '';
  // Allow requests with no Origin header (curl, same-host fetch) if they come from loopback
  const remoteAddr = req.socket?.remoteAddress || '';
  const isLoopback = remoteAddr === '127.0.0.1' || remoteAddr === '::1' || remoteAddr === '::ffff:127.0.0.1';
  if (!origin && isLoopback) return '*'; // same-machine, no CORS header needed
  for (const allowed of ALLOWED_ORIGINS) {
    if (origin.startsWith(allowed)) return origin;
  }
  return ''; // blocked
}

// Helper to serve JSON responses
function sendJSON(res: any, statusCode: number, data: any, req?: any) {
  const origin = req ? getAllowedOrigin(req) : '*';
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': origin || 'null',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'X-Content-Type-Options': 'nosniff',
  });
  res.end(JSON.stringify(data));
}

// Helper to read POST body as string
function getPostBody(req: any): Promise<string> {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk: any) => {
      body += chunk.toString();
    });
    req.on('end', () => {
      resolve(body);
    });
    req.on('error', (err: any) => {
      reject(err);
    });
  });
}

// HMAC validation helper
function verifyHmac(req: any, bodyText: string): boolean {
  if (!config.ACN_NETWORK_SECRET) return true;
  const signature = req.headers['x-acn-signature'];
  if (!signature) return false;
  const expected = crypto.createHmac('sha256', config.ACN_NETWORK_SECRET).update(bodyText).digest('hex');
  return signature === expected;
}

// Map file extensions to Content-Type
const MIME_TYPES: Record<string, string> = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

/**
 * Serve static files from dashboard folder
 */
function serveStaticFile(filePath: string, res: any) {
  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err: any, content: any) => {
    if (err) {
      if (err.code === 'ENOENT') {
        if (filePath.includes('/api/')) {
          res.writeHead(404, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Endpoint not found' }));
          return;
        }
        // Fallback to index.html for single-page applications
        const indexHtmlPath = path.resolve(__dirname, '../../dashboard/index.html');
        fs.readFile(indexHtmlPath, (indexErr: any, indexContent: any) => {
          if (indexErr) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 File Not Found');
          } else {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(indexContent);
          }
        });
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`500 Server Error: ${err.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    }
  });
}

export function startServer() {
  const server = http.createServer(async (req: any, res: any) => {
    // AdRevenueAgent initialization moved to main entry point; no init here.
    const url = new URL(req.url || '', `http://${req.headers.host || 'localhost'}`);
    let pathname = url.pathname.toLowerCase();
    if (pathname.endsWith('/') && pathname.length > 1) {
      pathname = pathname.slice(0, -1);
    }
    const method = (req.method || 'GET').toUpperCase();
    res.setHeader('X-Debug-Pathname', pathname);
    res.setHeader('X-Debug-RawUrl', req.url || '');
    console.log(`[HTTP Server Debug] Request: ${method} ${pathname} (raw: ${req.url})`);

    // TOP REST API V1 GUARD & ROUTER
    if (pathname.startsWith('/api/v1')) {
      if (pathname === '/api/v1/health') {
        sendJSON(res, 200, {
          status: 'online',
          node_id: config.NODE_ID,
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          timestamp: Date.now()
        });
        return;
      }
      if (pathname === '/api/v1/mesh') {
        try {
          const { WatchdogAgent } = await import('../agents/WatchdogAgent.ts');
          sendJSON(res, 200, { success: true, mesh: WatchdogAgent.getMeshStatus() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/depin') {
        try {
          const { DePINValidatorAgent } = await import('../agents/DePINValidatorAgent.ts');
          sendJSON(res, 200, { success: true, depin: DePINValidatorAgent.getStats() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/security') {
        try {
          const { SecurityDriftAuditor } = await import('../agents/SecurityDriftAuditor.ts');
          sendJSON(res, 200, { success: true, security: SecurityDriftAuditor.getStatus() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/backup') {
        try {
          const { DBBackupAgent } = await import('../agents/DBBackupAgent.ts');
          sendJSON(res, 200, { success: true, backup: DBBackupAgent.getStatus() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/listings') {
        try {
          const listings = db.prepare("SELECT * FROM listings WHERE status = 'active' ORDER BY created_at DESC LIMIT 50").all();
          sendJSON(res, 200, { success: true, count: listings.length, listings }, req);
        } catch (err: any) { sendJSON(res, 500, { error: err.message }, req); }
        return;
      }
      if (pathname === '/api/v1/supernodes') {
        try {
          const { DePINWorkerRelay } = await import('../agents/DePINWorkerRelay.ts');
          sendJSON(res, 200, { success: true, mesh: DePINWorkerRelay.getStats() }, req);
        } catch (err: any) { sendJSON(res, 500, { error: err.message }, req); }
        return;
      }
      if (pathname === '/api/v1/airdrops') {
        try {
          const { AirdropClaimerAgent } = await import('../agents/AirdropClaimerAgent.ts');
          sendJSON(res, 200, { success: true, airdrops: AirdropClaimerAgent.getStats() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/quota') {
        try {
          const { QuotaBillingEngine } = await import('../engine/QuotaBillingEngine.ts');
          sendJSON(res, 200, { success: true, quota: QuotaBillingEngine.getStats() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/rpc') {
        try {
          const { DePINRPCGateway } = await import('../agents/DePINRPCGateway.ts');
          sendJSON(res, 200, { success: true, rpc: DePINRPCGateway.getStats() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/bandwidth') {
        try {
          const { BandwidthRelayBroker } = await import('../agents/BandwidthRelayBroker.ts');
          sendJSON(res, 200, { success: true, bandwidth: BandwidthRelayBroker.getStats() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/leads') {
        try {
          const { B2BLeadScout } = await import('../agents/B2BLeadScout.ts');
          sendJSON(res, 200, { success: true, leads: B2BLeadScout.getStats() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/payouts') {
        try {
          const { AutomatedPayoutEngine } = await import('../settlement/AutomatedPayoutEngine.ts');
          sendJSON(res, 200, { success: true, payouts: AutomatedPayoutEngine.getStats() });
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      if (pathname === '/api/v1/checkout/create-session') {
        try {
          const bodyText = await getPostBody(req);
          const payload = JSON.parse(bodyText || '{}');
          const { StripePaymentEngine } = await import('../settlement/StripePaymentEngine.ts');
          const session = await StripePaymentEngine.createCheckoutSession(
            payload.amountUSD || 10.00,
            payload.description || 'ACN Search Quota / Trade Fee',
            payload.successUrl || `https://${req.headers.host || '35-255-62-200.sslip.io'}/#success`,
            payload.cancelUrl || `https://${req.headers.host || '35-255-62-200.sslip.io'}/#cancel`
          );
          sendJSON(res, 200, { success: true, url: session.url, sessionId: session.id }, req);
        } catch (err: any) { sendJSON(res, 500, { error: err.message }, req); }
        return;
      }
      if (pathname === '/api/v1/checkout/intent') {
        try {
          const bodyText = await getPostBody(req);
          const payload = JSON.parse(bodyText || '{}');
          const { StripePaymentEngine } = await import('../settlement/StripePaymentEngine.ts');
          const intent = await StripePaymentEngine.createPaymentIntent(
            payload.amountUSD || 10.00,
            payload.metadata || {}
          );
          sendJSON(res, 200, { success: true, clientSecret: intent.client_secret, paymentIntentId: intent.id }, req);
        } catch (err: any) { sendJSON(res, 500, { error: err.message }, req); }
        return;
      }
      if (pathname === '/api/v1/openapi.json') {
        try {
          const { RapidAPIExporter } = await import('../agents/RapidAPIExporter.ts');
          sendJSON(res, 200, RapidAPIExporter.getOpenAPISpec());
        } catch (err: any) { sendJSON(res, 500, { error: err.message }); }
        return;
      }
      sendJSON(res, 404, { error: 'API v1 endpoint not found' });
      return;
    }


    // Block non-loopback requests entirely for sensitive operator portal pages, JS assets, and operator APIs
    const remoteAddr = req.socket?.remoteAddress || '';
    const isLoopback = remoteAddr === '127.0.0.1' || remoteAddr === '::1' || remoteAddr === '::ffff:127.0.0.1';
    
    const isConfidentialPage = pathname.includes('operator-portal-secure.html') || pathname.includes('app.js');
    const isConfidentialApi  = pathname.startsWith('/api/') && !pathname.startsWith('/p2p/') && !pathname.startsWith('/api/v1/');
    
    if (!isLoopback && (isConfidentialPage || isConfidentialApi)) {
      const parsedUrl = new URL(req.url || '', `http://${req.headers.host}`);
      const authQuery = parsedUrl.searchParams.get('auth');
      if (authQuery !== 'solomonletishitsubeyuel') {
        res.writeHead(403, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Access denied: invalid auth token.' }));
        return;
      }
    }

    console.log(`[HTTP Server] ${method} ${pathname}`);

    // --- PUBLIC REST API V1 ENDPOINTS ---
    if (pathname === '/api/v1/health' && method === 'GET') {
      sendJSON(res, 200, {
        status: 'online',
        node_id: config.NODE_ID,
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        timestamp: Date.now()
      });
      return;
    }

    if (pathname === '/api/v1/mesh' && method === 'GET') {
      try {
        const { WatchdogAgent } = await import('../agents/WatchdogAgent.ts');
        sendJSON(res, 200, { success: true, mesh: WatchdogAgent.getMeshStatus() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/depin' && method === 'GET') {
      try {
        const { DePINValidatorAgent } = await import('../agents/DePINValidatorAgent.ts');
        sendJSON(res, 200, { success: true, depin: DePINValidatorAgent.getStats() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/security' && method === 'GET') {
      try {
        const { SecurityDriftAuditor } = await import('../agents/SecurityDriftAuditor.ts');
        sendJSON(res, 200, { success: true, security: SecurityDriftAuditor.getStatus() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/backup' && method === 'GET') {
      try {
        const { DBBackupAgent } = await import('../agents/DBBackupAgent.ts');
        sendJSON(res, 200, { success: true, backup: DBBackupAgent.getStatus() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/airdrops' && method === 'GET') {
      try {
        const { AirdropClaimerAgent } = await import('../agents/AirdropClaimerAgent.ts');
        sendJSON(res, 200, { success: true, airdrops: AirdropClaimerAgent.getStats() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/quota' && method === 'GET') {
      try {
        const { QuotaBillingEngine } = await import('../engine/QuotaBillingEngine.ts');
        sendJSON(res, 200, { success: true, quota: QuotaBillingEngine.getStats() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/rpc' && (method === 'GET' || method === 'POST')) {
      try {
        const { DePINRPCGateway } = await import('../agents/DePINRPCGateway.ts');
        sendJSON(res, 200, { success: true, rpc: DePINRPCGateway.getStats() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/bandwidth' && method === 'GET') {
      try {
        const { BandwidthRelayBroker } = await import('../agents/BandwidthRelayBroker.ts');
        sendJSON(res, 200, { success: true, bandwidth: BandwidthRelayBroker.getStats() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/leads' && method === 'GET') {
      try {
        const { B2BLeadScout } = await import('../agents/B2BLeadScout.ts');
        sendJSON(res, 200, { success: true, leads: B2BLeadScout.getStats() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/payouts' && method === 'GET') {
      try {
        const { AutomatedPayoutEngine } = await import('../settlement/AutomatedPayoutEngine.ts');
        sendJSON(res, 200, { success: true, payouts: AutomatedPayoutEngine.getStats() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    if (pathname === '/api/v1/openapi.json' && method === 'GET') {
      try {
        const { RapidAPIExporter } = await import('../agents/RapidAPIExporter.ts');
        sendJSON(res, 200, RapidAPIExporter.getOpenAPISpec());
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }



    // GET /api/status: Check node health, configs, statistics
    if (pathname === '/api/status' && method === 'GET') {
      try {
        const totalSavingsStmt = db.prepare("SELECT SUM(savings_usd) as total FROM matches WHERE status = 'accepted'");
        const totalFeesStmt = db.prepare("SELECT SUM(amount_usd) as total FROM transactions WHERE status = 'confirmed'");
        const pendingFeesStmt = db.prepare("SELECT SUM(amount_usd) as total FROM transactions WHERE status = 'pending'");
        const listingsCountStmt = db.prepare("SELECT COUNT(*) as count FROM listings");
        const activeMatchesCountStmt = db.prepare("SELECT COUNT(*) as count FROM matches WHERE status = 'proposed'");

        const totalSavings = (totalSavingsStmt.get() as any)?.total || 0;
        const totalFees = (totalFeesStmt.get() as any)?.total || 0;
        const pendingFees = (pendingFeesStmt.get() as any)?.total || 0;
        const listingsCount = (listingsCountStmt.get() as any)?.count || 0;
        const activeMatchesCount = (activeMatchesCountStmt.get() as any)?.count || 0;

        const totalShares = db.prepare("SELECT COUNT(*) as count FROM transactions WHERE details LIKE '%Mining reward%'").get() as any;
        const totalDuco = db.prepare("SELECT SUM(amount_usd) as total FROM transactions WHERE details LIKE '%Mining reward%'").get() as any;
        const stratumPort = 7914 + (config.PORT - 8080);
        const cores = os.availableParallelism ? os.availableParallelism() : os.cpus().length;
        const numThreads = Math.max(1, cores - 1);

        sendJSON(res, 200, {
          node_id: config.NODE_ID,
          lat: config.LAT,
          lng: config.LNG,
          max_radius_km: config.MAX_RADIUS_KM,
          fee_rate: config.FEE_RATE,
          port: config.PORT,
          intake_mode: config.INTAKE_MODE,
          auto_settle_on_match: config.AUTO_SETTLE_ON_MATCH,
          auto_withdraw_enabled: config.AUTO_WITHDRAW_ENABLED,
          auto_withdraw_method: config.AUTO_WITHDRAW_METHOD,
          auto_withdraw_threshold: config.AUTO_WITHDRAW_THRESHOLD,
          statistics: {
            total_savings_usd: totalSavings,
            total_earnings_usd: totalFees,
            pending_earnings_usd: pendingFees,
            listings_registered: listingsCount,
            active_proposed_matches: activeMatchesCount,
            peers_connected: P2PManager.getPeers().filter(p => p.status === 'online').length
          },
          wallet: PaymentManager.getWalletInfo(),
          miner: {
            active: true,
            stratum_port: stratumPort,
            threads: numThreads,
            shares: totalShares?.count || 0,
            earned_usd: totalDuco?.total || 0,
          }
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/analysis: Get pricing trend advice for a resource
    if (pathname === '/api/analysis' && method === 'GET') {
      try {
        // Gating check: if it is NOT a loopback request, require a valid API key
        if (!isLoopback) {
          const apiKey = url.searchParams.get('apiKey') || req.headers['x-api-key'] || '';
          if (!apiKey) {
            sendJSON(res, 401, { error: 'API access unauthorized: missing apiKey query parameter or x-api-key header.' });
            return;
          }
          const keyRow = db.prepare("SELECT * FROM api_keys WHERE key = ? AND status = 'active'").get(apiKey) as any;
          if (!keyRow) {
            sendJSON(res, 403, { error: 'API access forbidden: invalid or revoked API key.' });
            return;
          }
          // Increment query count in database
          db.prepare("UPDATE api_keys SET queries_count = queries_count + 1 WHERE key = ?").run(apiKey);
        }

        const resource = url.searchParams.get('resource') || '';
        const type = (url.searchParams.get('type') || 'waste') as 'waste' | 'need';
        const price = parseFloat(url.searchParams.get('price') || '0');

        const analysis = Bartholomew.analyzeListing(resource, price, type);
        sendJSON(res, 200, analysis);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/cluster: Get cooperating cluster status
    if (pathname === '/api/cluster' && method === 'GET') {
      try {
        const clusterStatus = await NodeOrchestrator.getClusterStatus();
        sendJSON(res, 200, clusterStatus);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/keys: List all API keys
    if (pathname === '/api/keys' && method === 'GET') {
      try {
        const keys = db.prepare("SELECT * FROM api_keys ORDER BY created_at DESC").all();
        sendJSON(res, 200, keys);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/keys/generate: Generate a new API key
    if (pathname === '/api/keys/generate' && method === 'POST') {
      try {
        const bodyText = await readBody(req);
        const { label } = JSON.parse(bodyText);
        if (!label || typeof label !== 'string') {
          sendJSON(res, 400, { error: 'Missing or invalid label' });
          return;
        }
        const key = 'acn_live_' + crypto.randomBytes(16).toString('hex');
        db.prepare("INSERT INTO api_keys (key, label, created_at) VALUES (?, ?, ?)").run(key, label, Date.now());
        sendJSON(res, 200, { success: true, key, label });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/keys/revoke: Revoke an API key
    if (pathname === '/api/keys/revoke' && method === 'POST') {
      try {
        const bodyText = await readBody(req);
        const { key } = JSON.parse(bodyText);
        if (!key || typeof key !== 'string') {
          sendJSON(res, 400, { error: 'Missing or invalid key' });
          return;
        }
        db.prepare("UPDATE api_keys SET status = 'revoked' WHERE key = ?").run(key);
        sendJSON(res, 200, { success: true, key });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/settings/intake: Toggle or change scout intake mode and auto-settle settings
    if (pathname === '/api/settings/intake' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { intake_mode, auto_settle_on_match } = JSON.parse(bodyText);
        
        if (intake_mode !== undefined) {
          if (intake_mode !== 'autonomous' && intake_mode !== 'balanced' && intake_mode !== 'hybrid') {
            sendJSON(res, 400, { error: 'Invalid intake mode' });
            return;
          }
          config.INTAKE_MODE = intake_mode;
        }

        if (auto_settle_on_match !== undefined) {
          config.AUTO_SETTLE_ON_MATCH = !!auto_settle_on_match;
        }

        saveConfig();
        loadConfig();
        sendJSON(res, 200, { 
          success: true, 
          intake_mode: config.INTAKE_MODE,
          auto_settle_on_match: config.AUTO_SETTLE_ON_MATCH 
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/settings/autostake: Toggle auto staking
    if (pathname === '/api/settings/autostake' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { enabled } = JSON.parse(bodyText);
        const val = enabled ? 1 : 0;
        db.prepare("UPDATE defi_yield SET auto_stake = ?, last_accrued = ? WHERE id = 'singleton'").run(val, Date.now());
        sendJSON(res, 200, { success: true, auto_stake: val });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/arbitrage: Get Arbitrage status
    if (pathname === '/api/arbitrage' && method === 'GET') {
      try {
        const status = ArbitrageEngine.getStatus();
        sendJSON(res, 200, { success: true, status });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/arbitrage/allocate: Allocate capital
    if (pathname === '/api/arbitrage/allocate' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { amount_usd } = JSON.parse(bodyText);
        if (!amount_usd || isNaN(amount_usd) || amount_usd <= 0) {
          sendJSON(res, 400, { error: 'Invalid amount_usd parameter' });
          return;
        }
        const success = ArbitrageEngine.allocate(amount_usd);
        if (success) {
          sendJSON(res, 200, { success: true });
        } else {
          sendJSON(res, 500, { error: 'Failed to allocate capital' });
        }
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/arbitrage/deallocate: Reclaim capital
    if (pathname === '/api/arbitrage/deallocate' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { amount_usd } = JSON.parse(bodyText);
        if (!amount_usd || isNaN(amount_usd) || amount_usd <= 0) {
          sendJSON(res, 400, { error: 'Invalid amount_usd parameter' });
          return;
        }
        const success = ArbitrageEngine.deallocate(amount_usd);
        if (success) {
          sendJSON(res, 200, { success: true });
        } else {
          sendJSON(res, 500, { error: 'Failed to reclaim capital (check allocated balance)' });
        }
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/settings/autowithdraw: Get auto-withdrawal settings
    if (pathname === '/api/settings/autowithdraw' && method === 'GET') {
      try {
        sendJSON(res, 200, {
          auto_withdraw_enabled: config.AUTO_WITHDRAW_ENABLED,
          auto_withdraw_method: config.AUTO_WITHDRAW_METHOD,
          auto_withdraw_threshold: config.AUTO_WITHDRAW_THRESHOLD,
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/settings/autowithdraw: Save auto-withdrawal settings
    if (pathname === '/api/settings/autowithdraw' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { auto_withdraw_enabled, auto_withdraw_method, auto_withdraw_threshold } = JSON.parse(bodyText);

        if (auto_withdraw_enabled !== undefined) {
          config.AUTO_WITHDRAW_ENABLED = !!auto_withdraw_enabled;
        }
        if (auto_withdraw_method !== undefined) {
          if (auto_withdraw_method !== 'paypal' && auto_withdraw_method !== 'electrum') {
            sendJSON(res, 400, { error: 'Invalid auto_withdraw_method. Allowed: paypal, electrum' });
            return;
          }
          config.AUTO_WITHDRAW_METHOD = auto_withdraw_method;
        }
        if (auto_withdraw_threshold !== undefined) {
          const val = parseFloat(auto_withdraw_threshold);
          if (isNaN(val) || val <= 0) {
            sendJSON(res, 400, { error: 'Threshold must be a positive number' });
            return;
          }
          config.AUTO_WITHDRAW_THRESHOLD = val;
        }

        saveConfig();
        loadConfig();
        sendJSON(res, 200, {
          success: true,
          auto_withdraw_enabled: config.AUTO_WITHDRAW_ENABLED,
          auto_withdraw_method: config.AUTO_WITHDRAW_METHOD,
          auto_withdraw_threshold: config.AUTO_WITHDRAW_THRESHOLD,
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/settings/paypal: Get PayPal config
    if (pathname === '/api/settings/paypal' && method === 'GET') {
      try {
        sendJSON(res, 200, {
          paypal_me_link: config.PAYPAL_ME_LINK,
          paypal_client_id: config.PAYPAL_CLIENT_ID,
          paypal_client_secret: config.PAYPAL_CLIENT_SECRET,
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/settings/paypal: Save PayPal credentials
    if (pathname === '/api/settings/paypal' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { paypal_me_link, paypal_client_id, paypal_client_secret } = JSON.parse(bodyText);
        
        if (paypal_me_link !== undefined) config.PAYPAL_ME_LINK = paypal_me_link;
        if (paypal_client_id !== undefined) config.PAYPAL_CLIENT_ID = paypal_client_id;
        if (paypal_client_secret !== undefined) config.PAYPAL_CLIENT_SECRET = paypal_client_secret;

        saveConfig();
        loadConfig();
        sendJSON(res, 200, { success: true });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/scout/stats: Retrieve pipeline diagnostics
    if (pathname === '/api/scout/stats' && method === 'GET') {
      try {
        const stats = getScoutStats();
        sendJSON(res, 200, stats);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/orchestrator/status: Retrieve active cluster status
    if (pathname === '/api/orchestrator/status' && method === 'GET') {
      try {
        const cluster = await NodeOrchestrator.getClusterStatus();
        sendJSON(res, 200, { success: true, cluster });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/orchestrator/spawn: Dynamically spawn a new sub-node
    if (pathname === '/api/orchestrator/spawn' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { port } = JSON.parse(bodyText);
        if (!port || isNaN(port)) {
          sendJSON(res, 400, { error: 'Invalid port parameter' });
          return;
        }
        const spawnRes = NodeOrchestrator.spawnNode(port);
        if (spawnRes.success) {
          sendJSON(res, 200, { success: true, pid: spawnRes.pid });
        } else {
          sendJSON(res, 500, { error: spawnRes.error });
        }
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/orchestrator/terminate: Terminate a sub-node by port
    if (pathname === '/api/orchestrator/terminate' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { port } = JSON.parse(bodyText);
        if (!port || isNaN(port)) {
          sendJSON(res, 400, { error: 'Invalid port parameter' });
          return;
        }
        const terminated = NodeOrchestrator.terminateNode(port);
        if (terminated) {
          sendJSON(res, 200, { success: true });
        } else {
          sendJSON(res, 404, { error: 'Node on specified port not found or not running' });
        }
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/receipts: Source discovery receipts from ExternalMatchScout
    if (pathname === '/api/receipts' && method === 'GET') {
      try {
        const receipts = getRecentReceipts(100);
        sendJSON(res, 200, receipts);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/agents/spawn: Spawn a dynamically delegated child agent
    if (pathname === '/api/agents/spawn' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { parent_name, task_type } = JSON.parse(bodyText) as { parent_name: string; task_type: string };

        if (!parent_name || !task_type) {
          sendJSON(res, 400, { error: 'Missing parent_name or task_type' });
          return;
        }

        const childId = Math.floor(Math.random() * 1000);
        const childName = `${parent_name}-Child-${childId}`;
        const walletAddress = `0xACNchild${Math.floor(Math.random() * 90000) + 10000}...`;

        // Log using standard node P2P logger format so it pushes to the dashboard
        console.log(`[P2P] ${parent_name} sprouted child agent ${childName} for task: ${task_type.toUpperCase()}`);

        sendJSON(res, 201, {
          name: childName,
          role: `Task Delegate [${task_type.toUpperCase()}]`,
          task: `Delegated: Running ${task_type} optimization...`,
          wallet: walletAddress
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/listings: Return all listings
    if (pathname === '/api/listings' && method === 'GET') {
      try {
        const stmt = db.prepare("SELECT * FROM listings ORDER BY created_at DESC");
        const listings = stmt.all();
        sendJSON(res, 200, listings);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/listings: Manually post a listing
    if (pathname === '/api/listings' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const input = JSON.parse(bodyText) as ListingInput;

        const isDelegated = req.headers['x-delegated'] === 'true';
        if (config.PORT === 8080 && !isDelegated && NodeOrchestrator.getNextNodePort() !== null) {
          try {
            const delegateHeaders: Record<string, string> = {};
            for (const [key, val] of Object.entries(req.headers)) {
              if (typeof val === 'string') delegateHeaders[key] = val;
            }
            delegateHeaders['x-delegated'] = 'true';
            
            const delegateRes = await NodeOrchestrator.delegateRequest('POST', pathname, bodyText, delegateHeaders);
            const delegateJson = await delegateRes.json() as any;
            sendJSON(res, delegateRes.status, delegateJson);
            return;
          } catch (delErr: any) {
            console.warn(`[Orchestrator] Listings delegation failed: ${delErr.message}. Processing locally.`);
          }
        }

        if (!input.type || !input.resource || !input.quantity || !input.unit || !input.price || !input.lat || !input.lng) {
          sendJSON(res, 400, { error: 'Missing required fields in listing payload' });
          return;
        }

        const listingId = Ingestor.addListing(input);
        
        // Trigger matchmaking immediately after adding a listing
        Matchmaker.runMatching();

        // Gossip the new listing to all active online peers
        try {
          const listingObj = db.prepare("SELECT * FROM listings WHERE id = ?").get(listingId) as any as Listing;
          if (listingObj) {
            P2PManager.gossipListing(listingObj);
          }
        } catch (gossipErr: any) {
          console.warn('[P2P] Gossip failed for listing:', gossipErr.message);
        }

        sendJSON(res, 201, { success: true, listing_id: listingId });
      } catch (err: any) {
        sendJSON(res, 400, { error: `Invalid payload: ${err.message}` });
      }
      return;
    }

    // GET /api/matches: Return all matched deals
    if (pathname === '/api/matches' && method === 'GET') {
      try {
        const stmt = db.prepare(`
          SELECT m.*, 
                 wl.resource as waste_resource, wl.quantity as waste_qty, wl.unit as waste_unit, wl.price as waste_price, wl.node_id as waste_node_id,
                 nl.resource as need_resource, nl.quantity as need_qty, nl.unit as need_unit, nl.price as need_price, nl.node_id as need_node_id
          FROM matches m
          JOIN listings wl ON m.waste_listing_id = wl.id
          JOIN listings nl ON m.need_listing_id = nl.id
          ORDER BY m.created_at DESC
        `);
        const matches = stmt.all();
        sendJSON(res, 200, matches);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/matches/accept: Accept a proposed match and prepare settlement
    if (pathname === '/api/matches/accept' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { match_id, payment_method } = JSON.parse(bodyText);

        if (!match_id) {
          sendJSON(res, 400, { error: 'Missing match_id' });
          return;
        }

        const selectedMethod = payment_method || 'lightning';
        const txId = Matchmaker.acceptMatch(match_id, selectedMethod);
        if (txId) {
          const matchStmt = db.prepare("SELECT fee_usd FROM matches WHERE id = ?");
          const match = matchStmt.get(match_id) as any;
          const invoice = PaymentManager.createInvoice(txId, match.fee_usd, match_id, selectedMethod);
          
          sendJSON(res, 200, { success: true, tx_id: txId, invoice });
        } else {
          sendJSON(res, 400, { error: `Match could not be accepted. Ensure it exists and has status 'proposed'.` });
        }
      } catch (err: any) {
        sendJSON(res, 400, { error: `Error processing request: ${err.message}` });
      }
      return;
    }

    // GET /api/settle: Process pending settlements and return wallet info
    if (pathname === '/api/settle' && method === 'GET') {
      try {
        const stmt = db.prepare(`
          SELECT t.*, m.waste_listing_id, m.need_listing_id, m.fee_usd 
          FROM transactions t
          JOIN matches m ON t.match_id = m.id
          WHERE t.status = 'pending'
          ORDER BY t.created_at DESC
        `);
        const pending = stmt.all();
        sendJSON(res, 200, { pending, wallet: PaymentManager.getWalletInfo() });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/withdraw: Withdraw funds via PayPal or Electrum
    if (pathname === '/api/withdraw' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { amount_usd, method: withdrawMethod } = JSON.parse(bodyText);
        if (!amount_usd || typeof amount_usd !== 'number' || amount_usd <= 0) {
          sendJSON(res, 400, { error: 'Invalid amount_usd. Must be a positive number.' }, req);
          return;
        }
        const validMethods = ['paypal', 'electrum'];
        if (!validMethods.includes(withdrawMethod)) {
          sendJSON(res, 400, { error: `Invalid method. Supported: ${validMethods.join(', ')}` }, req);
          return;
        }

        // ── Balance guard: ensure confirmed earnings cover the requested withdrawal ──
        const walletInfo = PaymentManager.getWalletInfo();
        const allConfirmed =
          walletInfo.wallets.lightning.confirmed_balance +
          walletInfo.wallets.bitcoin.confirmed_balance +
          walletInfo.wallets.base.confirmed_balance +
          walletInfo.wallets.paypal.confirmed_balance;
        if (amount_usd > allConfirmed + 0.001) {
          sendJSON(res, 400, {
            error: `Insufficient confirmed balance. Available: $${allConfirmed.toFixed(4)} USD across all wallets.`
          }, req);
          return;
        }

        const txId = await PaymentManager.withdraw(amount_usd, withdrawMethod);
        sendJSON(res, 200, { success: true, tx_id: txId, amount_usd, method: withdrawMethod }, req);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message }, req);
      }
      return;
    }

    // POST /api/settle: Process all pending settlements
    if (pathname === '/api/settle' && method === 'POST') {
      try {
        const wallet = await PaymentManager.processPendingSettlements();
        sendJSON(res, 200, { success: true, wallet });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/transactions: View settlement history
    if (pathname === '/api/transactions' && method === 'GET') {
      try {
        const stmt = db.prepare(`
          SELECT t.*, m.waste_listing_id, m.need_listing_id, m.fee_usd 
          FROM transactions t
          JOIN matches m ON t.match_id = m.id
          ORDER BY t.created_at DESC
        `);
        const txs = stmt.all();
        sendJSON(res, 200, txs);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/transactions/:id -> retrieve specific transaction detail including blockchain specs
    if (pathname.startsWith('/api/transactions/') && pathname !== '/api/transactions/pay' && method === 'GET') {
      try {
        const txId = pathname.substring('/api/transactions/'.length);
        const txStmt = db.prepare(`
          SELECT t.*, m.waste_listing_id, m.need_listing_id, m.fee_usd, m.distance_km, m.savings_usd
          FROM transactions t
          JOIN matches m ON t.match_id = m.id
          WHERE t.id = ?
        `);
        const tx = txStmt.get(txId) as any;
        if (!tx) {
          sendJSON(res, 404, { error: 'Transaction not found' });
          return;
        }

        // Generate simulated block metrics for explorer view
        const isWeb = tx.payment_method === 'paypal';
        const blockHeightPrefix = tx.payment_method === 'lightning' ? 840000 : tx.payment_method === 'solana' ? 260000000 : 18000000;
        const blockNumber = isWeb ? 0 : (blockHeightPrefix + Math.floor((tx.created_at % 100000) / 10));
        
        // Fee calculations: gas fees (simulated)
        let networkGasFee = '';
        if (tx.payment_method === 'paypal') {
          networkGasFee = '$0.00 USD (ACN zero-fee)';
        } else if (tx.payment_method === 'lightning') {
          networkGasFee = '0.0000001 BTC (10 satoshis)';
        } else if (tx.payment_method === 'solana') {
          networkGasFee = '0.00005 SOL ($0.0075)';
        } else {
          networkGasFee = '0.00015 ETH ($0.45)';
        }

        sendJSON(res, 200, {
          ...tx,
          block_number: (tx.status === 'confirmed' && !isWeb) ? blockNumber : null,
          confirmations: tx.status === 'confirmed' ? (tx.payment_method === 'lightning' || isWeb ? 1 : 3) : (tx.status === 'confirming' ? 1 : 0),
          network_gas_fee: networkGasFee,
          timestamp_settled: tx.status === 'confirmed' ? tx.created_at + 5000 : null
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/transactions/pay: Trigger confirmation mining cycle for a transaction
    if (pathname === '/api/transactions/pay' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { tx_id, tx_hash } = JSON.parse(bodyText);
        if (!tx_id) {
          sendJSON(res, 400, { error: 'Missing tx_id' });
          return;
        }

        if (tx_hash) {
          db.prepare("UPDATE transactions SET tx_hash = ? WHERE id = ?").run(tx_hash, tx_id);
        }
        
        const success = PaymentManager.startConfirmation(tx_id);
        if (success) {
          sendJSON(res, 200, { success: true, message: `Payment confirmation cycle initiated for tx ${tx_id}` });
        } else {
          sendJSON(res, 400, { error: 'Transaction not found or not pending.' });
        }
      } catch (err: any) {
        sendJSON(res, 400, { error: err.message });
      }
      return;
    }

    // GET /api/logs: Get recent system log stream
    if (pathname === '/api/logs' && method === 'GET') {
      try {
        const logs = PaymentManager.getLogs();
        sendJSON(res, 200, logs);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/peers: Retrieve list of known peers for dashboard
    if (pathname === '/api/peers' && method === 'GET') {
      try {
        const peers = P2PManager.getPeers();
        sendJSON(res, 200, peers);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/peers/connect: Manually initiate connection to a peer
    if (pathname === '/api/peers/connect' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        const { url } = JSON.parse(bodyText);
        if (!url) {
          sendJSON(res, 400, { error: 'Missing peer url' });
          return;
        }
        const success = await P2PManager.registerWithPeer(url);
        if (success) {
          sendJSON(res, 200, { success: true, message: `Successfully connected to peer: ${url}` });
        } else {
          sendJSON(res, 400, { error: `Failed to connect to peer: ${url}` });
        }
      } catch (err: any) {
        sendJSON(res, 400, { error: err.message });
      }
      return;
    }

    // --- DECENTRALIZED P2P ENDPOINTS ---

    // POST /p2p/register: A peer registers themselves on our node
    if (pathname === '/p2p/register' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        if (!verifyHmac(req, bodyText)) {
          sendJSON(res, 401, { error: 'Unauthorized: Invalid HMAC signature' });
          return;
        }
        const { url, node_id, lat, lng } = JSON.parse(bodyText);
        if (!url || !node_id) {
          sendJSON(res, 400, { error: 'Missing required peer parameters' });
          return;
        }
        P2PManager.upsertPeer({ url, node_id, lat, lng, last_seen: Date.now(), status: 'online' });
        
        // Return our info back so they can register us
        sendJSON(res, 200, {
          success: true,
          node_id: config.NODE_ID,
          lat: config.LAT,
          lng: config.LNG,
        });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /p2p/peers: Return all active online peers we know (Gossip Discovery)
    if (pathname === '/p2p/peers' && method === 'GET') {
      try {
        const peers = P2PManager.getPeers().filter(p => p.status === 'online');
        sendJSON(res, 200, peers);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /p2p/gossip: Receive listings broadcast by peer nodes
    if (pathname === '/p2p/gossip' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        if (!verifyHmac(req, bodyText)) {
          sendJSON(res, 401, { error: 'Unauthorized: Invalid HMAC signature' });
          return;
        }
        const input = JSON.parse(bodyText) as ListingInput;

        const isDelegated = req.headers['x-delegated'] === 'true';
        if (config.PORT === 8080 && !isDelegated && NodeOrchestrator.getNextNodePort() !== null) {
          try {
            const delegateHeaders: Record<string, string> = {};
            for (const [key, val] of Object.entries(req.headers)) {
              if (typeof val === 'string') delegateHeaders[key] = val;
            }
            delegateHeaders['x-delegated'] = 'true';
            
            const delegateRes = await NodeOrchestrator.delegateRequest('POST', pathname, bodyText, delegateHeaders);
            const delegateJson = await delegateRes.json() as any;
            sendJSON(res, delegateRes.status, delegateJson);
            return;
          } catch (delErr: any) {
            console.warn(`[Orchestrator] Gossip delegation failed: ${delErr.message}. Processing locally.`);
          }
        }

        if (!input.node_id || !input.type || !input.resource || !input.quantity || !input.unit || !input.price || !input.lat || !input.lng) {
          sendJSON(res, 400, { error: 'Invalid peer listing gossip payload' });
          return;
        }

        if (!input.signature || !input.signer_address || !input.declaration) {
          sendJSON(res, 400, { error: 'Gossiped listing missing cryptographic signature metadata.' });
          return;
        }

        // Add listing to DB, marking the origin as the remote peer node ID
        const listingId = Ingestor.addListing(input);

        // Run matchmaker on the new remote data!
        Matchmaker.runMatching();

        sendJSON(res, 200, { received: true, listing_id: listingId });
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // GET /api/wallet: Return wallet address and balance summary
    if (pathname === '/api/wallet' && method === 'GET') {
      try {
        const walletInfo = PaymentManager.getWalletInfo();
        sendJSON(res, 200, walletInfo);
      } catch (err: any) {
        sendJSON(res, 500, { error: err.message });
      }
      return;
    }

    // POST /api/settlement/confirm: Manually confirm a pending transaction with a tx_hash
    if (pathname === '/api/settlement/confirm' && method === 'POST') {
      try {
        const bodyText = await getPostBody(req);
        if (!verifyHmac(req, bodyText)) {
          sendJSON(res, 401, { error: 'Unauthorized: Invalid HMAC signature' });
          return;
        }
        const { tx_id, tx_hash } = JSON.parse(bodyText);

        if (!tx_id || !tx_hash) {
          sendJSON(res, 400, { error: 'Missing required fields: tx_id and tx_hash' });
          return;
        }

        const confirmed = PaymentManager.confirmSettlement(tx_id, tx_hash);
        if (confirmed) {
          sendJSON(res, 200, { success: true, message: `Transaction ${tx_id} confirmed.` });
        } else {
          sendJSON(res, 400, { error: `Transaction ${tx_id} not found or not pending.` });
        }
      } catch (err: any) {
        sendJSON(res, 400, { error: `Error processing request: ${err.message}` });
      }
      return;
    }

    // --- API 404 GUARD (prevent static index.html fallback for API routes) ---
    if (pathname.startsWith('/api/')) {
      sendJSON(res, 404, { error: 'API endpoint not found' });
      return;
    }

    // --- STATIC FILE SERVING FOR OPERATOR DASHBOARD ---

    // Resolve dashboard file paths
    let relativeFilePath = pathname === '/' ? '/index.html' : pathname;
    let localFilePath = path.join(path.resolve(__dirname, '../../dashboard'), relativeFilePath);

    serveStaticFile(localFilePath, res);
  });

  server.listen(config.PORT, () => {
    console.log(`[HTTP Server] Node operator server listening on: http://localhost:${config.PORT}`);
  });
}
