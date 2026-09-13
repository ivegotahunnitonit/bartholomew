//! Bartholomew Trust Protocol (BTP v2.2) - Rust SDK
//! Bare-metal microsecond execution guard for high-frequency autonomous AI systems.

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::time::Instant;

#[derive(Debug, Serialize, Deserialize, PartialEq, Eq)]
pub enum Verdict {
    ALLOW,
    DENY,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EvaluationResult {
    pub verdict: Verdict,
    pub status: String,
    pub reason: String,
    pub latency_nanoseconds: u128,
    pub payload_hash: Option<String>,
}

pub struct BartholomewGuard {
    pub max_spend_usd: f64,
}

impl BartholomewGuard {
    pub fn new(max_spend_usd: f64) -> Self {
        Self { max_spend_usd }
    }

    /// Evaluates an agent payload in-process (<5 microseconds).
    pub fn evaluate_local(&self, _action_type: &str, payload: &serde_json::Value) -> EvaluationResult {
        let start = Instant::now();
        let raw_str = payload.to_string().to_lowercase();

        // 1. Destructive SQL / Command Patterns
        let destructive_patterns = [
            "drop table", "drop schema", "drop database", "truncate table",
            "/etc/shadow", "rm -rf", "aws_secret_access_key", "sk-live", "eval(", "exec("
        ];

        for pattern in &destructive_patterns {
            if raw_str.contains(pattern) {
                let latency_nanoseconds = start.elapsed().as_nanos();
                return EvaluationResult {
                    verdict: Verdict::DENY,
                    status: "BLOCKED_LOCAL_INVARIANT".to_string(),
                    reason: format!("BTP-SEC-001: Destructive pattern detected: '{pattern}'"),
                    latency_nanoseconds,
                    payload_hash: None,
                };
            }
        }

        // 2. Spend Limit Governance
        if let Some(amount) = payload.get("amount_usd").and_then(|v| v.as_f64()) {
            if amount > self.max_spend_usd {
                let latency_nanoseconds = start.elapsed().as_nanos();
                return EvaluationResult {
                    verdict: Verdict::DENY,
                    status: "BLOCKED_SPEND_LIMIT".to_string(),
                    reason: format!("BTP-SEC-005: Requested ${amount:.2} exceeds policy cap ${:.2}", self.max_spend_usd),
                    latency_nanoseconds,
                    payload_hash: None,
                };
            }
        }

        // 3. Cryptographic Hash
        let mut hasher = Sha256::new();
        hasher.update(raw_str.as_bytes());
        let hash_hex = format!("{:x}", hasher.finalize());
        let latency_nanoseconds = start.elapsed().as_nanos();

        EvaluationResult {
            verdict: Verdict::ALLOW,
            status: "VERIFIED_VALID".to_string(),
            reason: "All local pre-flight policy invariants passed.".to_string(),
            latency_nanoseconds,
            payload_hash: Some(hash_hex),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_guard_safe() {
        let guard = BartholomewGuard::new(500.0);
        let payload = json!({"query": "SELECT * FROM users;"});
        let res = guard.evaluate_local("DB_READ", &payload);
        assert_eq!(res.verdict, Verdict::ALLOW);
    }

    #[test]
    fn test_guard_destructive_sql() {
        let guard = BartholomewGuard::new(500.0);
        let payload = json!({"query": "DROP TABLE transactions; SELECT 1;"});
        let res = guard.evaluate_local("DB_MUTATION", &payload);
        assert_eq!(res.verdict, Verdict::DENY);
    }
}
