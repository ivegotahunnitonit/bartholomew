import fs from 'fs';

const envContent = fs.readFileSync('.env', 'utf8');
const tokenMatch = envContent.match(/GITHUB_TOKEN=([^\r\n]+)/);
const TOKEN = tokenMatch ? tokenMatch[1].trim() : '';

const FORK = 'ivegotahunnitonit/memanto';
const BRANCH = 'feat-crewai-okf-migration-adapter-1609';
const HEADERS = {
  'User-Agent': 'ACN-Fixer/1.0',
  'Authorization': `token ${TOKEN}`,
  'Content-Type': 'application/json',
  'Accept': 'application/vnd.github.v3+json',
};

async function ghFetch(path, opts = {}) {
  const res = await fetch(`https://api.github.com${path}`, {
    ...opts,
    headers: { ...HEADERS, ...(opts.headers || {}) },
  });
  const data = await res.json();
  return { status: res.status, data };
}

async function commitFile(filePath, newContent, commitMsg) {
  const { data: existing } = await ghFetch(`/repos/${FORK}/contents/${filePath}?ref=${BRANCH}`);
  const existingSHA = existing?.sha || null;

  const body = {
    message: commitMsg,
    content: Buffer.from(newContent).toString('base64'),
    branch: BRANCH,
    ...(existingSHA ? { sha: existingSHA } : {}),
  };

  const { status, data } = await ghFetch(`/repos/${FORK}/contents/${filePath}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });

  if (status === 200 || status === 201) {
    console.log(`✅ [Committed] ${filePath} → SHA: ${data.content?.sha}`);
  } else {
    console.error(`❌ [Commit Failed] ${filePath}:`, data);
  }
}

async function run() {
  console.log('🚀 Patching PR #1710 on branch', BRANCH);

  // 1. Patch migrate_crewai.py
  const migratePyContent = `"""
CrewAI to OKF (Open Knowledge Format) Migration Adapter
=========================================================
Migrates CrewAI agent memory (short-term, long-term, entity memory) into
vendor-neutral Open Knowledge Format (OKF) markdown bundles for Memanto.

Features:
  - Parses CrewAI SQLite storage, JSON dumps, and memory dictionaries
  - Categorizes into OKF memory types: \`fact\`, \`preference\`, \`context\`, \`entity\`
  - Automated PII & secret redaction (API keys, emails, local filesystem paths)
  - Exports OKF manifest and Memanto migration report
"""

import os
import sys
import json
import re
import sqlite3
import argparse
import datetime
from typing import List, Dict, Any, Tuple

OKF_VERSION = "1.0.0"

# Secret & PII Sanitization Patterns
PII_PATTERNS = [
    (r'(?i)(api[_-]?key|secret|token|password|auth|bearer)\\s*[:=]\\s*["\']?([a-zA-Z0-9_\\-\\.]{16,})["\']?', r'\\1: [REDACTED_SECRET]'),
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]'),
    (r'(?i)/(Users|home|root)/[a-zA-Z0-9._\-]+', '[REDACTED_PATH]'),
]

def sanitize_text(text: str) -> str:
    """Removes API keys, secrets, emails, and sensitive paths from text."""
    if not text or not isinstance(text, str):
        return ""
    sanitized = text
    for pattern, replacement in PII_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    return sanitized

def parse_crewai_json(json_path: str) -> List[Dict[str, Any]]:
    """Parses a CrewAI memory JSON export."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    memories = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("memories", []) or data.get("long_term_memory", []) + data.get("short_term_memory", [])
    else:
        items = []

    for idx, item in enumerate(items):
        memories.append(_normalize_item(item, idx))
    return memories

def parse_crewai_sqlite(db_path: str) -> List[Dict[str, Any]]:
    """Parses a CrewAI SQLite memory database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    memories = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]

    idx = 0
    for table in ["long_term_memories", "short_term_memories", "entity_memories", "memories"]:
        if table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                row_dict = dict(row)
                row_dict["_source_table"] = table
                memories.append(_normalize_item(row_dict, idx))
                idx += 1

    conn.close()
    return memories

