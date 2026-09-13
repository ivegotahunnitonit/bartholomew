import { loadConfig, config } from './config.ts';
import { initDatabase } from './database/db.ts';
import { Ingestor } from './engine/Ingestor.ts';
import { Matchmaker } from './engine/Matchmaker.ts';
import { startExternalMatchScout } from './engine/ExternalMatchScout.ts';
import { startServer } from './network/Server.ts';
import { P2PManager } from './network/P2PManager.ts';
import { startSettlementEngine } from './settlement/PaymentManager.ts';
import { AdRevenueAgent } from './agents/AdRevenueAgent.ts';
import { CpuMinerAgent } from './agents/CpuMinerAgent.ts';
import { StratumProxyServer } from './agents/StratumProxyServer.ts';
import { NodeOrchestrator } from './network/NodeOrchestrator.ts';
import { ArbitrageEngine } from './settlement/ArbitrageEngine.ts';
import { AgentBuyerBot } from './agents/AgentBuyerBot.ts';
import { DynamicFeeEngine } from './engine/DynamicFeeEngine.ts';
import { MonitorAgent } from './agents/MonitorAgent.ts';
import { ComputeRelayBroker } from './agents/ComputeRelayBroker.ts';
import { AlgoraBountyScanner } from './agents/AlgoraBountyScanner.ts';
import { RealTrafficEngine } from './agents/RealTrafficEngine.ts';
import { TrafficRouter } from './agents/TrafficRouter.ts';
import { PublicAPIsSubmitter } from './agents/PublicAPIsSubmitter.ts';
import { BountyClaimer } from './agents/BountyClaimer.ts';
import { WatchdogAgent } from './agents/WatchdogAgent.ts';
import { DBBackupAgent } from './agents/DBBackupAgent.ts';
import { DePINValidatorAgent } from './agents/DePINValidatorAgent.ts';
import { SecurityDriftAuditor } from './agents/SecurityDriftAuditor.ts';
import { AirdropClaimerAgent } from './agents/AirdropClaimerAgent.ts';
import { QuotaBillingEngine } from './engine/QuotaBillingEngine.ts';
import { DePINRPCGateway } from './agents/DePINRPCGateway.ts';
import { BandwidthRelayBroker } from './agents/BandwidthRelayBroker.ts';
import { B2BLeadScout } from './agents/B2BLeadScout.ts';
import { AutomatedPayoutEngine } from './settlement/AutomatedPayoutEngine.ts';


async function main() {
  console.log('==================================================');
  console.log('   BARTHOLOMEW — Autonomous Circularity Network   ');
  console.log('==================================================');

  // 1. Load configuration and generate Node identity
  loadConfig();

  // 2. Initialize SQLite Database Sync
  initDatabase();

  // 3. Start HTTP Server & Operator Dashboard API immediately
  startServer();

  // 4. Seed node capabilities and high-volume commercial listings
  Ingestor.seedCapabilities(config.LAT, config.LNG);
  Ingestor.seedCommercialListings(config.LAT, config.LNG);
  // 5. Run initial matchmaking cycle
  Matchmaker.runMatching();

  // 6. Initialize P2P Network Bootstrap connections in background
  P2PManager.bootstrap().catch(p2pErr => console.warn('[P2P] Bootstrapping failed:', p2pErr.message));

  // Start cooperating sub-node cluster if Supernode mode is enabled
  if (config.SUPER_NODE_MODE) {
    // NodeOrchestrator.startCluster(4); // Disabled to prevent VM memory exhaustion
  }

  // 7. Revenue Engines: Settlement, Buyers, Dynamic Fees, Monitoring, Compute
  startSettlementEngine();
  // AgentBuyerBot disabled — was generating phantom demand. Real buyers only.
  DynamicFeeEngine.start(5000);

  MonitorAgent.start(30000);
  ComputeRelayBroker.start(500);
  // StakingVault disabled — no verified treasury balance yet to compound
  AlgoraBountyScanner.start(120000);
  BountyClaimer.start(15000);
  RealTrafficEngine.start(30000);
  TrafficRouter.start();
  WatchdogAgent.start(10000);     // Monitor all 5 nodes every 10s
  DBBackupAgent.start();           // Auto-backup DB every 15min
  DePINValidatorAgent.start(20000); // DePIN Physical Validator every 20s
  SecurityDriftAuditor.start(30000); // Security & Config Auditor every 30s
  AirdropClaimerAgent.start(45000);  // Node Airdrop & Epoch Payout Claimer every 45s
  DePINRPCGateway.start(15000);      // RPC Relay for Ankr & POKT Network every 15s
  BandwidthRelayBroker.start(25000); // Rent bandwidth to Grass & Mysterium every 25s
  B2BLeadScout.start(35000);         // B2B Lead Hunter every 35s
  AutomatedPayoutEngine.start(30000); // Automated Payout Engine every 30s


  // Submit ACN to public API directories on boot (uses GITHUB_TOKEN if available)
  PublicAPIsSubmitter.submitAll(process.env.GITHUB_TOKEN).catch(() => {});





  // CpuMinerAgent.start(); // Disabled by operator (unprofitable)
  // const stratumPort = 7914 + (config.PORT - 8080);
  // StratumProxyServer.start(stratumPort); // Disabled by operator (unprofitable)
  // AdRevenueAgent.start(); // Archived by operator request
  // ArbitrageEngine.start(); // Archived by operator request (no mock yields)

  // 8. Ultra-Fast High-Frequency Trading (HFT) Loop (Sub-1ms Microtask Reaction Speed)
  function runUltraFastHftLoop() {
    try {
      Matchmaker.runMatching();
    } catch (err) {
      console.error('[Ultra-Fast HFT] Error in event loop tick:', err);
    }
    // Execute on immediate process tick (<1ms V8 event loop latency)
    setImmediate(runUltraFastHftLoop);
  }
  runUltraFastHftLoop();



  // 9. Schedule continuous P2P peer checks and discovery (every 60 seconds)
  setInterval(() => {
    P2PManager.pingPeers().catch(err => {
      console.error('[Background P2P] Peer checks error:', err);
    });
  }, 60000);

  // 10. Start External Match Scout (polls peers + public feeds every 45s)
  startExternalMatchScout(45_000);

  console.log('[Bartholomew] Node is active and running autonomously.');

  // 11. Graceful exit process hooks to terminate all cluster sub-nodes
  process.on('SIGINT', () => {
    console.log('\n[System] SIGINT received. Shutting down orchestrator cluster...');
    NodeOrchestrator.terminateAll();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.log('\n[System] SIGTERM received. Shutting down orchestrator cluster...');
    NodeOrchestrator.terminateAll();
    process.exit(0);
  });
}

main().catch(err => {
  console.error('[Fatal System Error]:', err);
});
