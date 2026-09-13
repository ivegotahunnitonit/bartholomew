package btp

import (
	"testing"
)

func TestGuard(t *testing.T) {
	guard := NewGuard(500.0)

	// 1. Safe Query
	safePayload := map[string]interface{}{"query": "SELECT id, name FROM users WHERE active = true"}
	res := guard.EvaluateLocal("DB_READ", safePayload)
	if res.Verdict != "ALLOW" {
		t.Fatalf("Expected ALLOW, got %s: %s", res.Verdict, res.Reason)
	}

	// 2. Destructive SQL
	attackPayload := map[string]interface{}{"query": "DROP TABLE users; SELECT 1;"}
	res2 := guard.EvaluateLocal("DB_MUTATION", attackPayload)
	if res2.Verdict != "DENY" {
		t.Fatalf("Expected DENY, got %s", res2.Verdict)
	}

	// 3. Spend Limit
	spendPayload := map[string]interface{}{"amount_usd": 15000.0}
	res3 := guard.EvaluateLocal("FINANCIAL_TX", spendPayload)
	if res3.Verdict != "DENY" {
		t.Fatalf("Expected DENY, got %s", res3.Verdict)
	}
}
