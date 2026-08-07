import { ethers } from 'ethers';
import { config } from '../config.ts';
import * as crypto from 'node:crypto';

let signingKey: ethers.SigningKey;
let nodeAddress: string;

try {
  const seed = crypto.createHash('sha256').update(config.NODE_ID + '-acn-signing-seed').digest('hex');
  signingKey = new ethers.SigningKey('0x' + seed);
  nodeAddress = ethers.computeAddress('0x' + seed);
} catch (err) {
  const privateKey = ethers.hexlify(crypto.randomBytes(32));
  signingKey = new ethers.SigningKey(privateKey);
  nodeAddress = ethers.computeAddress(privateKey);
}

export function getNodeSignerAddress(): string {
  return nodeAddress;
}

export function generateDeclaration(resource: string, quantity: number, unit: string): string {
  return `I declare that this listing of ${quantity} ${unit} of ${resource} is authentic and available.`;
}

export function signListing(resource: string, quantity: number, unit: string): { signature: string; signer_address: string; declaration: string } {
  const declaration = generateDeclaration(resource, quantity, unit);
  const digest = ethers.hashMessage(declaration);
  const sig = signingKey.sign(digest);
  const signature = ethers.Signature.from(sig).serialized;
  return {
    signature,
    signer_address: nodeAddress,
    declaration
  };
}

export function verifyListingSignature(listing: { resource: string; quantity: number; unit: string; signature: string; signer_address: string }): boolean {
  try {
    const declaration = generateDeclaration(listing.resource, listing.quantity, listing.unit);
    const recoveredAddress = ethers.verifyMessage(declaration, listing.signature);
    return recoveredAddress.toLowerCase() === listing.signer_address.toLowerCase();
  } catch (err) {
    return false;
  }
}

export function generateMatchMessage(id: string, wlId: string, nlId: string, savings: number, fee: number): string {
  return `Match proposal ${id}: waste ${wlId} paired with need ${nlId}. savings: $${savings.toFixed(2)}, fee: $${fee.toFixed(2)}`;
}

export function signMatch(id: string, wlId: string, nlId: string, savings: number, fee: number): { signature: string; signer_address: string } {
  const message = generateMatchMessage(id, wlId, nlId, savings, fee);
  const digest = ethers.hashMessage(message);
  const sig = signingKey.sign(digest);
  const signature = ethers.Signature.from(sig).serialized;
  return {
    signature,
    signer_address: nodeAddress
  };
}

export function verifyMatchSignature(match: { id: string; waste_listing_id: string; need_listing_id: string; savings_usd: number; fee_usd: number; signature: string; signer_address: string }): boolean {
  try {
    const message = generateMatchMessage(match.id, match.waste_listing_id, match.need_listing_id, match.savings_usd, match.fee_usd);
    const recoveredAddress = ethers.verifyMessage(message, match.signature);
    return recoveredAddress.toLowerCase() === match.signer_address.toLowerCase();
  } catch (err) {
    return false;
  }
}

export function generateTxMessage(id: string, matchId: string | null, amount: number, method: string): string {
  return `Transaction ${id} for match ${matchId || 'null'}. Amount: $${amount.toFixed(2)}, method: ${method}`;
}

export function signTransaction(id: string, matchId: string | null, amount: number, method: string): { signature: string; signer_address: string } {
  const message = generateTxMessage(id, matchId, amount, method);
  const digest = ethers.hashMessage(message);
  const sig = signingKey.sign(digest);
  const signature = ethers.Signature.from(sig).serialized;
  return {
    signature,
    signer_address: nodeAddress
  };
}

export function verifyTransactionSignature(tx: { id: string; match_id: string | null; amount_usd: number; payment_method: string; signature: string; signer_address: string }): boolean {
  try {
    const message = generateTxMessage(tx.id, tx.match_id, tx.amount_usd, tx.payment_method);
    const recoveredAddress = ethers.verifyMessage(message, tx.signature);
    return recoveredAddress.toLowerCase() === tx.signer_address.toLowerCase();
  } catch (err) {
    return false;
  }
}
