# Product Hunt Launch Kit: Bartholomew v5.4.4

Use this kit to launch or schedule Bartholomew on Product Hunt: [https://www.producthunt.com/posts/new](https://www.producthunt.com/posts/new)

---

## 1. Core Listing Metadata

* **Product Name**: Bartholomew (btp-guard)
* **Tagline** (max 60 characters):
  ```text
  Zero accidental wipes. Zero runaway bills for AI agents.
  ```
* **Links**:
  * Website: `https://bartholomew.info`
  * Interactive Playground: `https://bartholomew.info/cookbook`
  * GitHub: `https://github.com/ivegotahunnitonit/bartholomew`
  * PyPI: `https://pypi.org/project/btp-guard/`
  * npm: `https://www.npmjs.com/package/btp-guard`
  * VS Code / Cursor: `https://open-vsx.org/extension/Bartholomew/bartholomew-guard-vscode`
* **Pricing**: Free & Open-Source (Apache 2.0) / Pro: $49/mo / Fleet: $199/mo
* **Topics / Tags**: Developer Tools, Artificial Intelligence, Open Source, Security, Startups

---

## 2. Short Description (max 260 characters)

```text
Stop worrying about AI agents hallucinating DROP TABLE, running rm -rf, or racking up 4-figure API bills. Bartholomew gives startups a 1-line in-process safety net (<35us) with zero setup and zero enterprise bloat.
```

---

## 3. First Maker Comment (To post immediately upon launch)

```text
Hey Product Hunt community!

We built Bartholomew because we kept seeing startup founders and engineering teams caught between two bad options:
1. Babysitting AI agents manually, wasting hours clicking "Approve" buttons on routine tasks.
2. Letting agents run hands-free and waking up to broken staging databases, wiped filesystems, or a $2,000 runaway cloud bill.

Prompt-level guardrails don't work reliably when models hallucinate or retry. Bartholomew solves this directly inside process memory with sub-35 microsecond deterministic checks before any command or tool ever reaches your operating system or database.

What you get out of the box:
- 30-Second Setup: Just one decorator (@guard.protect, @btp_crewai_tool, or @btp_langchain_tool) on your functions.
- Accidental Wipe Defense: Catches and blocks destructive commands (DROP TABLE, TRUNCATE, rm -rf, disk wipes) before execution.
- Hard Spend Caps: Set dollar budgets so runaway retry loops never spike your OpenAI or cloud invoices.
- In-Flight Secret Masking: Automatically scrubs AWS, OpenAI, GitHub, and custom credentials before they hit prompt logs or traces.
- Multi-Framework Ready: 1-line integration with CrewAI, LangGraph, AutoGen, LlamaIndex, Claude Desktop, and Cursor.

Test it right now in your terminal:
$ pip install btp-guard && python -m btp_guard try

Or test attacks live in your browser in 5 seconds with zero installation:
https://bartholomew.info/cookbook

The core engine is 100% open-source under Apache 2.0. For growing startups and teams, our Pro plan is $49/month with zero enterprise lock-in.

We would love to hear your feedback on how your team manages agent tool safety and runaway loop boundaries!
```

---

## 4. Media & Asset Checklist

* **Thumbnail**: `web/dist/favicon.svg`
* **Gallery Image 1**: Hero banner showing "Zero Accidental Wipes. Zero Runaway Bills." from `https://bartholomew.info`
* **Gallery Image 2**: Interactive In-Browser AST Invariant Playground at `https://bartholomew.info/cookbook`
* **Gallery Image 3**: Terminal screenshot showing `python cli.py try` (sub-35us blocks)
* **Gallery Image 4**: Framework Integrations diagram (CrewAI, LangGraph, AutoGen, Cursor, MCP)
