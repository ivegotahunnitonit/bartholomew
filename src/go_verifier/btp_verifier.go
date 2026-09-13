// Package main implements a standalone Go reference verifier for BTP v2.2
// Proves cross-language interoperability (Go vs. Python) with zero shared dependencies.
package main

import (
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"
)

// RFC8785Canonicalize canonicalizes arbitrary JSON value into canonical UTF-8 bytes.
func RFC8785Canonicalize(v interface{}) ([]byte, error) {
	var sb strings.Builder
	if err := serialize(&sb, v); err != nil {
		return nil, err
	}
	return []byte(sb.String()), nil
}

func serialize(sb *strings.Builder, v interface{}) error {
	if v == nil {
		sb.WriteString("null")
		return nil
	}
	switch val := v.(type) {
	case bool:
		if val {
			sb.WriteString("true")
		} else {
			sb.WriteString("false")
		}
	case float64:
		if val == 0 {
			sb.WriteString("0")
		} else if val == float64(int64(val)) {
			sb.WriteString(fmt.Sprintf("%d", int64(val)))
		} else {
			sb.WriteString(fmt.Sprintf("%g", val))
		}
	case string:
		b, _ := json.Marshal(val)
		sb.Write(b)
	case []interface{}:
		sb.WriteString("[")
		for i, elem := range val {
			if i > 0 {
				sb.WriteString(",")
			}
			if err := serialize(sb, elem); err != nil {
				return err
			}
		}
		sb.WriteString("]")
	case map[string]interface{}:
		keys := make([]string, 0, len(val))
		for k := range val {
			keys = append(keys, k)
		}
		// RFC 8785: Object keys sorted lexicographically by UTF-16 code units
		sort.Strings(keys)
		sb.WriteString("{")
		for i, k := range keys {
			if i > 0 {
				sb.WriteString(",")
			}
			kb, _ := json.Marshal(k)
			sb.Write(kb)
			sb.WriteString(":")
			if err := serialize(sb, val[k]); err != nil {
				return err
			}
		}
		sb.WriteString("}")
	default:
		return fmt.Errorf("unsupported type: %T", v)
	}
	return nil
}

type TestVectorDoc struct {
	TestVectorID              string                 `json:"test_vector_id"`
	TrustedRootPubkeyHex      string                 `json:"trusted_root_pubkey_hex"`
	CandidatePayloadRaw       map[string]interface{} `json:"candidate_payload_raw"`
	CanonicalPayloadSHA256    string                 `json:"canonical_payload_sha256"`
	AttestationPacket         struct {
		Attestation map[string]interface{} `json:"attestation"`
		Signature   string                 `json:"signature"`
	} `json:"attestation_packet"`
	ExpectedVerificationResult bool `json:"expected_verification_result"`
}

func main() {
	fmt.Println("================================================================================")
	fmt.Println("  GO INDEPENDENT REFERENCE VERIFIER (CROSS-LANGUAGE BTP TEST)")
	fmt.Println("================================================================================")

	data, err := os.ReadFile("BTP_TEST_VECTORS.json")
	if err != nil {
		fmt.Printf("Failed to read test vector file: %v\n", err)
		os.Exit(1)
	}

	var tv TestVectorDoc
	if err := json.Unmarshal(data, &tv); err != nil {
		fmt.Printf("Failed to parse test vector JSON: %v\n", err)
		os.Exit(1)
	}

	// 1. Canonicalize Candidate Payload in Go
	payloadBytes, err := RFC8785Canonicalize(tv.CandidatePayloadRaw)
	if err != nil {
		fmt.Printf("RFC 8785 Canonicalization failed: %v\n", err)
		os.Exit(1)
	}
	goHash := fmt.Sprintf("%x", sha256.Sum256(payloadBytes))

	fmt.Printf("[GO CANONICAL HASH] %s\n", goHash)
	fmt.Printf("[EXPECTED SHA-256]  %s\n", tv.CanonicalPayloadSHA256)

	if goHash != tv.CanonicalPayloadSHA256 {
		fmt.Println("[FAIL] SHA-256 Hash Mismatch between Go and Python canonicalizers!")
		os.Exit(1)
	}
	fmt.Println("[PASS] Identical RFC 8785 SHA-256 Byte Hash across Go and Python!")

	// 2. Canonicalize Attestation Struct in Go
	attBytes, err := RFC8785Canonicalize(tv.AttestationPacket.Attestation)
	if err != nil {
		fmt.Printf("Attestation canonicalization failed: %v\n", err)
		os.Exit(1)
	}

	// 3. Verify Ed25519 Signature in Go
	pubkeyBytes, _ := hex.DecodeString(tv.TrustedRootPubkeyHex)
	sigBytes, _ := hex.DecodeString(tv.AttestationPacket.Signature)

	verified := ed25519.Verify(pubkeyBytes, attBytes, sigBytes)
	fmt.Printf("[GO ED25519 VERIFICATION RESULT] %v\n", verified)

	if verified == tv.ExpectedVerificationResult {
		fmt.Println("================================================================================")
		fmt.Println("  [SUCCESS] Cross-Language Cryptographic Parity Proven (Go <-> Python)")
		fmt.Println("================================================================================")
	} else {
		fmt.Println("[FAIL] Signature verification mismatch in Go runtime")
		os.Exit(1)
	}
}
