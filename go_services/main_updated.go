// ADD THIS TO EXISTING main.go handleTrajectoryScan FUNCTION:
// Replace the JSON decode section with:

	var req TrajectoryScanRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": "Invalid JSON payload",
			"details": err.Error(),
		})
		return
	}

	// VALIDATE AGAINST SCHEMA
	validationErrors := ValidateTrajectory(req)
	if len(validationErrors) > 0 {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": "Schema validation failed",
			"violations": validationErrors,
		})
		return
	}

	res := evaluateTrajectory(req)
	if err := json.NewEncoder(w).Encode(res); err != nil {
		log.Printf("[ERROR] Encode failure: %v", err)
	}
