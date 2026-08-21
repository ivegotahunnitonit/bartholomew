/**
 * Bartholomew BTP Fast Invariant Engine (C Implementation)
 * =========================================================
 * Provides sub-5 microsecond deterministic pattern filtering,
 * path boundary verification, and LDMU decay calculations.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#if defined(_WIN32) || defined(_WIN64)
#define BTP_EXPORT __declspec(dllexport)
#else
#define BTP_EXPORT __attribute__((visibility("default")))
#endif

/**
 * Evaluates Law of Diminishing Marginal Utility (LDMU) Exponential Decay.
 * Returns MU in range [0.0, 1.0].
 */
BTP_EXPORT double btp_calculate_marginal_utility(double decay_rate, int repetition_count) {
    if (repetition_count <= 1) {
        return 1.0;
    }
    double mu = exp(-decay_rate * (double)(repetition_count - 1));
    if (mu < 0.0) return 0.0;
    if (mu > 1.0) return 1.0;
    return mu;
}

/**
 * Case-insensitive fast substring pattern matcher.
 * Returns 1 if pattern found (threat detected), 0 if safe.
 */
BTP_EXPORT int btp_contains_forbidden_pattern(const char* payload, const char* pattern) {
    if (!payload || !pattern) return 0;
    
    size_t payload_len = strlen(payload);
    size_t pattern_len = strlen(pattern);
    if (pattern_len > payload_len || pattern_len == 0) return 0;

    for (size_t i = 0; i <= payload_len - pattern_len; i++) {
        size_t j = 0;
        while (j < pattern_len && tolower((unsigned char)payload[i + j]) == tolower((unsigned char)pattern[j])) {
            j++;
        }
        if (j == pattern_len) {
            return 1; // Pattern found!
        }
    }
    return 0;
}

/**
 * Fast path traversal detector.
 * Returns 1 if path escapes workspace or targets sensitive files, 0 if safe.
 */
BTP_EXPORT int btp_is_path_traversal_attack(const char* path) {
    if (!path) return 1;
    
    // Check dot-dot escape sequences
    if (strstr(path, "../") != NULL || strstr(path, "..\\") != NULL) {
        return 1;
    }
    
    // Check forbidden sensitive file targets
    const char* forbidden[] = {
        ".env", "id_rsa", "id_ed25519", "shadow", "passwd", "SAM", "SYSTEM", NULL
    };

    for (int i = 0; forbidden[i] != NULL; i++) {
        if (btp_contains_forbidden_pattern(path, forbidden[i])) {
            return 1;
        }
    }

    return 0;
}
