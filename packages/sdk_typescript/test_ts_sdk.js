const { BartholomewGuard } = require('./dist/index.js');

async function testTsSdk() {
  console.log('='.repeat(80));
  console.log('TESTING BARTHOLOMEW TYPESCRIPT / NODE.JS SDK');
  console.log('='.repeat(80) + '\n');

  const guard = new BartholomewGuard({ maxSpendUsd: 500.0 });

  // 1. Safe Read Test
  const safePayload = { query: 'SELECT * FROM users WHERE active = true;' };
  const safeRes = guard.evaluateLocal('DB_READ', safePayload);
  console.log('[1] Safe Read Test:', safeRes.verdict, `(${safeRes.latency_us} µs)`);
  if (safeRes.verdict !== 'ALLOW') throw new Error('Safe query was blocked!');

  // 2. Destructive SQL Test
  const attackPayload = { query: 'DROP TABLE credentials; SELECT 1;' };
  const atkRes = guard.evaluateLocal('DB_MUTATION', attackPayload);
  console.log('[2] Destructive SQL Interception:', atkRes.verdict, `(${atkRes.reason}) in ${atkRes.latency_us} µs`);
  if (atkRes.verdict !== 'DENY') throw new Error('Attack query was not blocked!');

  // 3. Spend Cap Test
  const spendAttack = { action: 'WIRE_TRANSFER', amount_usd: 15000.0 };
  const spendRes = guard.evaluateLocal('FINANCIAL_TX', spendAttack);
  console.log('[3] Spend Cap Interception:', spendRes.verdict, `(${spendRes.reason}) in ${spendRes.latency_us} µs`);
  if (spendRes.verdict !== 'DENY') throw new Error('Spend escalation was not blocked!');

  console.log('\n' + '='.repeat(80));
  console.log('TYPESCRIPT / NODE.JS SDK TESTS PASSED 100% CLEAN!');
  console.log('='.repeat(80));
}

testTsSdk().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
