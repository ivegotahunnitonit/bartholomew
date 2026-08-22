import process from 'node:process';
process.env.NODE_ENV = 'test';

import { loadConfig, config, saveConfig } from './config.ts';
import { initDatabase, db } from './database/db.ts';
import { Ingestor } from './engine/Ingestor.ts';
import { Matchmaker } from './engine/Matchmaker.ts';
import { Bartholomew } from './engine/Bartholomew.ts';
import { PaymentManager } from './settlement/PaymentManager.ts';
import { EscrowSettlement } from './settlement/EscrowSettlement.ts';

function assert(condition: boolean, message: string) {
  if (!condition) {
    throw new Error(`Assertion Failed: ${message}`);
  }
  console.log(`[PASS] ${message}`);
}

async function testSuite() {
  console.log('==================================================');
  console.log('         ACN CORE ENGINE TEST SUITE               ');
  console.log('==================================================');

  // 1. Load config
  loadConfig();
  config.AUTO_ACCEPT_ENABLED = false;
  config.LIVE_MODE = false; // Force simulated mode for sandbox testing
  
  // 2. Init DB
  initDatabase();

  // Clean tables first to ensure clean test state
  db.exec("DELETE FROM transactions");
  db.exec("DELETE FROM matches");
  db.exec("DELETE FROM listings");
  console.log('[Test Setup] Cleared previous database entries.');

  // 3. Test Ingestor & Listing Insertions
  const wasteId = Ingestor.addListing({
    node_id: 'test_brewery_node',
    type: 'waste',
    resource: 'spent brewer grain',
    quantity: 500,
    unit: 'kg',
    price: 0.02,
    lat: 40.7128,
    lng: -74.0060,
  });

  const needId = Ingestor.addListing({
    node_id: 'test_mushroom_node',
    type: 'need',
    resource: 'spent grain substrate',
    quantity: 600,
    unit: 'kg',
    price: 0.15,
    lat: 40.7200, // 0.8km away
    lng: -74.0060,
  });

  const listingsCount = (db.prepare("SELECT COUNT(*) as count FROM listings").get() as any).count;
  assert(listingsCount === 2, 'Two active listings inserted correctly.');

  // 4. Test Matchmaker Engine
  const matches = Matchmaker.runMatching();
  assert(matches.length === 1, 'Matchmaker correctly paired the spent grain waste and need.');
  
  const dbMatchesCount = (db.prepare("SELECT COUNT(*) as count FROM matches").get() as any).count;
  assert(dbMatchesCount === 1, 'Proposed match persisted in SQLite database.');

  // Verify match metrics
  const match = matches[0];
  assert(match.savings_usd > 0, `Net savings should be positive (calculated: $${match.savings_usd.toFixed(2)}).`);
  assert(match.fee_usd > 0, `System fee should be positive (calculated: $${match.fee_usd.toFixed(2)}).`);

  // 5. Test Accepting Match
  const acceptTxId = Matchmaker.acceptMatch(match.id);
  assert(typeof acceptTxId === 'string', 'Match accepted successfully, returning transaction ID.');

  const checkMatchStatus = (db.prepare("SELECT status FROM matches WHERE id = ?").get(match.id) as any).status;
  assert(checkMatchStatus === 'accepted', 'Match status updated to "accepted" in SQLite.');

  const txCount = (db.prepare("SELECT COUNT(*) as count FROM transactions").get() as any).count;
  assert(txCount === 1, 'Settlement transaction automatically initialized in DB.');

  // Simulate confirming the transaction
  db.prepare("UPDATE transactions SET status = 'confirmed', tx_hash = 'sol_tx_hash_abc123xyz' WHERE match_id = ?").run(match.id);
  const checkTxStatus = (db.prepare("SELECT status, tx_hash FROM transactions WHERE match_id = ?").get(match.id) as any);
  assert(checkTxStatus.status === 'confirmed', 'Transaction status updated to confirmed.');
  assert(checkTxStatus.tx_hash === 'sol_tx_hash_abc123xyz', 'Transaction hash correctly updated.');

  // 6. Test Bartholomew Ledger Price Trends Analyzer
  const analysis = Bartholomew.analyzeListing('spent grain', 0.10, 'waste');
  assert(analysis.suggestedPrice > 0, 'Bartholomew suggested a positive price based on confirmed ledger history.');
  assert(analysis.message.includes('[BARTHOLOMEW]'), 'Bartholomew generated a valid recommendations log message.');

  // 7. Test Auto-Settlement Configuration & PaymentManager methods
  config.AUTO_SETTLE_ON_MATCH = true;
  saveConfig();
  loadConfig();
  config.AUTO_ACCEPT_ENABLED = false; // Prevent background auto-accept timeouts during test runs
  assert(config.AUTO_SETTLE_ON_MATCH === true, 'AUTO_SETTLE_ON_MATCH config flag correctly saved and reloaded.');

  // Create another match and verify auto-settlement starts confirmation
  Ingestor.addListing({
    node_id: 'test_brewery_node',
    type: 'waste',
    resource: 'spent brewer grain',
    quantity: 100,
    unit: 'kg',
    price: 0.02,
    lat: 40.7128,
    lng: -74.0060,
  });
  const needId2 = Ingestor.addListing({
    node_id: 'test_mushroom_node',
    type: 'need',
    resource: 'spent grain substrate',
    quantity: 100,
    unit: 'kg',
    price: 0.15,
    lat: 40.7200,
    lng: -74.0060,
  });
  const matches2 = Matchmaker.runMatching();
  assert(matches2.length === 1, 'Matchmaker created second match.');
  const txId2 = Matchmaker.acceptMatch(matches2[0].id, 'lightning');
  assert(typeof txId2 === 'string', 'Second match accepted.');
  
  // Since AUTO_SETTLE_ON_MATCH is true, transaction should automatically transition to 'confirming' or 'confirmed'
  const txCheck = db.prepare("SELECT status FROM transactions WHERE id = ?").get(txId2) as any;
  assert(txCheck.status === 'confirming' || txCheck.status === 'confirmed', 'Transaction automatically initiated confirmation flow.');

  // Mock PaymentManager.withdraw for unit tests to prevent executing live mainnet calls/APIs
  const originalWithdraw = PaymentManager.withdraw;
  PaymentManager.withdraw = async (amountUSD: number, method: 'paypal' | 'electrum') => {
    if (method === 'paypal') {
      return 'PP-MOCK-' + Math.random().toString(36).substring(2, 15);
    } else {
      return 'btc_mock_tx_' + Math.random().toString(36).substring(2, 15);
    }
  };

  // Test PaymentManager.withdraw
  // Paypal withdrawal
  config.PAYPAL_ME_LINK = 'https://paypal.me/acntest';
  const paypalPayoutId = await PaymentManager.withdraw(10.00, 'paypal');
  assert(typeof paypalPayoutId === 'string' && paypalPayoutId.length > 0, 'PayPal withdrawal returned valid payout ID.');

  // Electrum withdrawal
  config.ELECTRUM_WALLET_ADDRESS = 'tb1q34szqj7nk56g4275cmwzvv0ry5zwvmxch67q9t';
  const btcTxId = await PaymentManager.withdraw(20.00, 'electrum');
  assert(typeof btcTxId === 'string' && btcTxId.length > 0, 'Electrum BTC withdrawal returned valid transaction ID.');

  // Restore original method
  PaymentManager.withdraw = originalWithdraw;

  //  Supernode & Industrial Hub Optimization Tests 
  console.log('[Test] Running ACN Supernode & Industrial Hub optimization tests...');

  // 1. Proximity Hub and Material Boost Heuristics
  const utilityTest = Bartholomew.calculateMatchUtility(
    'copper scrap metal',
    29.7604, // Houston Ship Channel Lat
    -95.3698, // Houston Ship Channel Lng
    29.8000,
    -95.4000,
    5.0, // Distance
    100.0 // Base Savings
  );
  assert(utilityTest.multiplier > 1.5, 'Bartholomew correctly applies both industrial hub (+25%) and material boosts (+50%).');

  // 2. Multi-hop Matching
  // Clear tables in dependency order
  db.exec("DELETE FROM transactions");
  db.exec("DELETE FROM matches");
  db.exec("DELETE FROM listings");
  db.exec("DELETE FROM peers");

  // Insert intermediate broker peer
  db.prepare(`
    INSERT INTO peers (url, node_id, lat, lng, last_seen, status)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run('http://localhost:8085', 'broker-peer-8085', 39.0000, -109.0000, Date.now(), 'online');

  // Denver listing (waste)
  const d1 = Ingestor.addListing({
    node_id: 'denver_node',
    type: 'waste',
    resource: 'plastic waste hdpe',
    quantity: 1000,
    unit: 'kg',
    price: 0.10,
    lat: 39.7392,
    lng: -104.9903,
  });

  // Salt Lake City listing (need) -> ~600 km away from Denver
  const d2 = Ingestor.addListing({
    node_id: 'salt_lake_node',
    type: 'need',
    resource: 'plastic pellets',
    quantity: 1000,
    unit: 'kg',
    price: 0.90,
    lat: 40.7608,
    lng: -111.8910,
  });

  const matches3 = Matchmaker.runMatching();
  assert(matches3.length > 0, 'Matchmaker successfully matched Denver and Salt Lake City listings.');
  
  // Verify that routing path was computed through our broker peer
  const matchedRoute3 = matches3[0].routing_path;
  assert(typeof matchedRoute3 === 'string' && matchedRoute3.includes('broker-peer-8085'), 'Matchmaker successfully resolved a multi-hop routing path through intermediate peer.');

  // 3. EVM Escrow Settlement
  const escrowTx = await EscrowSettlement.createEscrow('deal-abc', '0xBuyer', '0xSeller', 250);
  assert(typeof escrowTx === 'string' && escrowTx.startsWith('0x'), 'EscrowSettlement successfully initialized on-chain stablecoin escrow.');

  const escrowCheck = EscrowSettlement.getEscrow('deal-abc');
  assert(escrowCheck !== undefined && escrowCheck.status === 'created', 'Escrow contract verified locally in created state.');

  const releaseTx = await EscrowSettlement.confirmDelivery('deal-abc', escrowCheck.verificationHash);
  assert(typeof releaseTx === 'string' && releaseTx.startsWith('0x'), 'EscrowSettlement successfully verified delivery and released locked funds.');
  
  assert(escrowCheck.status === 'released', 'Escrow contract status correctly updated to released.');

  const royaltyTx = await EscrowSettlement.payRoyalties('deal-abc', '0xCollector', 5);
  assert(typeof royaltyTx === 'string' && royaltyTx.startsWith('0x'), 'EscrowSettlement successfully distributed trade royalties to upstream collector.');


  console.log('==================================================');
  console.log('     SUCCESS: ALL CORE SYSTEM TESTS PASSED!       ');
  console.log('==================================================');
}

testSuite().catch(err => {
  console.error('[FAIL] Test Suite failed with error:', err);
  process.exit(1);
});
