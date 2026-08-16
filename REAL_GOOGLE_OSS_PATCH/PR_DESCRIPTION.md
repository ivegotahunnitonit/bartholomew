# Pull Request: Modernize AST Node Construction & Deprecation Cleanup in parser.py

## Target Repository

* **Repository**: [google/python-fire](https://github.com/google/python-fire)
* **Target Branch**: `master`

## Title

`Clean up legacy Python <3.8 ast.Str deprecation and modernize Constant AST node handling`

## Description

### Problem

In `fire/parser.py`, `_StrNode` maintained a fallback to `ast.Str` for Python < 3.8. In Python 3.14+, `ast.Str` has been fully removed from the standard library `ast` module, leaving deprecated references and pylint suppressions in the codebase.

### Solution

* Modernize `_StrNode` to directly use standard `ast.Constant` across supported Python versions (3.8+ through 3.14).
* Ensure clean instantiation of `ast.Constant(value=value)` with explicit keyword mapping for robust cross-version AST evaluation.
* Remove obsolete `pylint: disable=no-member` and deprecated legacy type ignores.

### Verification

* Tested across Python 3.8, 3.10, 3.12, 3.13, and 3.14.
* All parser unit tests pass with zero deprecation warnings.
