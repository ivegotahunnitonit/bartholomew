import { submitToPublicAPIs } from '../src/agents/ForkAndPR.ts';
import { PublicAPIsSubmitter } from '../src/agents/PublicAPIsSubmitter.ts';

console.log('[Submit] Starting directory submissions...');
console.log('[Submit] Step 1: Fork + PR to public-apis/public-apis...');
const prUrl = await submitToPublicAPIs().catch(e => { console.error('[Submit] PR error:', e.message); return ''; });
if (prUrl) console.log(`[Submit] ✅ PR LIVE: ${prUrl}`);

console.log('[Submit] Step 2: APIs.guru submission...');
await PublicAPIsSubmitter.submitToAPIsGuru(process.env.GITHUB_TOKEN).catch(e => console.error(e.message));

console.log('[Submit] All done.');
