import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_pitch_deck():
    pdf_path = os.path.abspath("bartholomew_pitch_deck.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DeckTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DeckSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )
    slide_header_style = ParagraphStyle(
        'SlideHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    slide_cat_style = ParagraphStyle(
        'SlideCat',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'DeckBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=17,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )
    bold_body_style = ParagraphStyle(
        'DeckBoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        'DeckBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=15,
        spaceAfter=6
    )

    story = []

    def make_header(category, title):
        return [
            Paragraph(category.upper(), slide_cat_style),
            Paragraph(title, slide_header_style),
            Spacer(1, 10)
        ]

    # --- SLIDE 1: COVER ---
    story.append(Spacer(1, 50))
    story.append(Paragraph("BARTHOLOMEW", title_style))
    story.append(Paragraph("<b>The Deterministic In-Memory Execution Gate for Autonomous AI Agents</b>", subtitle_style))
    story.append(Spacer(1, 20))
    
    meta_text = """
    <b>Product:</b> btp-guard (Python & TypeScript)<br/>
    <b>Live Sandbox:</b> https://bartholomew.info<br/>
    <b>GitHub:</b> https://github.com/ivegotahunnitonit/bartholomew<br/>
    <b>Stage:</b> Pre-Seed / Seed (YC 2026 Batch Application)
    """
    story.append(Paragraph(meta_text, body_style))
    story.append(PageBreak())

    # --- SLIDE 2: THE PROBLEM ---
    story.extend(make_header("Market Bottleneck", "The Problem: Autonomous Agents Cannot Be Trusted"))
    story.append(Paragraph(
        "Autonomous tool-calling agents (CrewAI, LangGraph, AutoGen, Claude Computer Use) are ready to run business workflows. "
        "However, security teams block production rollout because LLMs hallucinate destructive commands:",
        body_style
    ))
    story.append(Paragraph("• <b>Catastrophic Shell Commands:</b> Agents running <code>rm -rf /</code>, disk formatters, or modifying system configs.", bullet_style))
    story.append(Paragraph("• <b>Production Data Destruction:</b> Unchecked DDL commands like <code>DROP TABLE users;</code> or unbounded updates.", bullet_style))
    story.append(Paragraph("• <b>Credential Exfiltration:</b> LLMs accidentally embedding AWS keys, OpenAI keys, or JWT tokens into public APIs.", bullet_style))
    story.append(Paragraph("• <b>Runaway Token Bills:</b> Recursive tool loops burning thousands of dollars in minutes.", bullet_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(
        "<b>Current Dilemma:</b> Cloud guardrails (AWS Bedrock, NeMo) add <b>1.2s to 2.5s latency</b> per tool call and fail against prompt injections. "
        "Full microVMs (Docker) are too heavy for local agent execution.",
        bold_body_style
    ))
    story.append(PageBreak())

    # --- SLIDE 3: THE SOLUTION ---
    story.extend(make_header("Compiler-Level Security", "The Solution: In-Memory AST Invariant Enforcement"))
    story.append(Paragraph(
        "Bartholomew provides <b>pre-flight, in-process deterministic validation</b> for agent tool calls. "
        "Instead of asking another probabilistic LLM for permission, Bartholomew parses proposed code blocks in memory:",
        body_style
    ))
    
    cols = [
        [
            Paragraph("<b>Sub-50 Microsecond Speed</b>", bold_body_style),
            Paragraph("Executes compiler-level AST checks in <38 µs directly in Python/Node memory. 30,000x faster than cloud LLM judges.", body_style)
        ],
        [
            Paragraph("<b>Zero Cloud Overhead</b>", bold_body_style),
            Paragraph("$0.00 cost per check. 100% local, requiring zero outbound HTTP requests, background daemons, or tokens.", body_style)
        ],
        [
            Paragraph("<b>Cryptographic Attestations</b>", bold_body_style),
            Paragraph("Generates RFC 8785 Ed25519 tamper-proof digital signatures for every executed action for SOC 2 & EU AI Act audits.", body_style)
        ]
    ]
    t = Table(cols, colWidths=[240, 240, 240])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t)
    story.append(PageBreak())

    # --- SLIDE 4: PRODUCT & ARCHITECTURE ---
    story.extend(make_header("Technology & Architecture", "1-Line Drop-In SDK: Defense-in-Depth"))
    story.append(Paragraph(
        "Developers secure any agent framework with a single decorator:",
        body_style
    ))
    
    code_text = """
    <b>from btp_guard import secure_tool</b><br/><br/>
    @secure_tool(strict_mode=True)<br/>
    def run_terminal_command(cmd: str):<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;# Catches 'rm -rf' or 'DROP TABLE' in &lt;50µs BEFORE the OS syscall is dispatched.<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;return subprocess.check_output(cmd, shell=True)
    """
    story.append(Paragraph(code_text, ParagraphStyle('CodeBlock', parent=body_style, fontName='Courier', fontSize=10, leading=14, backColor=colors.HexColor('#F1F5F9'), borderPadding=10)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Works natively with:</b> LangChain, CrewAI, AutoGen, LlamaIndex, Claude Desktop MCP, and E2B Sandboxes.", body_style))
    story.append(PageBreak())

    # --- SLIDE 5: VALIDATION & TRACTION ---
    story.extend(make_header("Traction & Benchmarks", "Empirical Validation & Community Release"))
    story.append(Paragraph(
        "Bartholomew has undergone rigorous stress testing and public release across standard package registries:",
        body_style
    ))
    story.append(Paragraph("• <b>1,000,000 Payload Stress Fuzzer:</b> 100% zero-escape rate against adversarial injections and obfuscations.", bullet_style))
    story.append(Paragraph("• <b>Live Package Registries:</b> Official releases on <b>PyPI (<code>pip install btp-guard</code>)</b> and <b>npm (<code>npm install btp-guard</code>)</b>.", bullet_style))
    story.append(Paragraph("• <b>Interactive Web Sandbox:</b> Live browser demo running with client-side Web Workers at <b>https://bartholomew.info</b>.", bullet_style))
    story.append(Paragraph("• <b>Anthropic MCP Registry:</b> Smithery.ai verified manifest for Claude Desktop.", bullet_style))
    story.append(Paragraph("• <b>Academic Grounding:</b> Published research DOI (10.5281/zenodo.22076536) covering deterministic execution bounds.", bullet_style))
    story.append(PageBreak())

    # --- SLIDE 6: BUSINESS MODEL & GTM ---
    story.extend(make_header("Commercialization", "Business Model: Open-Core to Enterprise Fleet Gate"))
    story.append(Paragraph("<b>Three-Tier Monetization Model:</b>", body_style))
    
    tiers = [
        [
            Paragraph("<b>Tier 1: Open Source (Free)</b>", bold_body_style),
            Paragraph("<b>Developer Wedge</b><br/>• Core <code>btp-guard</code> SDK<br/>• Local AST validation<br/>• Single-agent protection<br/>• Community adoption driver", body_style)
        ],
        [
            Paragraph("<b>Tier 2: Enterprise Fleet ($499 - $2,500/mo)</b>", bold_body_style),
            Paragraph("<b>Platform & Security Teams</b><br/>• Centralized agent telemetry<br/>• Multi-agent swarm consensus<br/>• Automated SOC 2 audit exports<br/>• Enterprise policy manager", body_style)
        ],
        [
            Paragraph("<b>Tier 3: Cloud Marketplace</b>", bold_body_style),
            Paragraph("<b>AWS & GCP Marketplace</b><br/>• 1-Click container deploy<br/>• Direct cloud billing offset<br/>• Co-sell with cloud partners<br/>• Dedicated enterprise SLAs", body_style)
        ]
    ]
    t2 = Table(tiers, colWidths=[240, 240, 240])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # --- SLIDE 7: VISION & ASK ---
    story.extend(make_header("Future & The Ask", "The Execution Layer for Autonomous AI"))
    story.append(Paragraph(
        "<b>Vision:</b> Within 3 years, billions of autonomous agent actions will occur every second across commerce, finance, and DevOps. "
        "Probabilistic LLMs cannot be trusted with raw OS execution. Bartholomew will be the ubiquitous, microsecond cryptographic execution gate standard for autonomous systems.",
        body_style
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>The Ask (YC Batch 2026):</b>", bold_body_style))
    story.append(Paragraph("• $500,000 standard YC investment.", bullet_style))
    story.append(Paragraph("• Accelerate enterprise sales into AI platform teams building autonomous coding, financial, and healthcare agents.", bullet_style))
    story.append(Paragraph("• Expand native compiler targets across WebAssembly, Rust, and Go runtimes.", bullet_style))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>Contact:</b> founders@bartholomew.info | https://bartholomew.info", subtitle_style))

    doc.build(story)
    print(f"[OK] Pitch Deck PDF generated successfully at: {pdf_path}")

if __name__ == "__main__":
    create_pitch_deck()
