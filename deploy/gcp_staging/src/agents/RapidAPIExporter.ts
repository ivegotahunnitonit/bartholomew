// RapidAPIExporter.ts
// Generates and exposes OpenAPI 3.0 specification for RapidAPI, Postman, and APIlayer integrations.
// Allows developer marketplaces to discover, subscribe, and bill API requests automatically.

export class RapidAPIExporter {
  static getOpenAPISpec() {
    return {
      openapi: '3.0.3',
      info: {
        title: 'Autonomous Circularity Network (ACN) API',
        description: 'Decentralized waste-to-feedstock matchmaking, DePIN physical validation, and edge compute relay API.',
        version: '2.5.0',
        contact: {
          name: 'ACN Developer Operations',
          url: 'https://35-255-62-200.sslip.io',
          email: 'api@circularitynetwork.io',
        },
      },
      servers: [
        { url: 'https://35-255-62-200.sslip.io', description: 'Primary Multi-AZ Supernode Gateway 1' },
        { url: 'https://34-73-34-145.sslip.io', description: 'US-East Supernode Gateway 2' },
        { url: 'https://136-117-15-127.sslip.io', description: 'US-West Supernode Gateway 3' },
      ],
      paths: {
        '/api/v1/health': {
          get: {
            summary: 'Get network health status',
            responses: {
              '200': { description: 'Node online status and memory metrics' }
            }
          }
        },
        '/api/v1/mesh': {
          get: {
            summary: 'Get Multi-AZ supernode mesh status',
            responses: {
              '200': { description: 'Status of all 5 global availability zone supernodes' }
            }
          }
        },
        '/api/v1/depin': {
          get: {
            summary: 'Get DePIN physical asset attestation stats',
            responses: {
              '200': { description: 'Physical material weight/GPS proofs and validator stats' }
            }
          }
        },
        '/api/v1/quota': {
          get: {
            summary: 'Get API quota billing rates and account stats',
            responses: {
              '200': { description: 'Per-dollar API request rates ($10.00/1k standard, $50.00/1k premium)' }
            }
          }
        },
        '/api/v1/rpc/v1': {
          post: {
            summary: 'JSON-RPC 2.0 Relay Endpoint for Ankr and POKT Network',
            responses: {
              '200': { description: 'JSON-RPC 2.0 response' }
            }
          }
        }
      }
    };
  }
}
