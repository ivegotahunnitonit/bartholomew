import * as fs from 'node:fs';
import * as path from 'node:path';
import * as crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ENV_PATH = path.resolve(__dirname, '../.env');
const ENCRYPTION_PASSPHRASE = process.env.ACN_DECRYPT_KEY || 'solomonletishitsubeyuel';

function decryptEnv(ciphertext: string): string {
  if (!ciphertext.startsWith('ACNENC:')) {
    return ciphertext;
  }
  const parts = ciphertext.substring(7).split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const encryptedText = Buffer.from(parts[1], 'hex');
  const hashedKey = crypto.createHash('sha256').update(ENCRYPTION_PASSPHRASE).digest();
  const decipher = crypto.createDecipheriv('aes-256-cbc', hashedKey, iv);
  let decrypted = decipher.update(encryptedText);
  decrypted = Buffer.concat([decrypted, decipher.final()]);
  return decrypted.toString('utf8');
}

if (fs.existsSync(ENV_PATH)) {
  const content = fs.readFileSync(ENV_PATH, 'utf8');
  const decrypted = decryptEnv(content);
  console.log('Decrypted .env contents:');
  decrypted.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const parts = trimmed.split('=');
      const key = parts[0].trim();
      const val = parts.slice(1).join('=').trim();
      // Mask sensitive values
      const isSensitive = key.includes('KEY') || key.includes('SECRET') || key.includes('PASSWORD') || key.includes('WIF') || key.includes('PRIVATE');
      console.log(`${key}=${isSensitive ? '********' : val}`);
    }
  });
} else {
  console.log('.env file not found.');
}
