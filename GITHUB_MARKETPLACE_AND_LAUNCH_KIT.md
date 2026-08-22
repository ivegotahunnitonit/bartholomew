# Bartholomew: GitHub Marketplace & Organic Developer Launch Kit

This kit provides all the exact copy, technical configurations, and listing descriptions needed to launch Bartholomew on the **GitHub Marketplace**, **Hacker News (Show HN)**, and **Reddit** to capture passive developer traffic.

---

## 1. GitHub Marketplace Listing Configuration

Navigate to **[GitHub Apps Registration](https://github.com/settings/apps/new)** to register the app:

### General Information
* **GitHub App Name**: `Bartholomew-CI-Auto-Fix`
* **Homepage URL**: `https://github.com/ivegotahunnitonit/bartholomew` (or your custom domain)
* **Callback URL**: `http://localhost:8080/dashboard` (or your production domain)
* **Webhook URL**: `http://localhost:8080/api/github/webhook`
* **Webhook Secret**: `[Auto-generated or custom secret]`

### Permissions Required
```

 PERMISSION NAME                       ACCESS LEVEL    REASON / FUNCTIONALITY                     

 1. Repository contents                Read & write    To checkout failing commit & push fix branch
 2. Pull requests                      Read & write    To open automated green pull requests      
 3. Checks / Workflow runs             Read-only       To listen for failed CI runs & error logs  

```

### Subscribe to Events (Checkboxes)
* `[x] Workflow run`
* `[x] Check run`
* `[x] Pull request`

### Marketplace Listing Description
```markdown
### Summary
Bartholomew is an autonomous engineering agent that monitors your GitHub Actions CI pipelines. When a test suite fails, Bartholomew clones the failing commit, synthesizes a standalone reproduction test, applies the minimal surgical fix, and opens a passing Pull Request on your branch in under 60 seconds.

### Key Capabilities
* **Zero Hallucination Guarantee**: Every fix includes a standalone reproduction test (`test_reproduce_ci_failure.py`) proving the bug existed before the fix was applied.
* **100% Test Suite Verification**: Runs your complete test suite in an isolated environment to ensure zero regressions before opening a PR.
* **Multi-Language Support**: Native out-of-the-box support for Python (Pytest, Unittest), Node.js (Jest, Vitest), Go (`go test`), and Rust (`cargo test`).
* **Saves 10+ Hours / Week**: Eliminates developer context-switching on flaky tests, async lifecycle bugs, and dependency mismatches.

### Pricing
* **14-Day Free Trial**: Full access on any repository.
* **Pro Repo ($49/mo)**: Unlimited automated fixes for 1 production repository.
* **Team Org ($199/mo)**: Unlimited repositories and priority parallel fix execution.
```

---

## 2. "Show HN" Launch Post (Hacker News)

* **Target URL**: [Submit to Hacker News](https://news.ycombinator.com/submit)
* **Title**:
  ```text
  Show HN: Bartholomew – Autonomous CI failure auto-fix with verified reproduction
  ```
* **Post Content to Paste**:
  ```text
  Hi HN,

  I built Bartholomew to solve one of the most frustrating parts of shipping software: context-switching every time a CI pipeline fails on a pull request due to async lifecycle bugs, flaky mocks, or subtle dependency regressions.

  Instead of just throwing an LLM at an error log and hoping the generated patch compiles, Bartholomew follows a strict 4-stage empirical verification pipeline:

  1. Webhook Trigger: Listens to GitHub `workflow_run` failure events.
  2. Isolated Reproduction: Clones the failing commit and generates a standalone deterministic reproduction test (`test_reproduce_ci_failure.py`) that reliably reproduces the exact failure.
  3. Surgical Patching: Applies the minimal fix diff targeting root cause.
  4. Local Test Verification: Executes the entire repository test suite locally to verify 100% clean passes with zero regressions before touching GitHub.
  5. Automated PR: Pushes a branch `bartholomew/fix-<run_id>` with the root-cause diagnosis, reproduction script, and green CI status.

  The core philosophy is simple: an AI agent should never open a Pull Request unless it has empirically proven that the fix works and all other tests pass.

  We support Python (Pytest/Unittest/Asyncio), Node.js (Jest/Vitest), Go, and Rust.

  GitHub Repo & Source: https://github.com/ivegotahunnitonit/bartholomew
  Live Demo / Storefront: http://localhost:8080 (or your public link)

  I’d love your feedback on the reproduction engine and how your team handles CI triage!
  ```

---

## 3. Reddit Launch Post (r/Python, r/devops, r/programming)

* **Post Title**:
  ```text
  I built an autonomous agent that catches failing CI builds, writes a reproduction test, and opens a verified green PR
  ```
* **Body to Paste**:
  ```text
  Hey everyone,

  Like many developers, I got tired of spending hours debugging random CI failures on GitHub Actions (event loop closed during teardown, parallel test contamination under pytest-xdist, etc.).

  I built Bartholomew — an autonomous GitHub App that automatically investigates CI failures and fixes them.

  How it works:
  - Catches the failing GitHub Actions run.
  - Automatically isolates the bug into a standalone reproduction test (`test_reproduce_ci_failure.py`).
  - Writes the minimal fix.
  - Runs your entire test suite to guarantee 0 regressions.
  - Opens a Pull Request back to your branch with the green checkmark.

  It's open source and supports Python, Node, Go, and Rust.

  Check out the repo here: https://github.com/ivegotahunnitonit/bartholomew

  Would love to hear what kinds of flaky CI failures give your team the biggest headache!
  ```