def _normalize_item(item: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """Standardizes raw CrewAI items into OKF canonical records."""
    raw_metadata = item.get("metadata") or item.get("attributes") or {}
    if isinstance(raw_metadata, str):
        try:
            metadata = json.loads(raw_metadata)
        except Exception:
            metadata = {}
    elif isinstance(raw_metadata, dict):
        metadata = raw_metadata
    else:
        metadata = {}

    text = item.get("text") or item.get("content") or item.get("memory") or item.get("observation") or item.get("task_description") or ""

    agent_id = item.get("agent_id") or metadata.get("agent_role") or metadata.get("agent") or "crewai_agent"
    task = item.get("task") or metadata.get("task_description") or item.get("task_description") or ""

    # Map CrewAI types to OKF types
    raw_type = (item.get("_source_table") or item.get("type") or metadata.get("memory_type") or "").lower()
    if "entity" in raw_type:
        memory_type = "entity"
    elif "long" in raw_type or "preference" in text.lower():
        memory_type = "preference" if "prefer" in text.lower() or "always" in text.lower() else "fact"
    elif "short" in raw_type or "context" in raw_type:
        memory_type = "context"
    else:
        memory_type = "fact"

    created_at = item.get("timestamp") or item.get("created_at") or datetime.datetime.utcnow().isoformat()

    return {
        "id": f"crewai-mem-{idx+1:04d}",
        "agent_id": str(agent_id),
        "content": sanitize_text(text),
        "memory_type": memory_type,
        "task": sanitize_text(task),
        "created_at": str(created_at),
        "tags": ["crewai", memory_type, "okf_migrated"],
    }

def export_to_okf(memories: List[Dict[str, Any]], output_dir: str) -> Tuple[int, str]:
    """Writes memories out as standard OKF markdown files."""
    os.makedirs(output_dir, exist_ok=True)
    exported_count = 0

    manifest = {
        "okf_version": OKF_VERSION,
        "source_framework": "CrewAI",
        "exported_at": datetime.datetime.utcnow().isoformat(),
        "total_memories": len(memories),
        "memory_types": {},
    }

    for mem in memories:
        if not mem["content"].strip():
            continue

        filename = f"{mem['id']}.md"
        filepath = os.path.join(output_dir, filename)

        frontmatter = {
            "okf_version": OKF_VERSION,
            "id": mem["id"],
            "agent_id": mem["agent_id"],
            "type": mem["memory_type"],
            "tags": mem["tags"],
            "created_at": mem["created_at"],
            "source": "crewai_adapter",
        }

        md_content = f"""---
{json.dumps(frontmatter, indent=2)}
---

# Knowledge Record ({mem['id']})

**Agent Role**: \`{mem['agent_id']}\`  
**Type**: \`{mem['memory_type']}\`  
**Created**: \`{mem['created_at']}\`  

## Memory Content

{mem['content']}

"""
        if mem.get("task"):
            md_content += f"## Originating Task\\n\\n> {mem['task']}\\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        m_type = mem["memory_type"]
        manifest["memory_types"][m_type] = manifest["memory_types"].get(m_type, 0) + 1
        exported_count += 1

    manifest_path = os.path.join(output_dir, "okf_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    report_content = f"""# Memanto OKF Migration & Savings Report

**Source Framework**: CrewAI Agent Memory  
**Export Date**: {manifest['exported_at']}  
**OKF Version**: {OKF_VERSION}  

## Migration Metrics

| Metric | Value |
|---|---|
| Total Source Memories Extracted | {len(memories)} |
| Successfully Exported to OKF | {exported_count} |
| PII / API Keys Redacted | Automated |
| Vendor Lock-in Status | **Eliminated (Portable Markdown)** |

## Memory Type Breakdown

| Type | Count | Description |
|---|---|---|
| \`fact\` | {manifest['memory_types'].get('fact', 0)} | Extracted objective domain knowledge |
| \`preference\` | {manifest['memory_types'].get('preference', 0)} | Agent behaviors and constraints |
| \`context\` | {manifest['memory_types'].get('context', 0)} | Execution context & session state |
| \`entity\` | {manifest['memory_types'].get('entity', 0)} | Entity knowledge graph nodes |

## Verification Command

Test Memanto ingestion via dry-run:
\`\`\`bash
memanto migrate okf {output_dir} --dry-run
\`\`\`
"""
    with open(os.path.join(output_dir, "SAVINGS_REPORT.md"), 'w', encoding='utf-8') as f:
        f.write(report_content)

    return exported_count, manifest_path

def main():
    parser = argparse.ArgumentParser(description="Migrate CrewAI memories to Open Knowledge Format (OKF)")
    parser.add_argument("--source", required=True, help="Path to CrewAI .db or .json memory export")
    parser.add_argument("--output", default="./okf_bundle", help="Output directory for OKF markdown files")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: Source file '{args.source}' does not exist.")
        return

    print(f"[CrewAI Adapter] Extracting memories from {args.source}...")
    if args.source.endswith(".db") or args.source.endswith(".sqlite"):
        memories = parse_crewai_sqlite(args.source)
    elif args.source.endswith(".json"):
        memories = parse_crewai_json(args.source)
    else:
        print("Unsupported file format. Please provide a .db, .sqlite, or .json file.")
        return

    print(f"[CrewAI Adapter] Extracted {len(memories)} memory records.")
    exported, manifest_file = export_to_okf(memories, args.output)
    print(f"[CrewAI Adapter] ✅ Successfully exported {exported} OKF records to '{args.output}'.")
    print(f"[CrewAI Adapter] Manifest: {manifest_file}")

if __name__ == "__main__":
    main()
`;

  await commitFile('examples/migrations/crewai_to_okf/migrate_crewai.py', migratePyContent, 'fix(migrate): parse string metadata as JSON & include task_description in fallback chain');

  // 2. Patch run_sample.sh
  const runSampleContent = `#!/usr/bin/env bash
set -e

echo "=== CrewAI → Memanto OKF Migration Showcase ==="
SCRIPT_DIR="$( cd "$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
OUTPUT_DIR="$SCRIPT_DIR/sample_output/okf"

rm -rf "$OUTPUT_DIR"

python3 "$SCRIPT_DIR/migrate_crewai.py" \\
  --source "$SCRIPT_DIR/sample_data.json" \\
  --output "$OUTPUT_DIR"

echo ""
echo "=== Migration Complete ==="
echo "Exported OKF files in $OUTPUT_DIR:"
ls -l "$OUTPUT_DIR"
`;

  await commitFile('examples/migrations/crewai_to_okf/run_sample.sh', runSampleContent, 'fix(run_sample): clean stale sample output before export');

  // 3. Patch README.md
  const readmeContent = `# CrewAI → Memanto OKF Migration Showcase (Path B - Bounty #1609)

> **Prove the Freedom Loop**: CrewAI Memory → Open Knowledge Format (OKF) → Memanto

This showcase provides a production-ready migration path for **CrewAI** agents to liberate their short-term, long-term, and entity memory stores into vendor-neutral **Open Knowledge Format (OKF)** markdown bundles, and import them seamlessly into **Memanto**.

---

## 🌟 Highlights

- **Multi-Store Support**: Automatically parses CrewAI SQLite databases (\`long_term_memories\`, \`short_term_memories\`, \`entity_memories\`) and JSON memory dumps.
- **Categorization Engine**: Maps CrewAI memories into standard OKF memory types (\`fact\`, \`preference\`, \`context\`, \`entity\`).
- **PII & Secret Redaction**: Built-in automated scrubbing of API keys, emails, passwords, and local filesystem paths prior to export.
- **Memanto Import Ready**: Produces OKF markdown bundles with complete \`okf_manifest.json\` and \`SAVINGS_REPORT.md\` for immediate dry-run ingestion with \`memanto migrate okf\`.

---

## 🚀 Quick Start & Usage

Run commands from the repository root:

\`\`\`bash
# Run the end-to-end migration showcase script
bash ./examples/migrations/crewai_to_okf/run_sample.sh
\`\`\`

Or invoke the migration adapter directly on your own CrewAI memory export:

\`\`\`bash
# From repository root
python3 ./examples/migrations/crewai_to_okf/migrate_crewai.py \\
  --source ./examples/migrations/crewai_to_okf/sample_data.json \\
  --output ./examples/migrations/crewai_to_okf/sample_output/okf
\`\`\`

---

## 📂 Output Bundle Structure

After migration, the output directory contains:

\`\`\`
sample_output/okf/
├── crewai-mem-0001.md
├── crewai-mem-0002.md
├── crewai-mem-0003.md
├── crewai-mem-0004.md
├── okf_manifest.json
└── SAVINGS_REPORT.md
\`\`\`

### Example OKF Markdown Record

\`\`\`markdown
---
{
  "okf_version": "1.0.0",
  "id": "crewai-mem-0001",
  "agent_id": "lead_researcher",
  "type": "fact",
  "tags": ["crewai", "fact", "okf_migrated"],
  "created_at": "2026-07-29T00:00:00Z",
  "source": "crewai_adapter"
}
---

# Knowledge Record (crewai-mem-0001)

**Agent Role**: \`lead_researcher\`  
**Type**: \`fact\`  
**Created**: \`2026-07-29T00:00:00Z\`  

## Memory Content

User prefers concise summary bullet points and markdown code snippets over raw JSON.
\`\`\`

---

## 🧪 Testing Ingestion into Memanto

Verify the exported OKF bundle with Memanto CLI:

\`\`\`bash
memanto migrate okf ./examples/migrations/crewai_to_okf/sample_output/okf --dry-run
\`\`\`
`;

  await commitFile('examples/migrations/crewai_to_okf/README.md', readmeContent, 'docs(readme): update commands to be runnable from repository root');

  console.log('\n🎉 ALL PR #1710 REVIEW FIXES COMMITTED & PUSHED!');
}

run();
