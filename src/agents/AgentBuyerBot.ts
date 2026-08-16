import { Ingestor } from '../engine/Ingestor.ts';
import { Matchmaker } from '../engine/Matchmaker.ts';
import { config } from '../config.ts';

export class AgentBuyerBot {
  private static isRunning = false;

  static start(intervalMs = 100) {
    if (this.isRunning) return;
    this.isRunning = true;
    console.log('[AgentBuyerBot] Autonomous High-Frequency AI Buyer Demand Engine started (100ms HFT Cycle)...');

    const loop = () => {
      this.generateBuyerDemand();
      setTimeout(loop, intervalMs);
    };
    loop();
  }


  static generateBuyerDemand() {
    const buyerNeeds = [
      { resource: 'plastic pellets', quantity: 25000, unit: 'kg', price: 0.95, node: 'salt_lake_buyer' },
      { resource: 'steel', quantity: 15000, unit: 'kg', price: 1.20, node: 'detroit_buyer' },
      { resource: 'chemicals', quantity: 10000, unit: 'l', price: 2.80, node: 'dallas_buyer' },
      { resource: 'spent grain', quantity: 1000, unit: 'kg', price: 0.25, node: 'farm_buyer' },
      { resource: 'H100 GPU compute slot', quantity: 50, unit: 'hours', price: 3.00, node: 'ai_lab_buyer' },
    ];

    try {
      const selected = buyerNeeds[Math.floor(Math.random() * buyerNeeds.length)];
      const listingId = Ingestor.addListing({
        node_id: selected.node,
        type: 'need',
        resource: selected.resource,
        quantity: selected.quantity,
        unit: selected.unit,
        price: selected.price,
        lat: config.LAT || 39.7392,
        lng: config.LNG || -104.9903,
      });

      console.log(`[AgentBuyerBot] Ingested active buyer demand: need - ${selected.resource} (${selected.quantity} ${selected.unit} @ $${selected.price}/${selected.unit}) => ${listingId}`);

      // Instant Matchmaker Execution
      const matches = Matchmaker.runMatching();
      if (matches.length > 0) {
        console.log(`[AgentBuyerBot] Successfully matched ${matches.length} buyer order(s)!`);
      }
    } catch (err: any) {
      console.warn('[AgentBuyerBot] Demand generation cycle:', err.message);
    }
  }
}
