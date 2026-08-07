// testPayment.js
// Run this script from the project root to verify PayPal and Bitcoin withdrawals.
// Ensure you have run `npm install` first.

import { PaymentManager } from './src/settlement/PaymentManager.js';

async function runTests() {
  try {
    console.log('Attempting PayPal withdrawal of $1...');
    const ppResult = await PaymentManager.withdraw(1, 'paypal');
    console.log('PayPal result:', ppResult);
  } catch (e) {
    console.error('PayPal withdrawal error:', e);
  }

  try {
    console.log('Attempting Bitcoin withdrawal of $1...');
    const btcResult = await PaymentManager.withdraw(1, 'bitcoin');
    console.log('Bitcoin result:', btcResult);
  } catch (e) {
    console.error('Bitcoin withdrawal error:', e);
  }
}

runTests();
