"""
Universal Test Runner for Bartholomew Test Suite
=================================================
Discovers and executes all unit tests, function tests, and compliance suites in tests/.
"""

import os
import sys
import unittest
import importlib
import inspect

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

pypi_path = os.path.join(BASE_DIR, "pypi_package")
if pypi_path not in sys.path:
    sys.path.insert(0, pypi_path)

test_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("  BARTHOLOMEW COMPREHENSIVE TEST SUITE RUNNER")
print("=" * 70)

passed = 0
failed = 0
errors = []

for f in sorted(os.listdir(test_dir)):
    if f.startswith("test_") and f.endswith(".py"):
        mod_name = f[:-3]
        full_mod_name = f"tests.{mod_name}"
        
        try:
            mod = importlib.import_module(full_mod_name)
        except Exception as e:
            print(f"  [ERROR] Loading {mod_name}: {e}")
            failed += 1
            errors.append((mod_name, str(e)))
            continue

        # 1. Run unittest.TestCase classes if present
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(mod)
        if suite.countTestCases() > 0:
            runner = unittest.TextTestRunner(verbosity=0)
            res = runner.run(suite)
            if res.wasSuccessful():
                print(f"  [PASS] {mod_name} ({suite.countTestCases()} unit tests)")
                passed += suite.countTestCases()
            else:
                print(f"  [FAIL] {mod_name} ({len(res.failures)} failures, {len(res.errors)} errors)")
                failed += len(res.failures) + len(res.errors)
                for err in res.failures + res.errors:
                    errors.append((mod_name, str(err[1])))

        # 2. Run standalone test_* functions
        for name, func in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("test_"):
                try:
                    func()
                    print(f"  [PASS] {mod_name}.{name}")
                    passed += 1
                except Exception as ex:
                    print(f"  [FAIL] {mod_name}.{name}: {ex}")
                    failed += 1
                    errors.append((f"{mod_name}.{name}", str(ex)))

print("=" * 70)
if failed == 0:
    print(f"  ALL TESTS PASSED: {passed} passed, 0 failed (100.0% SUCCESS)")
else:
    print(f"  TEST RUN SUMMARY: {passed} passed, {failed} failed")
    for src, err in errors[:5]:
        print(f"    - {src}: {err.strip().splitlines()[-1]}")
print("=" * 70)

if failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
