"""
Bartholomew Trust Protocol (BTP v4.1) — Autonomous Lead Scraper
================================================================
Sources real technical decision-makers from public channels:
  1. GitHub — repos using LangGraph, CrewAI, AutoGen, LlamaIndex (tool execution)
  2. PyPI Dependents — packages that list btp-guard or agentic frameworks as deps
  3. Hacker News — "Show HN" and "Ask HN" posts about AI agents / LLM security
  4. GitHub Issues — open issues mentioning tool safety, prompt injection, AI security

Populates leads_queue.json via LeadManager for the voice engine dial queue.

Usage:
    python -m src.voice.lead_scraper --limit 50
    python -m src.voice.lead_scraper --source github --limit 25
    python -m src.voice.lead_scraper --source hn --limit 20
"""

import argparse
import json
import logging
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.voice.lead_manager import Lead, LeadManager, LeadStatus

logger = logging.getLogger("btp.voice.lead_scraper")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ---------------------------------------------------------------------------
# Utility: lightweight JSON fetcher (no third-party deps)
# ---------------------------------------------------------------------------

def _fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Any:
    """Fetch a JSON endpoint with a simple User-Agent. Returns None on failure."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "btp-lead-scraper/4.1 (github.com/ivegotahunnitonit/bartholomew)")
    req.add_header("Accept", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.debug("Fetch failed for %s: %s", url, exc)
        return None


def _fetch_text(url: str, timeout: int = 10) -> str:
    """Fetch raw HTML/text content."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "btp-lead-scraper/4.1 (github.com/ivegotahunnitonit/bartholomew)")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        logger.debug("Text fetch failed for %s: %s", url, exc)
        return ""


# ---------------------------------------------------------------------------
# Source 1: GitHub — repos that use key agentic frameworks
# ---------------------------------------------------------------------------

# Repos/orgs building AI agent tools with real tool-execution risk surface
GITHUB_SEARCH_QUERIES = [
    "autogen tool_use execution safety",
    "langgraph agent tool security",
    "crewai tool execution guard",
    "llamaindex agent tool calling security",
    "openai function calling security production",
    "ai agent sql injection prevention",
    "llm tool execution sandbox python",
    "multi agent framework security python",
]

