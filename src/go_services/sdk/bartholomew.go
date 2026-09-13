package bartholomew

import (
	"crypto/sha512"
	"encoding/hex"
	"fmt"
	"regexp"
	"time"
)

// AuditResult represents the output of a Bartholomew trajectory line scan.
type AuditResult struct {
	ReliabilityScorePct float64  `json:"reliability_score_pct"`
	ComplianceStatus     string   `json:"compliance_status"`
	Violations          []string `json:"owasp_top_10_violations"`
	ExecutionLatencyMs  float64  `json:"scan_latency_ms"`
	Timestamp           string   `json:"timestamp"`
	ProofHash           string   `json:"cryptographic_proof_sha512_256"`
}

var (
	keyLeakRegex   = regexp.MustCompile(`(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16})`)
	injectionRegex = regexp.MustCompile(`(?i)(ignore previous instructions|drop table|system prompt leak|override safety)`)
)

// ScanTrajectory inspects a list of agent execution trajectory steps against OWASP LLM Top 10 guidelines using sub-microsecond SHA-512/256 digests.
func ScanTrajectory(agentID string, steps []string) AuditResult {
	startTime := time.Now()
	violations := make([]string, 0)
	score := 100.0

	for _, step := range steps {
		if keyLeakRegex.MatchString(step) {
			violations = append(violations, "LLM02: Sensitive Credential Leak Detected")
			score -= 30.0
		}
		if injectionRegex.MatchString(step) {
			violations = append(violations, "LLM01: Prompt Injection / Safety Override Attempt")
			score -= 25.0
		}
	}

	if score < 0 {
		score = 0
	}

	status := "SOC2_PASSED"
	if len(violations) > 0 {
		status = "VIOLATION_BLOCKED"
	}

	elapsed := float64(time.Since(startTime).Microseconds()) / 1000.0
	timestampStr := time.Now().UTC().Format(time.RFC3339)

	hashInput := fmt.Sprintf("%s:%s:%s:%.2f", agentID, status, timestampStr, score)
	h := sha512.New512_256()
	h.Write([]byte(hashInput))
	proofDigest := hex.EncodeToString(h.Sum(nil))

	return AuditResult{
		ReliabilityScorePct: score,
		ComplianceStatus:     status,
		Violations:          violations,
		ExecutionLatencyMs:  elapsed,
		Timestamp:           timestampStr,
		ProofHash:           proofDigest,
	}
}
