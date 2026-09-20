/**
 * PriceFeedManager.ts
 * Real-time Market Price & Currency Exchange Rate Engine for ACN.
 * 
 * Fetches live market crypto prices and FX rates with local caching & safe fallback defaults.
 */

export interface MarketPrices {
  usd: number;
  eur: number; // EUR per USD
  gbp: number; // GBP per USD
  jpy: number; // JPY per USD
  sgd: number; // SGD per USD
  btc: number; // BTC in USD
  eth: number; // ETH in USD
  sol: number; // SOL in USD
  akt: number; // AKT in USD
  rndr: number; // RNDR in USD
  lastUpdated: number;
}

let cachedPrices: MarketPrices = {
  usd: 1.0,
  eur: 0.922,
  gbp: 0.789,
  jpy: 157.4,
  sgd: 1.351,
  btc: 105340,
  eth: 3821,
  sol: 195.4,
  akt: 4.18,
  rndr: 7.52,
  lastUpdated: 0,
};

const CACHE_TTL_MS = 60_000; // 1 minute cache

export class PriceFeedManager {
  static async getPrices(): Promise<MarketPrices> {
    const now = Date.now();
    if (now - cachedPrices.lastUpdated < CACHE_TTL_MS) {
      return cachedPrices;
    }

    try {
      // Fetch live crypto prices from CoinCap / CoinGecko public APIs
      const cryptoRes = await fetch('https://api.coincap.io/v2/assets?ids=bitcoin,ethereum,solana,akash-network,render-token', {
        headers: { 'Accept': 'application/json' }
      });

      if (cryptoRes.ok) {
        const json = await cryptoRes.json() as any;
        if (json && Array.isArray(json.data)) {
          for (const item of json.data) {
            const price = parseFloat(item.priceUsd);
            if (price > 0) {
              if (item.id === 'bitcoin') cachedPrices.btc = Math.round(price);
              if (item.id === 'ethereum') cachedPrices.eth = Math.round(price);
              if (item.id === 'solana') cachedPrices.sol = parseFloat(price.toFixed(2));
              if (item.id === 'akash-network') cachedPrices.akt = parseFloat(price.toFixed(2));
              if (item.id === 'render-token') cachedPrices.rndr = parseFloat(price.toFixed(2));
            }
          }
        }
      }
    } catch (e) {
      // Keep cached defaults on network error
    }

    try {
      // Fetch live FX rates
      const fxRes = await fetch('https://open.er-api.com/v6/latest/USD');
      if (fxRes.ok) {
        const fxJson = await fxRes.json() as any;
        if (fxJson && fxJson.rates) {
          if (fxJson.rates.EUR) cachedPrices.eur = parseFloat(fxJson.rates.EUR.toFixed(3));
          if (fxJson.rates.GBP) cachedPrices.gbp = parseFloat(fxJson.rates.GBP.toFixed(3));
          if (fxJson.rates.JPY) cachedPrices.jpy = parseFloat(fxJson.rates.JPY.toFixed(1));
          if (fxJson.rates.SGD) cachedPrices.sgd = parseFloat(fxJson.rates.SGD.toFixed(3));
        }
      }
    } catch (e) {
      // Keep cached defaults on network error
    }

    cachedPrices.lastUpdated = now;
    return cachedPrices;
  }
}
