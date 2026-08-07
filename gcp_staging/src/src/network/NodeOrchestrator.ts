import { spawn } from 'node:child_process';
import * as path from 'node:path';
import * as fs from 'node:fs';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { config } from '../config.ts';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface ManagedNode {
  pid: number;
  port: number;
  stratumPort: number;
  nodeId: string;
  status: 'running' | 'stopped' | 'error';
  shares: number;
  earnedUsd: number;
  uptime: number; // in seconds
  startTime: number;
  peersCount?: number;
  listingsCount?: number;
  matchesCount?: number;
}

export class NodeOrchestrator {
  private static subNodes: Map<number, {
    process: any;
    port: number;
    startTime: number;
    nodeId: string;
  }> = new Map();

  private static clusterPorts: number[] = [];
  private static rrIndex = 0;

  /**
   * Spawns a cluster of cooperating nodes starting from config.PORT + 1
   */
  static startCluster(size: number) {
    console.log(`[Orchestrator] Starting ACN Supernode Cluster of size ${size}...`);
    const mainPort = config.PORT;
    this.clusterPorts = [];

    // Size includes the main node, so we spawn size - 1 sub-nodes
    for (let i = 1; i < size; i++) {
      const port = mainPort + i;
      const res = this.spawnNode(port);
      if (res.success) {
        this.clusterPorts.push(port);
      } else {
        console.error(`[Orchestrator] Failed to spawn cluster node on port ${port}:`, res.error);
      }
    }
  }

  /**
   * Returns the next sub-node port in the cluster for load balancing
   */
  static getNextNodePort(): number | null {
    if (this.clusterPorts.length === 0) return null;
    const activePorts = Array.from(this.subNodes.keys());
    if (activePorts.length === 0) return null;

    // Choose round-robin from currently running sub-nodes
    const port = activePorts[this.rrIndex % activePorts.length];
    this.rrIndex++;
    return port;
  }

  /**
   * Delegate a request to a cluster sub-node
   */
  static async delegateRequest(method: string, pathname: string, bodyText: string, headers: Record<string, string>): Promise<Response> {
    const targetPort = this.getNextNodePort();
    if (!targetPort) {
      throw new Error('No active sub-nodes in the cluster to delegate request.');
    }

    const url = `http://localhost:${targetPort}${pathname}`;
    console.log(`[Orchestrator] Load Balancing: Delegating ${method} ${pathname} to cluster node on port ${targetPort}`);

    return fetch(url, {
      method,
      headers: {
        ...headers,
        'host': `localhost:${targetPort}`
      },
      body: method !== 'GET' && method !== 'HEAD' ? bodyText : undefined,
    });
  }

  static spawnNode(port: number): { success: boolean; pid?: number; error?: string } {
    if (this.subNodes.has(port)) {
      return { success: false, error: `Node on port ${port} is already running.` };
    }

    const dataDir = path.resolve(`./data_node_${port}`);
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    const logFile = path.join(dataDir, 'node.log');
    const logStream = fs.createWriteStream(logFile, { flags: 'a' });

    const nodeId = `node-sub-${port}-${Math.random().toString(36).substring(2, 9)}`;

    try {
      // Use agy-node script in %APPDATA%/Antigravity/bin/agy-node.cmd if it exists
      const appData = process.env.APPDATA || (process.platform === 'darwin' ? process.env.HOME + '/Library/Application Support' : process.env.HOME + '/.config');
      const agyPath = path.join(appData, 'Antigravity/bin/agy-node.cmd');

      const cmd = fs.existsSync(agyPath) ? agyPath : 'node';
      const args = fs.existsSync(agyPath)
        ? ['--experimental-strip-types', path.resolve('src/index.ts')]
        : ['--experimental-strip-types', 'src/index.ts'];

      const child = spawn(
        cmd,
        args,
        {
          env: {
            ...process.env,
            PORT: port.toString(),
            ACN_DATA_DIR: dataDir,
            NODE_ID: nodeId,
            BOOTSTRAP_PEERS: `http://localhost:${config.PORT}`,
          },
          stdio: ['ignore', 'pipe', 'pipe'],
          shell: true
        }
      );

      child.stdout.pipe(logStream);
      child.stderr.pipe(logStream);

      this.subNodes.set(port, {
        process: child,
        port,
        startTime: Date.now(),
        nodeId
      });

      child.on('close', (code) => {
        console.log(`[Orchestrator] Sub-node on port ${port} exited with code ${code}`);
        this.subNodes.delete(port);

        // Auto crash recovery: Respawn if exited unexpectedly
        if (code !== 0 && code !== null) {
          console.warn(`[Orchestrator] Crash detected on node ${port}. Restarting node...`);
          setTimeout(() => this.spawnNode(port), 2000);
        }
      });

      return { success: true, pid: child.pid };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  }

  static terminateNode(port: number): boolean {
    const node = this.subNodes.get(port);
    if (!node) return false;

    // Use taskkill on Windows to ensure child and its descendants are terminated
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', node.process.pid.toString(), '/f', '/t']);
    } else {
      node.process.kill('SIGTERM');
    }
    this.subNodes.delete(node.port);
    return true;
  }

  static async getClusterStatus(): Promise<ManagedNode[]> {
    const list: ManagedNode[] = [];

    for (const [port, node] of this.subNodes.entries()) {
      let shares = 0;
      let earnedUsd = 0;
      let status: 'running' | 'stopped' | 'error' = 'running';
      let peersCount = 0;
      let listingsCount = 0;
      let matchesCount = 0;

      try {
        const res = await fetch(`http://localhost:${port}/api/status`);
        if (res.ok) {
          const data = await res.json();
          shares = data.miner?.shares || 0;
          earnedUsd = data.miner?.earned_usd || 0;
          peersCount = data.statistics?.peers_connected || 0;
          listingsCount = data.statistics?.listings_registered || 0;
          matchesCount = data.statistics?.active_proposed_matches || 0;
        } else {
          status = 'error';
        }
      } catch (err) {
        status = 'error';
      }

      list.push({
        pid: node.process.pid,
        port: node.port,
        stratumPort: 7914 + (port - 8080),
        nodeId: node.nodeId,
        status,
        shares,
        earnedUsd,
        startTime: node.startTime,
        uptime: Math.floor((Date.now() - node.startTime) / 1000),
        peersCount,
        listingsCount,
        matchesCount
      });
    }

    return list;
  }

  static terminateAll() {
    console.log(`[Orchestrator] Terminating all ${this.subNodes.size} sub-nodes...`);
    for (const port of Array.from(this.subNodes.keys())) {
      this.terminateNode(port);
    }
  }
}
