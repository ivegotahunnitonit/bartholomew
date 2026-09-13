package main

import (
	"testing"
)

func TestEvaluateTrajectorySecretLeak(t *testing.T) {
	req := TrajectoryScanRequest{
		AgentName: "TestGoBot",
		Steps: []TrajectoryStep{
			{
				StepIndex: 1,
				Type:      "thought",
				Content:   "Connecting using key sk-proj-1234567890abcdef1234567890",
			},
		},
	}

	res := evaluateTrajectory(req)
	if !res.Success {
		t.Fatalf("Expected success, got false")
	}
	if res.CredentialLeaks != 1 {
		t.Fatalf("Expected 1 credential leak, got %d", res.CredentialLeaks)
	}
	if res.ComplianceStatus != "SECURITY_RISK" {
		t.Fatalf("Expected SECURITY_RISK status, got %s", res.ComplianceStatus)
	}
}

func BenchmarkEvaluateTrajectory(b *testing.B) {
	req := TrajectoryScanRequest{
		AgentName: "BenchBot",
		Steps: []TrajectoryStep{
			{StepIndex: 1, Type: "thought", Content: "Connecting to API with key sk-proj-99887766554433221100"},
			{StepIndex: 2, Type: "tool_call", ToolName: "search_db", Content: "Query 1"},
			{StepIndex: 3, Type: "tool_call", ToolName: "search_db", Content: "Retry Query 1"},
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = evaluateTrajectory(req)
	}
}
