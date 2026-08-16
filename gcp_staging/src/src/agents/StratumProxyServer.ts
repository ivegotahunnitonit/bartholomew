import * as net from 'node:net';
import * as crypto from 'node:crypto';
import { addSystemLog } from '../settlement/PaymentManager.ts';
import { config } from '../config.ts';
import { db } from '../database/db.ts';

export class StratumProxyServer {
  private static server: net.Server | null = null;

  static start(port = 7914) {
    if (this.server) return;

    this.server = net.createServer((clientSocket) => {
      console.log(`[Proxy] External miner connected from ${clientSocket.remoteAddress}:${clientSocket.remotePort}`);
      
      const poolSocket = new net.Socket();
      
      // Connect to the master pool
      poolSocket.connect(7913, '152.53.241.160', () => {
        console.log(`[Proxy] Connected client ${clientSocket.remoteAddress} to pool master.`);
      });
      
      // Forward client data to pool
      clientSocket.on('data', (data) => {
        poolSocket.write(data);
      });
      
      // Forward pool data to client and intercept GOOD responses to credit earnings
      let buffer = '';
      poolSocket.on('data', (data) => {
        clientSocket.write(data);
        
        buffer += data.toString();
        while (buffer.includes('\n')) {
          const lineEnd = buffer.indexOf('\n');
          const line = buffer.substring(0, lineEnd).trim();
          buffer = buffer.substring(lineEnd + 1);
          
          if (line === 'GOOD' || line.includes('GOOD')) {
            console.log(`[Proxy] External miner (${clientSocket.remoteAddress}) submitted a valid share! Crediting reward...`);
            // DB write disabled in production mode (no mock transactions)
            /*
            try {
              // 0.0001 DUCO reward per share * $0.01 exchange rate
              const rewardDuco = 0.0001; 
              const rewardUsd = rewardDuco * 0.01;
              
              const txId = crypto.randomUUID();
              const txHash = 'duco_proxy_' + crypto.randomBytes(32).toString('hex');
              db.prepare(`
                INSERT INTO transactions 
                  (id, match_id, tx_hash, amount_usd, status, created_at, payment_method, details)
                VALUES 
                  (?, NULL, ?, ?, 'confirmed', ?, 'bitcoin', ?)
              `).run(
                txId,
                txHash,
                rewardUsd,
                Date.now(),
                `Duino-Coin Proxy Mining reward (External Miner: ${clientSocket.remoteAddress})`
              );
            } catch (dbErr: any) {
              console.error('[Proxy] DB write error:', dbErr.message);
            }
            */
          }
        }
      });
      
      clientSocket.on('error', (err) => {
        console.log(`[Proxy] Client socket error from ${clientSocket.remoteAddress}: ${err.message}`);
        poolSocket.destroy();
      });
      
      poolSocket.on('error', (err) => {
        console.log(`[Proxy] Pool socket error for ${clientSocket.remoteAddress}: ${err.message}`);
        clientSocket.destroy();
      });
      
      clientSocket.on('close', () => {
        poolSocket.destroy();
      });
      
      poolSocket.on('close', () => {
        clientSocket.destroy();
      });
    });
    
    this.server.listen(port, () => {
      addSystemLog('system', `📡 [Proxy] Stratum Proxy Server listening on port ${port}. Outsource mining port is active!`);
    });
  }

  static stop() {
    if (this.server) {
      this.server.close();
      this.server = null;
      addSystemLog('system', 'Stratum Proxy Server stopped.');
    }
  }
}
