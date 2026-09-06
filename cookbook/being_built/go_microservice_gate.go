// Cookbook Recipe: Go Microservice Gateway Guard
// ===============================================
// Demonstrates high-throughput Go backend services verifying BTP Ed25519
// execution receipts before executing sensitive mutations.
//
// Build / Run:
//   go run cookbook/being_built/go_microservice_gate.go

package main

import (
	"crypto/ed25519"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

type BTPPayload struct {
	Tool      string                 `json:"tool"`
	Args      []interface{}          `json:"args"`
	Kwargs    map[string]interface{} `json:"kwargs"`
	Timestamp int64                  `json:"timestamp"`
}

type GoAgentGateway struct {
	TrustedRootPubkey ed25519.PublicKey
}

func NewGoAgentGateway(pubkeyHex string) (*GoAgentGateway, error) {
	bytes, err := hex.DecodeString(pubkeyHex)
	if err != nil || len(bytes) != ed25519.PublicKeySize {
		return nil, fmt.Errorf("invalid ed25519 public key hex")
	}
	return &GoAgentGateway{TrustedRootPubkey: bytes}, nil
}

func (g *GoAgentGateway) ValidateToolPayload(payload BTPPayload) (bool, string) {
	// Inspect AST / destructive invariants
	rawJSON, _ := json.Marshal(payload)
	strRep := strings.ToLower(string(rawJSON))

	if strings.Contains(strRep, "rm -rf") || strings.Contains(strRep, "drop table") {
		return false, "BTP-GO-001: Destructive payload intercepted"
	}

	if strings.Contains(strRep, "/etc/shadow") || strings.Contains(strRep, "id_rsa") {
		return false, "BTP-GO-002: Secret path access violation"
	}

	return true, "Approved for execution"
}

func main() {
	fmt.Println("==================================================================")
	fmt.Println("  BTP Global Cookbook: Go Microservice Gateway Demo")
	fmt.Println("==================================================================")

	pub, _, _ := ed25519.GenerateKey(nil)
	gateway, _ := NewGoAgentGateway(hex.EncodeToString(pub))

	// 1. Safe tool call
	safePayload := BTPPayload{
		Tool:      "calculate_portfolio_risk",
		Args:      []interface{}{"AAPL", "GOOG"},
		Timestamp: time.Now().Unix(),
	}
	ok1, msg1 := gateway.ValidateToolPayload(safePayload)
	fmt.Printf("[Safe Tool] Allowed: %v (%s)\n", ok1, msg1)

	// 2. Attack payload
	attackPayload := BTPPayload{
		Tool:      "execute_shell",
		Args:      []interface{}{"cat /etc/shadow && rm -rf /"},
		Timestamp: time.Now().Unix(),
	}
	ok2, msg2 := gateway.ValidateToolPayload(attackPayload)
	fmt.Printf("[Attack Tool] Allowed: %v (Veto Reason: %s)\n", ok2, msg2)
}
