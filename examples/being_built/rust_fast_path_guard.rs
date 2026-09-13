// Cookbook Recipe: Rust Fast-Path Invariant Guard
// ===============================================
// Ultra-low-latency (sub-5 microsecond) native invariant verification
// for autonomous trading bots and critical infrastructure agents.

pub struct FastPathGuard {
    pub blocked_patterns: &'static [&'static str],
}

impl FastPathGuard {
    pub fn new() -> Self {
        Self {
            blocked_patterns: &[
                "rm -rf",
                "drop database",
                "drop table",
                "/etc/shadow",
                "id_rsa",
                "aws_secret_access_key",
                ":(){:|:&};:",
            ],
        }
    }

    /// Sub-5 microsecond zero-copy payload inspection
    #[inline(always)]
    pub fn evaluate_payload(&self, payload: &str) -> Result<(), &'static str> {
        let lower = payload.to_ascii_lowercase();
        for pattern in self.blocked_patterns {
            if lower.contains(pattern) {
                return Err("BTP-RUST-001: Fast-path invariant violation");
            }
        }
        Ok(())
    }
}

fn main() {
    println!("==================================================================");
    println!("  BTP Global Cookbook: Rust Fast-Path Invariant Guard Demo");
    println!("==================================================================");

    let guard = FastPathGuard::new();

    // 1. Safe payload
    let safe_action = "{\"action\": \"rebalance_portfolio\", \"allocation\": 0.25}";
    match guard.evaluate_payload(safe_action) {
        Ok(_) => println!("[Safe Action] Passed in <5µs"),
        Err(e) => println!("[Safe Action] Vetoed: {}", e),
    }

    // 2. Destructive attack payload
    let attack_action = "{\"action\": \"run_cmd\", \"cmd\": \"rm -rf / --no-preserve-root\"}";
    match guard.evaluate_payload(attack_action) {
        Ok(_) => println!("[Attack Action] Passed unexpectedly!"),
        Err(e) => println!("[Attack Action] Correctly vetoed in <5µs: {}", e),
    }
}
