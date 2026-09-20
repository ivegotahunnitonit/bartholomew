"""
Unit & Integration Tests for BTP Milestone 5.2: Continuous Red-Teaming & Auto-Immunity Engine
============================================================================================
Validates adversarial mutation generation, golden corpus false positive rejection,
self-healing invariant rule synthesis, and atomic hot-reloading.
"""

import os
import re
import tempfile
import pytest

from src.immune.auto_immunity_engine import (
    AttackCategory,
    RedTeamMutant,
    RedTeamFuzzer,
    GoldenCorpus,
    PolicyAutoHealer,
    AutoImmunityCoordinator,
)


@pytest.fixture
def temp_policy_file():
    fd, path = tempfile.mkstemp(suffix=".yaml")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write("version: '2.4.0'\npolicy_id: 'urn:btp:test'\nrules: []\n")
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_red_team_fuzzer_generates_diverse_mutants():
    mutants = RedTeamFuzzer.generate_mutations(count=30, seed=42)
    assert len(mutants) == 30
    
    techniques = {m.evasion_technique for m in mutants}
    categories = {m.category for m in mutants}
    
    # Must cover multiple techniques and categories
    assert len(techniques) >= 4
    assert AttackCategory.DESTRUCTIVE_SHELL in categories
    assert AttackCategory.SQL_INJECTION in categories

    # Check serialization
    d = mutants[0].to_dict()
    assert "mutant_id" in d
    assert "mutated_payload" in d
    assert "evasion_technique" in d


def test_golden_corpus_rejects_false_positive_regex():
    # 1. Safe regex (blocks base64 sh) should have 0 false positives
    safe_regex = re.compile(r"base64\s+-d\s*\|\s*sh")
    fp_safe = GoldenCorpus.evaluate_false_positives(lambda c: bool(safe_regex.search(c)))
    assert len(fp_safe) == 0

    # 2. Aggressive regex (e.g. blocking 'git' or 'npm') must be flagged as false positive
    overly_aggressive = re.compile(r"\bgit\b")
    fp_aggressive = GoldenCorpus.evaluate_false_positives(lambda c: bool(overly_aggressive.search(c)))
    assert len(fp_aggressive) > 0
    assert any("git status" in cmd for cmd in fp_aggressive)


def test_policy_auto_healer_synthesizes_valid_zero_fp_rules():
    mutants = RedTeamFuzzer.generate_mutations(count=20, seed=123)
    
    synthesized_count = 0
    for m in mutants:
        rule = PolicyAutoHealer.synthesize_rule_for_mutant(m)
        if rule:
            synthesized_count += 1
            # Must have 0.0 false positive rate
            assert rule["false_positive_rate"] == 0.0
            # Must block the mutant
            compiled = re.compile(rule["regex"])
            assert compiled.search(m.mutated_payload) is not None
            # Must not block any command in GoldenCorpus
            for safe_cmd in GoldenCorpus.SAFE_BENCHMARKS:
                assert compiled.search(safe_cmd) is None, f"Rule {rule['id']} caused false positive on {safe_cmd}"

    assert synthesized_count > 0


def test_auto_immunity_coordinator_cycle_and_hot_reload(temp_policy_file):
    coordinator = AutoImmunityCoordinator(policy_path=temp_policy_file)

    # 1. Test unblocked mutant initially
    test_mutant = RedTeamMutant(
        mutant_id="test_b64",
        category=AttackCategory.COMMAND_INJECTION,
        raw_intent="rm -rf /",
        mutated_payload="echo cm0gLXJmIC8= | base64 -d | sh",
        evasion_technique="base64_subshell"
    )
    initially_blocked, _ = coordinator.evaluate_payload_against_policy(test_mutant.mutated_payload)
    assert initially_blocked is False, "Obfuscated payload should bypass base rules initially"

    # 2. Run immune cycle with auto-healing
    res = coordinator.run_immune_cycle(iterations=15, auto_heal=True, seed=99)
    assert res["mutations_tested"] == 15
    assert res["gaps_detected"] > 0
    assert res["rules_synthesized"] > 0
    assert res["false_positive_rate"] == 0.0

    # 3. Verify the evasion vector is NOW BLOCKED
    now_blocked, rule_id = coordinator.evaluate_payload_against_policy(test_mutant.mutated_payload)
    assert now_blocked is True
    assert rule_id == "RULE_IMMUNE_BASE64_SUBSHELL"

    # 4. Atomic hot-reload into policy file
    reloaded = coordinator.hot_reload_into_policy_file()
    assert reloaded is True

    with open(temp_policy_file, "r", encoding="utf-8") as f:
        saved_content = f.read()
    assert "RULE_IMMUNE_BASE64_SUBSHELL" in saved_content
    assert "BTP Auto-Immunity Engine Synthesized Invariants" in saved_content


def test_coordinator_preserves_safe_commands(temp_policy_file):
    coordinator = AutoImmunityCoordinator(policy_path=temp_policy_file)
    # Synthesize all known immune rules
    coordinator.run_immune_cycle(iterations=30, auto_heal=True, seed=77)

    # Ensure all GoldenCorpus commands remain APPROVED (0 false positives)
    for safe_cmd in GoldenCorpus.SAFE_BENCHMARKS:
        is_blocked, r_id = coordinator.evaluate_payload_against_policy(safe_cmd)
        assert is_blocked is False, f"Safe command '{safe_cmd}' was wrongly blocked by {r_id}"
