import { ethers } from 'ethers';
import * as crypto from 'node:crypto';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workspaceRoot = path.join(__dirname, '..');

// Base RPC provider
const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');

// USDC contract address on Base
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const USDC_ABI = [
  'function balanceOf(address account) external view returns (uint256)',
  'function decimals() external view returns (uint8)'
];

function getDerivedAddress(nodeId: string): { address: string; privateKey: string } {
  const seed = crypto.createHash('sha256').update(nodeId + '-acn-signing-seed').digest('hex');
  const privateKey = '0x' + seed;
  const wallet = new ethers.Wallet(privateKey);
  return { address: wallet.address, privateKey };
}

async function checkAddress(name: string, address: string) {
  try {
    const ethBalanceWei = await provider.getBalance(address);
    const ethBalance = ethers.formatEther(ethBalanceWei);

    const usdcContract = new ethers.Contract(USDC_ADDRESS, USDC_ABI, provider);
    let usdcBalance = '0.00';
    try {
      const balanceVal = await usdcContract.balanceOf(address);
      const decimals = await usdcContract.decimals();
      usdcBalance = ethers.formatUnits(balanceVal, decimals);
    } catch (e) {
      // ignore
    }

    console.log(`${name}: Address: ${address}`);
    console.log(`  ETH Balance: ${ethBalance} ETH`);
    console.log(`  USDC Balance: ${usdcBalance} USDC`);
  } catch (err: any) {
    console.error(`  Failed to check ${name}: ${err.message}`);
  }
}

async function run() {
  console.log('Checking main node...');
  const mainDerived = getDerivedAddress('node-a-unique-id');
  await checkAddress('Main Node (derived)', mainDerived.address);

  // Scan sub-node directories to find their node IDs
  if (fs.existsSync(workspaceRoot)) {
    const files = fs.readdirSync(workspaceRoot);
    for (const file of files) {
      if (file.startsWith('data_node_')) {
        const port = file.replace('data_node_', '');
        const logFile = path.join(workspaceRoot, file, 'node.log');
        let nodeId = '';
        if (fs.existsSync(logFile)) {
          const logs = fs.readFileSync(logFile, 'utf8');
          const match = logs.match(/node-sub-[0-9]+-[a-z0-9]+/);
          if (match) {
            nodeId = match[0];
          }
        }
        if (nodeId) {
          const subDerived = getDerivedAddress(nodeId);
          await checkAddress(`Sub-node ${port} (${nodeId})`, subDerived.address);
        } else {
          console.log(`Sub-node ${port}: Node ID not found in logs.`);
        }
      }
    }
  }
}

run();
