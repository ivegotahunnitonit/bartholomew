package btp

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

// EvaluationResult represents the decision output from Bartholomew Guard.
type EvaluationResult struct {
	Verdict     string  `json:"verdict"`
	Status      string  `json:"status"`
	Reason      string  `json:"reason"`
	LatencyUs   float64 `json:"latency_microseconds"`
	PayloadHash string  `json:"payload_hash,omitempty"`
}

// Guard is the high-performance Go sub-millisecond execution guard.
type Guard struct {
	GatewayURL  string
	MaxSpendUSD float64
}

// NewGuard initializes a new Bartholomew Guard (100% offline local evaluation by default).
func NewGuard(maxSpendUSD float64) *Guard {
	if maxSpendUSD <= 0 {
		maxSpendUSD = 500.0
	}
	return &Guard{
		GatewayURL:  "",
		MaxSpendUSD: maxSpendUSD,
	}
}

// EvaluateLocal performs a sub-millisecond in-process check (<20 microseconds).
func (g *Guard) EvaluateLocal(actionType string, payload map[string]interface{}) EvaluationResult {
	start := time.Now()
	rawBytes, _ := json.Marshal(payload)
	rawStr := strings.ToLower(string(rawBytes))

	// 1. Destructive SQL & System Command Invariants
	destructive := []string{
		"drop table", "drop schema", "drop database", "truncate table",
		"/etc/shadow", "rm -rf", "aws_secret_access_key", "sk-live", "eval(", "exec(",
	}

	for _, p := range destructive {
		if strings.Contains(rawStr, p) {
			latencyUs := float64(time.Since(start).Nanoseconds()) / 1000.0
			return EvaluationResult{
				Verdict:   "DENY",
				Status:    "BLOCKED_LOCAL_INVARIANT",
				Reason:    fmt.Sprintf("BTP-SEC-001: Destructive pattern detected: '%s'", p),
				LatencyUs: latencyUs,
			}
		}
	}

	// 2. Spend Limit Governance
	if amount, ok := payload["amount_usd"].(float64); ok && amount > g.MaxSpendUSD {
		latencyUs := float64(time.Since(start).Nanoseconds()) / 1000.0
		return EvaluationResult{
			Verdict:   "DENY",
			Status:    "BLOCKED_SPEND_LIMIT",
			Reason:    fmt.Sprintf("BTP-SEC-005: Requested $%.2f exceeds policy cap $%.2f", amount, g.MaxSpendUSD),
			LatencyUs: latencyUs,
		}
	}

	// 3. Compute Cryptographic Hash
	hash := sha256.Sum256(rawBytes)
	hashHex := hex.EncodeToString(hash[:])
	latencyUs := float64(time.Since(start).Nanoseconds()) / 1000.0

	return EvaluationResult{
		Verdict:     "ALLOW",
		Status:      "VERIFIED_VALID",
		Reason:      "All local pre-flight policy invariants passed.",
		LatencyUs:   latencyUs,
		PayloadHash: hashHex,
	}
}
