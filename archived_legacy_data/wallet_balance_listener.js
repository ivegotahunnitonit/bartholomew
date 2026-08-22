import fs from 'fs';

const BASE_ADDRESS = '0xaD38221a686318aB1049fa5D60fA5b15DBB73ba4';
const USDC_CONTRACT = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';

let lastUsdcBalance = -1;

async function checkOnChainBalance() {
  try {
    const res = await fetch('https://mainnet.base.org', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'eth_call',
        params: [{ to: USDC_CONTRACT, data: '0x70a08231000000000000000000000000' + BASE_ADDRESS.replace('0x', '') }, 'latest']
      })
    });
    const data = await res.json();
    const hex = data.result || '0x0';
    const usdc = Number(BigInt(hex)) / 1e6;

    if (lastUsdcBalance !== -1 && usdc > lastUsdcBalance) {
      const diff = usdc - lastUsdcBalance;
      console.log(`\n  INCOMING PAYOUT DETECTED ON-CHAIN! Received +${diff.toFixed(2)} USDC! Total: ${usdc.toFixed(2)} USDC\n`);
      fs.writeFileSync('PAYOUT_ALERT.json', JSON.stringify({
        timestamp: new Date().toISOString(),
        amount_received_usdc: diff,
        total_balance_usdc: usdc,
        wallet: BASE_ADDRESS
      }, null, 2));
    }

    lastUsdcBalance = usdc;
    console.log(`[Base On-Chain Monitor @ ${new Date().toLocaleTimeString()}] Live USDC Balance: $${usdc.toFixed(2)} USD (Wallet: ${BASE_ADDRESS})`);
  } catch (err) {
    console.error('[On-Chain Monitor Error]:', err.message);
  }
}

console.log(' BASE USDC ON-CHAIN BALANCE LISTENER ACTIVE — MONITORING 0xaD38221a686318aB1049fa5D60fA5b15DBB73ba4 24/7');
checkOnChainBalance();
setInterval(checkOnChainBalance, 10000);
