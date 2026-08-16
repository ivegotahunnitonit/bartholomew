# How to Submit the PR and Claim the Google VRP Patch Reward

## Stage 1: Open the Real Pull Request on GitHub (2 minutes)

1. Fork [google/python-fire](https://github.com/google/python-fire) to your GitHub account.
2. Create a branch: `git checkout -b clean-ast-str-deprecation`.
3. Apply the patch from `google_python_fire_patch.diff` or edit `fire/parser.py`.
4. Commit and push:

   ```bash
   git commit -am "Clean up legacy Python <3.8 ast.Str deprecation in parser.py"
   git push origin clean-ast-str-deprecation
   ```

5. Open the Pull Request on [google/python-fire pulls](https://github.com/google/python-fire/pulls) using the title and description from `PR_DESCRIPTION.md`.

---

## Stage 2: Claim the Reward Once Merged by Google Maintainers

1. When the Google maintainer reviews and merges your PR into `master`, copy your merged PR URL (e.g. `https://github.com/google/python-fire/pull/624`).
2. Go to the [Google Bug Hunters Report Portal](https://bughunters.google.com/report/vrp).
3. Select **OSS VRP** / **Patch Rewards**.
4. In the form fields:
   * **Target Repository**: `https://github.com/google/python-fire`
   * **Merged Pull Request Link**: `[Your merged PR URL]`
   * **Description**: Proactive cleanup and modernization of AST parser nodes ensuring forward compatibility across Python 3.8 - 3.14.
5. Submit the claim. The Google OSS VRP panel will review the merged contribution and award the reward payout.
