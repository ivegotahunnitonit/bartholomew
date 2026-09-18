"""
Generates a crisp, publication-grade 1-page Seed Investor Teaser PDF for Bartholomew.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_seed_one_pager(filename="SEED_ONE_PAGER.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    header_title = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
        spaceAfter=2
    )

    subtitle = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=8
    )

    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'BodyP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4
    )

    stat_box_title = ParagraphStyle(
        'StatTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        alignment=1
    )

    stat_box_desc = ParagraphStyle(
        'StatDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )

    story = []

    # Title Banner
    story.append(Paragraph("BARTHOLOMEW (BTP v5.4)", header_title))
    story.append(Paragraph("The In-Process Runtime Execution Gateway for Autonomous AI Agent Swarms • Seed Financing ($2.0M at $15M Cap SAFE)", subtitle))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0284c7"), spaceBefore=1, spaceAfter=8))

    # Traction Highlight Box
    stats_data = [
        [
            Paragraph("<b>4,500+</b>", stat_box_title),
            Paragraph("<b>&lt; 35 µs</b>", stat_box_title),
            Paragraph("<b>2,500+</b>", stat_box_title),
            Paragraph("<b>$48.5B</b>", stat_box_title)
        ],
        [
            Paragraph("Active Developers<br/>(npm, PyPI, Open VSX)", stat_box_desc),
            Paragraph("P50 Decision Latency<br/>(50,000x faster than LLMs)", stat_box_desc),
            Paragraph("Metered Actions<br/>in Production Ledger", stat_box_desc),
            Paragraph("TAM by 2028<br/>(Enterprise Agent Security)", stat_box_desc)
        ]
    ]
    t_stats = Table(stats_data, colWidths=[130, 130, 130, 142])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 6))

    # The Problem & Solution Columns
    story.append(Paragraph("THE CRISIS & THE SOLUTION", section_heading))
    story.append(Paragraph(
        "<b>The Autonomous Execution Gap:</b> As enterprises transition from discursive copilots to autonomous multi-agent swarms "
        "(CrewAI, LangGraph, AutoGen, OpenAI Agents SDK), LLMs are granted access to terminal execution, SQL databases, and financial APIs. "
        "A single adversarial prompt injection can trigger <code>rm -rf /</code>, database truncation, secret leakage, or runaway spend cycles.<br/>"
        "<b>Why Existing Tools Fail:</b> LLM-as-a-judge (LlamaGuard) adds 1,500–3,000 ms of latency and doubles inference costs. "
        "Perimeter WAFs cannot see in-process function calls. Traditional EDR lacks Model Context Protocol (MCP) semantics.<br/>"
        "<b>Bartholomew's Breakthrough:</b> Running directly inside the agent's host memory space, Bartholomew evaluates declarative policy "
        "invariants in <b>under 35 microseconds</b>, blocking threats before OS kernel dispatch with zero cloud latency and 100% data sovereignty.",
        body
    ))
    story.append(Spacer(1, 4))

    # Core Architectural Moats
    story.append(Paragraph("UNFAIR ADVANTAGES & DEEP TECH MOAT", section_heading))
    moats = [
        ["Technology Component", "Legacy Guardrails / LLM Judges", "Bartholomew Trust Protocol (v5.4)"],
        ["Decision Latency", "1,500 – 3,000 ms (Bottlenecks Agents)", "< 0.035 ms (35 µs) — 50,000x Faster"],
        ["Execution Seam", "Remote Cloud API (Privacy Leakage)", "In-Process Process Memory (Zero Exfiltration)"],
        ["Marginal Evaluation Cost", "$0.002 – $0.015 / evaluation", "$0.000000 (100% Local / Free Core)"],
        ["Compliance & Receipts", "Unstructured Heuristic Text Logs", "RFC 8785 + Ed25519 Cryptographic Merkle Receipts"],
        ["M2M Economic Rails", "None (Credit Card KYC Only)", "Native RFC L402 Lightning Micropayments ($0.01/action)"]
    ]
    t_moats = Table(moats, colWidths=[120, 200, 212])
    t_moats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('LEADING', (0, 0), (-1, -1), 9.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor("#047857")),
        ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_moats)
    story.append(Spacer(1, 6))

    # Business Model & The Ask
    story.append(Paragraph("BUSINESS MODEL, UNIT ECONOMICS & THE ASK", section_heading))
    story.append(Paragraph(
        "• <b>Bottom-Up PLG + Top-Down Enterprise:</b> Open-source Python & Node SDKs drive organic adoption across 4,500+ developers. "
        "Enterprise Swarm Control Plane ($50,000 – $250,000 ACV) monetizes air-gapped on-premises deployments, continuous SOC 2 / EU AI Act "
        "dossiers, and multi-tenant swarm governance with &gt; 88% gross margins.<br/>"
        "• <b>The Seed Financing:</b> Raising <b>$2,000,000 USD</b> on a Post-Money SAFE (<b>$15M Valuation Cap</b>) to expand our low-latency "
        "systems engineering team, certify SOC 2 Type II, and scale from 10 to 50 enterprise contracts reaching $1.8M ARR in 18 months.<br/>"
        "• <b>Founder:</b> Itsub Alemayehu (Chief Architect, Autonomous Circularity Labs) • <code>itsub@bartholomew.info</code> • <code>https://bartholomew.info</code>",
        body
    ))

    doc.build(story)
    print(f"[SUCCESS] Built 1-page Seed Investor Teaser: {filename}")

if __name__ == "__main__":
    build_seed_one_pager()
