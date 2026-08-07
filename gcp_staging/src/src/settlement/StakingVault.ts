// StakingVault.ts — DeFi Yield Compounding on Idle Treasury Balances
// Simulates Aave/Compound-style yield earning on idle USDC between settlement cycles.

const APY_RATE = 0.065; // 6.5% APY (Aave USDC stable yield)
const SECONDS_PER_YEAR = 365 * 24 * 60 * 60;

interface VaultEntry {
  principal: number;
  stakedAt: number;
  yieldEarned: number;
}

const vault: VaultEntry[] = [];
let totalPrincipal = 0;
let totalYieldEarned = 0;

export class StakingVault {
  private static isRunning = false;

  static start(intervalMs = 10000) {
    if (this.isRunning) return;
    this.isRunning = true;
    console.log(`[StakingVault] DeFi Yield Vault started (${(APY_RATE * 100).toFixed(1)}% APY on idle treasury)...`);

    const cycle = () => {
      this.compoundYield();
      setTimeout(cycle, intervalMs);
    };
    cycle();
  }

  // Stake idle treasury funds into yield vault
  static stake(amountUsd: number) {
    if (amountUsd <= 0) return;
    vault.push({ principal: amountUsd, stakedAt: Date.now(), yieldEarned: 0 });
    totalPrincipal += amountUsd;
    console.log(`[StakingVault] Staked $${amountUsd.toFixed(2)} USDC into yield vault. Total principal: $${totalPrincipal.toFixed(2)}`);
  }

  // Compound yield on all vault entries
  static compoundYield() {
    const now = Date.now();
    let cycleYield = 0;

    for (const entry of vault) {
      const elapsedSeconds = (now - entry.stakedAt) / 1000;
      const yieldRate = APY_RATE / SECONDS_PER_YEAR;
      const yield_ = entry.principal * yieldRate * elapsedSeconds;
      const newYield = yield_ - entry.yieldEarned;
      entry.yieldEarned = yield_;
      cycleYield += newYield;
    }

    if (cycleYield > 0) {
      totalYieldEarned += cycleYield;
      console.log(`[StakingVault] Yield compounded: +$${cycleYield.toFixed(6)} | Total yield earned: $${totalYieldEarned.toFixed(4)}`);
    }
  }

  static getTotalPrincipal(): number { return totalPrincipal; }
  static getTotalYield(): number { return totalYieldEarned; }
  static getEffectiveAPY(): number { return APY_RATE; }

  // Withdraw + yield from vault
  static withdraw(amountUsd: number): { withdrawn: number; yieldReleased: number } {
    let remaining = amountUsd;
    let yieldReleased = 0;

    while (remaining > 0 && vault.length > 0) {
      const entry = vault[0];
      if (entry.principal <= remaining) {
        remaining -= entry.principal;
        yieldReleased += entry.yieldEarned;
        totalPrincipal -= entry.principal;
        vault.shift();
      } else {
        const proportion = remaining / entry.principal;
        yieldReleased += entry.yieldEarned * proportion;
        entry.principal -= remaining;
        entry.yieldEarned *= (1 - proportion);
        totalPrincipal -= remaining;
        remaining = 0;
      }
    }

    console.log(`[StakingVault] Withdrew $${amountUsd.toFixed(2)} + $${yieldReleased.toFixed(4)} yield from vault.`);
    return { withdrawn: amountUsd, yieldReleased };
  }
}
