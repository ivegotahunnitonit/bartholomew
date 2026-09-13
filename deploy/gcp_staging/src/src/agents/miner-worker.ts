import { parentPort, workerData } from 'node:worker_threads';
import * as net from 'node:net';
import * as crypto from 'node:crypto';

if (!parentPort) {
  process.exit(1);
}

const { workerId, poolIp, poolPort, username } = workerData;

function log(msg: string) {
  parentPort?.postMessage({ type: 'log', message: `[Worker #${workerId}] ${msg}` });
}

function solve(lastHash: string, expectedHash: string, difficulty: number): number {
  for (let nonce = 0; nonce <= difficulty * 100; nonce++) {
    const hash = crypto.createHash('sha1').update(lastHash + nonce).digest('hex');
    if (hash === expectedHash) {
      return nonce;
    }
  }
  return 0;
}

const socket = new net.Socket();

socket.connect(poolPort, poolIp, () => {
  log(`Connected to mining pool at ${poolIp}:${poolPort}`);
});

let buffer = '';
let stage: 'greeting' | 'job' | 'result' = 'greeting';
let lastHash = '';
let expectedHash = '';
let difficulty = 0;
let jobStartTime = Date.now();

socket.on('data', (data) => {
  buffer += data.toString();
  
  while (buffer.includes('\n')) {
    const lineEnd = buffer.indexOf('\n');
    const line = buffer.substring(0, lineEnd).trim();
    buffer = buffer.substring(lineEnd + 1);

    if (stage === 'greeting') {
      stage = 'job';
      socket.write(`JOB,${username},LOW,\n`);
      jobStartTime = Date.now();
    } else if (stage === 'job') {
      const parts = line.split(',');
      if (parts.length >= 3) {
        lastHash = parts[0];
        expectedHash = parts[1];
        difficulty = parseInt(parts[2], 10);
        
        const nonce = solve(lastHash, expectedHash, difficulty);
        const durationSec = (Date.now() - jobStartTime) / 1000;
        const hashrate = nonce / (durationSec || 0.001);

        stage = 'result';
        socket.write(`${nonce},${hashrate.toFixed(0)},Bartholomew,\n`);
      } else {
        socket.write(`JOB,${username},LOW,\n`);
        jobStartTime = Date.now();
      }
    } else if (stage === 'result') {
      if (line === 'GOOD' || line.includes('GOOD')) {
        parentPort?.postMessage({
          type: 'share_accepted',
          difficulty,
          workerId
        });
      } else {
        log(`Share rejected: ${line}`);
      }
      
      stage = 'job';
      socket.write(`JOB,${username},LOW,\n`);
      jobStartTime = Date.now();
    }
  }
});

socket.on('error', (err) => {
  log(`Connection error: ${err.message}`);
  process.exit(1);
});

socket.on('close', () => {
  log('Connection closed by pool');
  process.exit(1);
});
