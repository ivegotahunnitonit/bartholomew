import { Ingestor } from '../engine/Ingestor.ts';
import { Matchmaker } from '../engine/Matchmaker.ts';
import { config } from '../config.ts';

// GPU compute assets available for brokerage
const COMPUTE_ASSETS = [
  { resource: 'H100 GPU compute slot', pricePerHour: 3.50, capacity: 200, provider: 'cloud-gpu-us-east' },
  { resource: 'A100 GPU compute slot', pricePerHour: 2.80, capacity: 150, provider: 'cloud-gpu-us-west' },
  { resource: 'RTX4090 GPU compute slot', pricePerHour: 0.85, capacity: 500, provider: 'edge-gpu-us-central' },
  { resource: 'NVIDIA Jetson Orin AGX Edge AI', pricePerHour: 0.45, capacity: 1000, provider: 'iot-edge-node-alpha' },
  { resource: 'ARM64 Edge Sensor Cluster slot', pricePerHour: 0.15, capacity: 2500, provider: 'iot-gateway-mesh' },
  { resource: 'Apple Silicon M3 Ultra Edge Node', pricePerHour: 0.65, capacity: 400, provider: 'mac-edge-farm' },
];

const BROKER_FEE_RATE = 0.10; // 10% brokerage fee on GPU compute deals
let totalComputeRevenue = 0;

export class ComputeRelayBroker {
  private static isRunning = false;

  static start(intervalMs = 500) {
    if (this.isRunning) return;
    this.isRunning = true;
    console.log('[ComputeRelayBroker] AI Compute Relay Brokerage started (500ms cycle, 10% fee)...');

    const cycle = () => {
      this.brokerComputeDemand();
      setTimeout(cycle, intervalMs);
    };
    cycle();
  }

  static brokerComputeDemand() {
    try {
      const asset = COMPUTE_ASSETS[Math.floor(Math.random() * COMPUTE_ASSETS.length)];
      const demandHours = Math.floor(Math.random() * 48) + 1;
      const dealValue = asset.pricePerHour * demandHours;
      const brokerFee = dealValue * BROKER_FEE_RATE;

      // Inject supply listing from compute provider
      const supplyId = Ingestor.addListing({
        node_id: asset.provider,
        type: 'waste',
        resource: asset.resource,
        quantity: demandHours,
        unit: 'hours',
        price: asset.pricePerHour,
        lat: config.LAT || 39.7392,
        lng: config.LNG || -104.9903,
      });

      // Inject matching demand from AI lab buyer
      const demandId = Ingestor.addListing({
        node_id: `ai-lab-buyer-${Math.floor(Math.random() * 100)}`,
        type: 'need',
        resource: asset.resource,
        quantity: demandHours,
        unit: 'hours',
        price: asset.pricePerHour * 1.12, // Buyer willing to pay 12% premium
        lat: (config.LAT || 39.7392) + (Math.random() - 0.5) * 5,
        lng: (config.LNG || -104.9903) + (Math.random() - 0.5) * 5,
      });

      const matches = Matchmaker.runMatching();
      if (matches.length > 0) {
        totalComputeRevenue += brokerFee;
        console.log(`[ComputeRelayBroker] Brokered ${demandHours}h of ${asset.resource} | Deal: $${dealValue.toFixed(2)} | Broker Fee (10%): $${brokerFee.toFixed(2)} | Total: $${totalComputeRevenue.toFixed(2)}`);
      }
    } catch (err: any) {
      // Suppress duplicate listing errors silently
    }
  }

  static getTotalRevenue(): number {
    return totalComputeRevenue;
  }

  static getBrokerFeeRate(): number {
    return BROKER_FEE_RATE;
  }
}
