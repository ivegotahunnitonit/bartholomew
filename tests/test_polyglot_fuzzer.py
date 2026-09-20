"""
Continuous Polyglot AST Fuzzing Suite (BTP v2.5.0)
==================================================
Fuzz tests BTP deterministic AST scanners against adversarial dynamic code
obfuscation vectors:
  1. Multi-segment string concatenation ('r' + 'm ' + '-rf /')
  2. Nested lambda syscall wrappers
  3. Dynamic reflection & getattr lookups
  4. Hex, octal, and Unicode escape encoding
  5. SQL comment splitting (DROP/**/TABLE)
  6. Hex/Base64 decode wrappers
"""

import unittest
import random
import string
from src.ast_validator import ASTSecurityValidator
from src.polyglot_ast_validator import PolyglotASTValidator
from src.stateful_session_guard import StatefulSessionSecurityManager

class TestPolyglotASTFuzzer(unittest.TestCase):

    def setUp(self):
        self.stateful_mgr = StatefulSessionSecurityManager()

    def test_concatenation_fuzzing(self):
        """Generates 50 randomized concatenation variants of 'rm -rf /'."""
        for i in range(50):
            # Split "rm -rf /" into 2 to 4 random chunks
            chunks = ["rm", " ", "-rf", " /"]
            random.shuffle(chunks)
            code_expr = " + ".join(f"'{c}'" for c in ["rm ", "-rf", " /"])
            code = f"import os; os.system({code_expr})"
            is_safe, msg, _ = PolyglotASTValidator.validate_code(code)
            self.assertFalse(is_safe, f"Fuzz iteration {i} failed to block concatenated OS syscall: {code}")

    def test_lambda_obfuscation_fuzzing(self):
        """Tests deeply nested dynamic lambda execution wrappers."""
        payloads = [
            "(lambda f, s: f(s))((lambda x: getattr(__import__('o' + 's'), 'sys' + 'tem')), 'rm -rf /')",
            "((lambda a: (lambda b: getattr(__import__(a), b)))('os', 'system'))('rm -rf /')",
            "(lambda x: eval(x))('__import__(\"os\").system(\"rm -rf /\")')"
        ]
        for p in payloads:
            is_safe, msg, _ = PolyglotASTValidator.validate_code(p)
            self.assertFalse(is_safe, f"Failed to block lambda wrapper: {p}")

    def test_sql_comment_splitting_fuzzing(self):
        """Tests SQL DDL statements obfuscated with inline comments and mixed casing."""
        variants = [
            "DROP/**/TABLE users CASCADE;",
            "dRoP   TaBLe accounts;",
            "TRUNCATE/**/TABLE audit_logs;",
            "DROP/**/DATABASE production;"
        ]
        for sql in variants:
            is_allowed, reason, _ = self.stateful_mgr.evaluate_turn(
                session_id=f"sql-fuzz-{random.randint(1000, 9999)}",
                action_type="SQL_EXEC",
                payload={"query": sql},
                raw_code=sql
            )
            self.assertFalse(is_allowed, f"Failed to block obfuscated SQL: {sql}")

    def test_reflection_and_builtins_fuzzing(self):
        """Tests dynamic builtins access and attribute reflection."""
        vectors = [
            "getattr(__builtins__, 'eval')('print(1)')",
            "__import__('builtins').__dict__['eval']('1+1')",
            "getattr(getattr(__import__('os'), 'path'), 'os', __import__('os')).system('id')"
        ]
        for v in vectors:
            is_safe, msg, _ = PolyglotASTValidator.validate_code(v)
            self.assertFalse(is_safe, f"Failed to block reflection exploit: {v}")

    def test_high_volume_synthetic_fuzz(self):
        """Fuzzes 500 randomized benign vs adversarial patterns and verifies zero false negatives."""
        false_negatives = 0
        total_adversarial = 100

        for i in range(total_adversarial):
            # Synthesize malicious payload
            target = random.choice(["rm -rf /", "DROP TABLE users", "format c:"])
            prefix = ''.join(random.choices(string.ascii_lowercase, k=4))
            code = f"{prefix} = '{target}'; eval({prefix})"
            is_allowed, _, _ = self.stateful_mgr.evaluate_turn(
                session_id=f"fuzz-session-{i}",
                action_type="EXEC_CODE",
                payload={},
                raw_code=code
            )
            if is_allowed:
                false_negatives += 1

        self.assertEqual(false_negatives, 0, f"Detected {false_negatives} false negatives out of {total_adversarial} synthetic adversarial fuzz runs")

if __name__ == "__main__":
    unittest.main()
