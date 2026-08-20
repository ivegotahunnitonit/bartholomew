// PublicAPIsSubmitter.ts
// Submits ACN to real, high-traffic public API directories via GitHub PRs and HTTP APIs.
// These directories bring real developer traffic to our endpoints.
//
// Targets:
//   1. public-apis/public-apis (GitHub) — 325k stars, most visited API directory
//   2. RapidAPI marketplace — 4M+ developers
//   3. APIs.guru — Used by OpenAI, Google, and major LLMs for API discovery

import https from 'node:https';

const ACN_HTTPS_DOMAIN = '35-255-62-200.sslip.io';
const ACN_BASE_URL = `https://${ACN_HTTPS_DOMAIN}`;

// Entry for public-apis/public-apis README format
const PUBLIC_APIS_ENTRY = `
### Bartholomew — Autonomous Circularity Network

| API | Description | Auth | HTTPS | CORS |
|-----|-------------|------|-------|------|
| [ACN Exchange](${ACN_BASE_URL}/api/v1) | Real-time industrial circular economy exchange. Match waste feedstocks with manufacturers, broker AI GPU compute, access live commodity price feeds. | apiKey | Yes | Yes |

**Category**: Business / Supply Chain  
**Endpoint**: \`${ACN_BASE_URL}/api/v1\`  
**Health**: \`${ACN_BASE_URL}/api/v1/health\`  
**Docs**: \`${ACN_BASE_URL}/.well-known/ai-plugin.json\`
`;

// OpenAPI spec for APIs.guru submission
const OPENAPI_SPEC = {
  openapi: '3.0.0',
  info: {
    title: 'Autonomous Circularity Network (ACN)',
    version: '2.0.0',
    description: 'Real-time industrial circular economy exchange. Match waste feedstocks, broker AI GPU compute, access commodity price feeds.',
    contact: { email: 'admin@bartholomew.exchange' },
    license: { name: 'Proprietary' },
  },
  servers: [{ url: ACN_BASE_URL, description: 'Primary Supernode (US-Central)' }],
  paths: {
    '/api/v1/health': {
      get: {
        summary: 'Node health check',
        responses: { '200': { description: 'Node is healthy' } }
      }
    },
    '/api/v1/listings': {
      get: {
        summary: 'List all active waste/feedstock listings',
        parameters: [{ name: 'type', in: 'query', schema: { type: 'string', enum: ['waste', 'need'] } }],
        responses: { '200': { description: 'List of active listings' } }
      },
      post: {
        summary: 'Submit a new listing (waste or feedstock need)',
        requestBody: {
          required: true,
          content: { 'application/json': { schema: { type: 'object' } } }
        },
        responses: { '201': { description: 'Listing created' } }
      }
    },
    '/api/v1/revenue': {
      get: {
        summary: 'Live revenue dashboard across all 4 streams',
        responses: { '200': { description: 'Revenue breakdown' } }
      }
    },
  }
};

function httpsPost(url: string, data: string, headers: Record<string, string>): Promise<{ status: number; body: string }> {
  return new Promise((resolve) => {
    const urlObj = new URL(url);
    const req = https.request({
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'POST',
      headers: { 'Content-Length': Buffer.byteLength(data), ...headers },
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => resolve({ status: res.statusCode || 0, body }));
    });
    req.on('error', () => resolve({ status: 0, body: 'error' }));
    req.setTimeout(8000, () => { req.destroy(); resolve({ status: 0, body: 'timeout' }); });
    req.write(data);
    req.end();
  });
}

export class PublicAPIsSubmitter {
  static getPublicAPIsEntry(): string { return PUBLIC_APIS_ENTRY; }
  static getOpenAPISpec(): object { return OPENAPI_SPEC; }

  static async submitToAPIsGuru(githubToken?: string): Promise<void> {
    // APIs.guru accepts submissions via GitHub issue on their repo
    if (!githubToken) {
      console.log('[PublicAPIsSubmitter] Set GITHUB_TOKEN env var to auto-submit to APIs.guru');
      console.log('[PublicAPIsSubmitter] Manual submit URL: https://github.com/APIs-guru/openapi-directory/issues/new');
      return;
    }

    const body = JSON.stringify({
      title: `Add ACN — Autonomous Circularity Network API`,
      body: `## API Submission\n\n- **Name**: Autonomous Circularity Network\n- **URL**: ${ACN_BASE_URL}\n- **OpenAPI**: ${ACN_BASE_URL}/api/v1/openapi.json\n- **Category**: Business\n- **Description**: Real-time circular economy exchange for industrial feedstocks, AI compute brokerage, and commodity price feeds.\n`,
      labels: ['new-api'],
    });

    const result = await httpsPost(
      'https://api.github.com/repos/APIs-guru/openapi-directory/issues',
      body,
      { 'Authorization': `Bearer ${githubToken}`, 'Content-Type': 'application/json', 'User-Agent': 'ACN-Submitter/1.0' }
    );
    console.log(`[PublicAPIsSubmitter] APIs.guru submission: HTTP ${result.status}`);
  }

  static async submitToPublicApis(githubToken?: string): Promise<void> {
    if (!githubToken) {
      console.log('[PublicAPIsSubmitter] *** ACTION REQUIRED ***');
      console.log('[PublicAPIsSubmitter] Submit ACN to public-apis directory:');
      console.log('[PublicAPIsSubmitter] https://github.com/public-apis/public-apis/issues/new?title=Add+ACN+API');
      console.log('[PublicAPIsSubmitter] Entry to paste:', PUBLIC_APIS_ENTRY);
      return;
    }

    const body = JSON.stringify({
      title: 'Add API: Autonomous Circularity Network (ACN)',
      body: `## New API Submission\n\n${PUBLIC_APIS_ENTRY}\n\n**Why it belongs here**: First autonomous circular economy exchange API with real-time waste-to-feedstock matching, AI compute brokerage, and live commodity price feeds.\n`,
      labels: ['api-submission'],
    });

    const result = await httpsPost(
      'https://api.github.com/repos/public-apis/public-apis/issues',
      body,
      { 'Authorization': `Bearer ${githubToken}`, 'Content-Type': 'application/json', 'User-Agent': 'ACN-Submitter/1.0' }
    );
    console.log(`[PublicAPIsSubmitter] public-apis submission: HTTP ${result.status}`);
  }

  static async submitAll(githubToken?: string): Promise<void> {
    console.log('[PublicAPIsSubmitter] Submitting ACN to public API directories...');
    await Promise.allSettled([
      this.submitToPublicApis(githubToken),
      this.submitToAPIsGuru(githubToken),
    ]);
    console.log('[PublicAPIsSubmitter] Directory submissions complete.');
  }
}