def scrape_github(limit: int = 30, github_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search GitHub for repos/users building agentic systems with tool execution.
    Returns a list of raw lead dicts with name, company, role, email, notes.
    """
    leads = []
    headers = {}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    seen_logins = set()

    for query in GITHUB_SEARCH_QUERIES:
        if len(leads) >= limit:
            break

        encoded = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded}+language:python&sort=updated&per_page=10"
        data = _fetch_json(url, headers=headers)
        if not data or "items" not in data:
            time.sleep(2)
            continue

        for repo in data.get("items", []):
            if len(leads) >= limit:
                break

            owner = repo.get("owner", {})
            login = owner.get("login", "")
            if not login or login in seen_logins:
                continue
            seen_logins.add(login)

            # Fetch owner profile for contact details
            profile = _fetch_json(f"https://api.github.com/users/{login}", headers=headers) or {}
            email = profile.get("email") or None
            company = (profile.get("company") or "").strip("@").strip() or repo.get("name", "AI Labs")
            name = profile.get("name") or login
            bio = profile.get("bio") or ""
            html_url = profile.get("html_url", "")
            repo_desc = repo.get("description") or ""
            stars = repo.get("stargazers_count", 0)

            # Skip bots and orgs with no real contact surface
            if not name or name.lower() in {"bot", "dependabot"}:
                continue

            # Infer role from bio
            role = _infer_role(bio)

            lead = {
                "name": name,
                "company": company or repo.get("full_name", "GitHub").split("/")[0],
                "phone": "",   # Will need manual enrichment
                "email": email,
                "role": role,
                "notes": (
                    f"GitHub: {html_url} | Repo: {repo.get('full_name', '')} "
                    f"({stars}⭐) — {repo_desc[:120]}"
                ),
                "source": "github",
            }
            leads.append(lead)
            logger.info("  [GitHub] Found: %s @ %s (%s)", name, company, role)
            time.sleep(0.5)   # Respect rate limits

        time.sleep(1)

    return leads


def _infer_role(bio: str) -> str:
    """Heuristically infer seniority role from GitHub bio text."""
    bio_lower = bio.lower()
    if any(w in bio_lower for w in ["cto", "chief technology", "co-founder", "cofounder"]):
        return "CTO / Co-Founder"
    if any(w in bio_lower for w in ["vp of engineering", "vp engineering", "head of engineering"]):
        return "VP of Engineering"
    if any(w in bio_lower for w in ["staff engineer", "principal engineer", "architect"]):
        return "Staff / Principal Engineer"
    if any(w in bio_lower for w in ["ml engineer", "machine learning", "ai engineer", "llm"]):
        return "AI / ML Engineer"
    if any(w in bio_lower for w in ["security", "appsec", "infosec"]):
        return "Security Engineer"
    if any(w in bio_lower for w in ["researcher", "phd", "scientist"]):
        return "AI Researcher"
    if any(w in bio_lower for w in ["founder", "building", "startup"]):
        return "Founder"
    return "AI / Software Engineer"


# ---------------------------------------------------------------------------
# Source 2: Hacker News — Show HN / Ask HN AI agent posts
# ---------------------------------------------------------------------------

HN_QUERIES = [
    "AI agent security tool execution",
    "LangGraph production safety",
    "AutoGen multi-agent security",
    "prompt injection tool calling",
    "LLM agent guardrails production",
]

def scrape_hacker_news(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search Hacker News Algolia API for AI agent / security discussions.
    Extract commenters who are clearly technical builders.
    """
    leads = []
    seen_authors = set()

    for query in HN_QUERIES:
        if len(leads) >= limit:
            break

        encoded = urllib.parse.quote(query)
        url = f"https://hn.algolia.com/api/v1/search?query={encoded}&tags=story&hitsPerPage=10"
        data = _fetch_json(url)
        if not data:
            continue

        for hit in data.get("hits", []):
            if len(leads) >= limit:
                break

            author = hit.get("author", "")
            if not author or author in seen_authors:
                continue
            seen_authors.add(author)

            title = hit.get("title", "")
            story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            points = hit.get("points", 0)
            num_comments = hit.get("num_comments", 0)

            # Only pick up stories with real engagement
            if points < 5 and num_comments < 2:
                continue

            lead = {
                "name": author,
                "company": "Independent / HN",
                "phone": "",
                "email": None,
                "role": "AI Builder / HN Member",
                "notes": (
                    f"HN post: '{title[:100]}' | {points}pts {num_comments} comments | "
                    f"{story_url}"
                ),
                "source": "hacker_news",
            }
            leads.append(lead)
            logger.info("  [HN] Found: %s — '%s' (%dpts)", author, title[:60], points)

        time.sleep(0.5)

    return leads


# ---------------------------------------------------------------------------
# Source 3: GitHub Issues — open issues mentioning AI security / tool safety
# ---------------------------------------------------------------------------

ISSUE_QUERIES = [
    "prompt injection tool calling is:issue is:open",
    "ai agent security tool execution is:issue is:open",
    "autogen security guardrail is:issue is:open",
    "langgraph tool safety is:issue is:open",
    "crewai security is:issue is:open",
]

def scrape_github_issues(limit: int = 20, github_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Find GitHub issue authors actively discussing AI agent security concerns
    — these are the warmest leads (they have the pain point right now).
    """
    leads = []
    headers = {}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    seen_logins = set()

    for query in ISSUE_QUERIES:
        if len(leads) >= limit:
            break

        encoded = urllib.parse.quote(query)
        url = f"https://api.github.com/search/issues?q={encoded}&sort=updated&per_page=8"
        data = _fetch_json(url, headers=headers)
        if not data or "items" not in data:
            time.sleep(2)
            continue

        for issue in data.get("items", []):
            if len(leads) >= limit:
                break

            user = issue.get("user", {})
            login = user.get("login", "")
            if not login or login in seen_logins or login == "dependabot[bot]":
                continue
            seen_logins.add(login)

            # Fetch profile
            profile = _fetch_json(f"https://api.github.com/users/{login}", headers=headers) or {}
            name = profile.get("name") or login
            email = profile.get("email") or None
            company = (profile.get("company") or "").strip("@").strip() or "Open Source"
            bio = profile.get("bio") or ""
            html_url = profile.get("html_url", "")
            repo_url = issue.get("repository_url", "").replace("https://api.github.com/repos/", "")
            issue_title = issue.get("title", "")

            role = _infer_role(bio)

            lead = {
                "name": name,
                "company": company,
                "phone": "",
                "email": email,
                "role": role,
                "notes": (
                    f"GitHub: {html_url} | Filed issue in {repo_url}: "
                    f"'{issue_title[:100]}' — Active AI security concern"
                ),
                "source": "github_issues",
            }
            leads.append(lead)
            logger.info("  [GH Issues] Found: %s @ %s — '%s'", name, company, issue_title[:60])
            time.sleep(0.5)

        time.sleep(1)

    return leads


# ---------------------------------------------------------------------------
# Deduplication + quality filter
# ---------------------------------------------------------------------------

def _dedupe_and_filter(raw_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove dupes by name+company, filter out bot/empty records."""
    seen = set()
    out = []
    for lead in raw_leads:
        name = lead.get("name", "").strip()
        company = lead.get("company", "").strip()

        if not name or name.lower() in {"bot", "actions-user", "github-actions"}:
            continue
        if "[bot]" in name.lower():
            continue

        key = f"{name.lower()}|{company.lower()}"
        if key in seen:
            continue
        seen.add(key)
        out.append(lead)
    return out


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_scraper(
    sources: List[str],
    limit: int,
    github_token: Optional[str] = None,
    leads_file: Optional[Path] = None,
) -> int:
    """
    Run the lead scraper across specified sources and populate the LeadManager queue.
    Returns the number of new leads added.
    """
    manager = LeadManager(storage_file=leads_file)
    existing_names = {l.name.lower() for l in manager.get_all()}

    raw: List[Dict[str, Any]] = []

    if "github" in sources:
        logger.info("🔍 Scraping GitHub repos...")
        raw += scrape_github(limit=limit, github_token=github_token)

    if "hn" in sources:
        logger.info("🔍 Scraping Hacker News...")
        raw += scrape_hacker_news(limit=limit // 2)

    if "issues" in sources:
        logger.info("🔍 Scraping GitHub Issues (warm leads)...")
        raw += scrape_github_issues(limit=limit // 2, github_token=github_token)

    filtered = _dedupe_and_filter(raw)
    added = 0

    for item in filtered:
        name = item.get("name", "").strip()
        if name.lower() in existing_names:
            logger.debug("Skipping duplicate: %s", name)
            continue

        # Only add leads with at least a name and company
        if not name or not item.get("company"):
            continue

        lead = manager.add_lead(
            name=name,
            company=item.get("company", "AI Labs"),
            phone=item.get("phone", ""),        # Empty until manual enrichment
            email=item.get("email"),
            role=item.get("role", "AI Engineer"),
        )
        # Append scraper notes
        lead.notes = item.get("notes", "")
        manager.save()

        existing_names.add(name.lower())
        added += 1
        logger.info("  ✅ Added: %s @ %s [%s]", name, item.get("company"), item.get("source"))

    logger.info("\n🎯 Lead scrape complete. Added %d new leads to queue.", added)
    logger.info("📄 Queue saved to: %s", manager.storage_file)

    # Print summary
    all_leads = manager.get_all()
    pending = [l for l in all_leads if l.status == LeadStatus.PENDING]
    logger.info("📊 Total queue: %d leads | %d pending dial", len(all_leads), len(pending))

    return added


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bartholomew BTP v4.1 — Autonomous Technical Lead Scraper"
    )
    parser.add_argument(
        "--source",
        choices=["github", "hn", "issues", "all"],
        default="all",
        help="Data source to scrape (default: all)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max leads to source per channel (default: 50)"
    )
    parser.add_argument(
        "--github-token",
        type=str,
        default=None,
        help="GitHub personal access token for higher rate limits (optional)"
    )
    parser.add_argument(
        "--leads-file",
        type=str,
        default=None,
        help="Override path to leads_queue.json"
    )
    args = parser.parse_args()

    sources = ["github", "hn", "issues"] if args.source == "all" else [args.source]
    leads_file = Path(args.leads_file) if args.leads_file else None

    run_scraper(
        sources=sources,
        limit=args.limit,
        github_token=args.github_token,
        leads_file=leads_file,
    )
