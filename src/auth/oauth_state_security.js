import crypto from 'crypto';

/**
 * Secure OAuth 2.0 State Token Manager
 * Protects against CSRF and Account Takeover attacks by generating
 * cryptographically strong, session-bound, single-use state tokens.
 */
export class OAuthStateManager {
  constructor(ttlSeconds = 600) {
    this.ttlSeconds = ttlSeconds;
    // Maps session_id -> { token: string, expiresAt: number }
    this.stateStore = new Map();
  }

  /**
   * Generates a 32-byte (256-bit) cryptographically secure random state token
   * bound to the user's session_id with a single-use TTL.
   */
  generateState(sessionId) {
    if (!sessionId) {
      throw new Error('sessionId is required to bind OAuth state token');
    }
    const token = crypto.randomBytes(32).toString('hex');
    const expiresAt = Date.now() + this.ttlSeconds * 1000;
    
    this.stateStore.set(sessionId, { token, expiresAt });
    return token;
  }

  /**
   * Validates and immediately consumes the state token (single-use).
   * Returns true if valid, false if invalid, expired, or replayed.
   */
  validateAndConsumeState(sessionId, incomingToken) {
    if (!sessionId || !incomingToken) {
      return false;
    }

    const stored = this.stateStore.get(sessionId);
    if (!stored) {
      return false; // No state found for session or already consumed
    }

    // Immediately consume to enforce single-use (anti-replay)
    this.stateStore.delete(sessionId);

    // Check expiration
    if (Date.now() > stored.expiresAt) {
      return false; // Token expired
    }

    // Timing-safe comparison to prevent side-channel attacks
    try {
      const bufA = Buffer.from(stored.token, 'hex');
      const bufB = Buffer.from(incomingToken, 'hex');
      if (bufA.length !== bufB.length) return false;
      return crypto.timingSafeEqual(bufA, bufB);
    } catch (e) {
      return false;
    }
  }
}
