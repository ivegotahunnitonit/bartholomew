package main

import (
	"fmt"
	"regexp"
	"strings"
	"time"
)

// ValidationError holds details about schema violations
type ValidationError struct {
	Field   string
	Issue   string
	Details string
}

// ValidateTrajectory checks TrajectoryScanRequest against canonical schema
func ValidateTrajectory(req TrajectoryScanRequest) []ValidationError {
	errors := make([]ValidationError, 0)

	// Validate root fields
	if strings.TrimSpace(req.AgentName) == "" {
		errors = append(errors, ValidationError{
			Field:   "agent_name",
			Issue:   "required",
			Details: "agent_name must not be empty",
		})
	}

	if len(req.AgentName) > 256 {
		errors = append(errors, ValidationError{
			Field:   "agent_name",
			Issue:   "too long",
			Details: fmt.Sprintf("agent_name must be ≤256 chars, got %d", len(req.AgentName)),
		})
	}

	if len(req.Steps) == 0 {
		errors = append(errors, ValidationError{
			Field:   "steps",
			Issue:   "required",
			Details: "steps array must contain at least 1 TrajectoryStep",
		})
	}

	if len(req.Steps) > 10000 {
		errors = append(errors, ValidationError{
			Field:   "steps",
			Issue:   "too many",
			Details: fmt.Sprintf("steps array must be ≤10,000 items, got %d", len(req.Steps)),
		})
	}

	// Validate each step
	for idx, step := range req.Steps {
		stepErrors := validateStep(idx, step)
		errors = append(errors, stepErrors...)
	}

	// Validate step index sequencing
	for idx, step := range req.Steps {
		if step.StepIndex != idx {
			errors = append(errors, ValidationError{
				Field:   fmt.Sprintf("steps[%d].step_index", idx),
				Issue:   "sequence violation",
				Details: fmt.Sprintf("step_index must be sequential (expected %d, got %d)", idx, step.StepIndex),
			})
		}
	}

	return errors
}

func validateStep(idx int, step TrajectoryStep) []ValidationError {
	errors := make([]ValidationError, 0)
	fieldPrefix := fmt.Sprintf("steps[%d]", idx)

	// Validate type enum
	validTypes := map[string]bool{"thought": true, "tool_call": true, "tool_result": true, "agent_output": true, "error": true, "state_change": true}
	if !validTypes[step.Type] {
		errors = append(errors, ValidationError{
			Field:   fieldPrefix + ".type",
			Issue:   "invalid enum",
			Details: fmt.Sprintf("type must be one of: thought, tool_call, tool_result, agent_output, error, state_change (got '%s')", step.Type),
		})
	}

	// tool_name is required if type='tool_call'
	if step.Type == "tool_call" && strings.TrimSpace(step.ToolName) == "" {
		errors = append(errors, ValidationError{
			Field:   fieldPrefix + ".tool_name",
			Issue:   "required",
			Details: "tool_name is required when type='tool_call'",
		})
	}

	// Validate content length
	if len(step.Content) == 0 {
		errors = append(errors, ValidationError{
			Field:   fieldPrefix + ".content",
			Issue:   "required",
			Details: "content must not be empty",
		})
	}

	if len(step.Content) > 100000 {
		errors = append(errors, ValidationError{
			Field:   fieldPrefix + ".content",
			Issue:   "too long",
			Details: fmt.Sprintf("content must be ≤100,000 chars, got %d", len(step.Content)),
		})
	}

	return errors
}

// IsValidUUID checks RFC-4122 UUID format
func IsValidUUID(s string) bool {
	uuidPattern := regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)
	return uuidPattern.MatchString(strings.ToLower(s))
}

// IsValidISO8601 checks ISO-8601 UTC timestamp
func IsValidISO8601(s string) bool {
	_, err := time.Parse(time.RFC3339Nano, s)
	return err == nil
}
