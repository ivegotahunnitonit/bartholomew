import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_resume_pdf():
    pdf_path = os.path.abspath("Itsub_Alemayehu_FullStack_Resume.pdf")
    
    # 0.45-inch tight margins to fit single page perfectly
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=32,
        rightMargin=32,
        topMargin=28,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()
    
    # Typography Styles
    name_style = ParagraphStyle(
        'ResName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=1 # Center
    )
    title_style = ParagraphStyle(
        'ResTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#2563EB'),
        alignment=1,
        spaceAfter=3
    )
    contact_style = ParagraphStyle(
        'ResContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=6
    )
    sec_hdr_style = ParagraphStyle(
        'ResSecHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=4,
        spaceAfter=2
    )
    role_title_style = ParagraphStyle(
        'ResRoleTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    role_sub_style = ParagraphStyle(
        'ResRoleSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569')
    )
    role_date_style = ParagraphStyle(
        'ResRoleDate',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2563EB'),
        alignment=2 # Right
    )
    bullet_style = ParagraphStyle(
        'ResBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=10.8,
        textColor=colors.HexColor('#334155'),
        leftIndent=10,
        spaceAfter=2
    )
    body_style = ParagraphStyle(
        'ResBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=10.8,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # 1. HEADER
    story.append(Paragraph("ITSUB ALEMAYEHU", name_style))
    story.append(Paragraph("SENIOR FULL-STACK & DISTRIBUTED SYSTEMS ENGINEER", title_style))
    contact_line = "itsub@bartholomew.info &bull; github.com/ivegotahunnitonit &bull; bartholomew.info &bull; United States"
    story.append(Paragraph(contact_line, contact_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceAfter=4, spaceBefore=1))

    # 2. EXECUTIVE SUMMARY
    story.append(Paragraph("EXECUTIVE SUMMARY", sec_hdr_style))
    summary_text = (
        "High-velocity Full-Stack & Distributed Systems Engineer with deep expertise in Python, TypeScript, React, Go, and "
        "cloud infrastructure (AWS/GCP/Docker/K8s). Founder & Lead Architect of <b>Bartholomew (btp-guard)</b>, an open-source, "
        "sub-50 microsecond execution runtime with live packages on PyPI and npm. Awarded competitive non-dilutive hyperscaler "
        "cloud grants, architected high-throughput client-side sandboxes, and scaled full-stack architectures passing 100% of enterprise security gates."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 4))

    # 3. TECHNICAL SKILLS
    story.append(Paragraph("TECHNICAL SKILLS", sec_hdr_style))
    skills_data = [
        [
            Paragraph("<b>Frontend:</b> TypeScript, JavaScript, React, Next.js, Vite, TailwindCSS, Web Workers, HTML5/CSS3, State Management", body_style),
            Paragraph("<b>Backend & Systems:</b> Python (FastAPI, Flask, asyncio), Go (Golang), Node.js/Express, REST, WebSockets, gRPC", body_style)
        ],
        [
            Paragraph("<b>Databases & Caching:</b> PostgreSQL, SQLite, MongoDB, Redis, Vector Databases, In-Memory AST Caching", body_style),
            Paragraph("<b>Cloud & DevOps:</b> AWS (EC2, Bedrock, CDK, S3), GCP (Cloud Run), Docker, Kubernetes, CI/CD, Git, Linux/Bash", body_style)
        ],
        [
            Paragraph("<b>Security & AI Systems:</b> AST Code Analysis, Cryptography (Ed25519, SHA-256), OWASP Top 10, Agent Runtimes, LangChain", body_style),
            Paragraph("<b>Testing & Architecture:</b> Pytest, Vitest, TDD, Microservices, Event-Driven Systems, RFC Conformance Suites", body_style)
        ]
    ]
    st = Table(skills_data, colWidths=[270, 278])
    st.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 1.2),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(st)
    story.append(Spacer(1, 4))

    # 4. EXPERIENCE & VENTURE HIGHLIGHTS
    story.append(Paragraph("PROFESSIONAL EXPERIENCE & LEADERSHIP", sec_hdr_style))

    # Job 1: Bartholomew / ACN
    j1_hdr = [
        [Paragraph("<b>Founder & Lead Full-Stack Architect</b> &bull; Bartholomew Autonomous Systems", role_title_style),
         Paragraph("2024 &ndash; PRESENT", role_date_style)]
    ]
    t_j1 = Table(j1_hdr, colWidths=[420, 128])
    t_j1.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 0)]))
    story.append(t_j1)
    story.append(Paragraph("Enterprise in-memory safety kernel, real-time telemetry dashboard, and open-source developer SDK", role_sub_style))
    story.append(Spacer(1, 2))

    story.append(Paragraph("• <b>Full-Stack Web Architecture:</b> Built high-performance reactive web application (React, TypeScript, Vite, TailwindCSS) featuring interactive real-time sandboxes, Web Worker AST compilers, and live SVG threat monitors.", bullet_style))
    story.append(Paragraph("• <b>Distributed Backend & Telemetry:</b> Engineered Python/FastAPI backend & Go inspection microservices delivering sub-50µs execution decisions, handling concurrent agent tool calls with zero cloud network overhead.", bullet_style))
    story.append(Paragraph("• <b>Cryptographic Compliance Layer:</b> Implemented FIPS 186-5 Ed25519 digital signatures and RFC 8785 canonical JSON attestation for automated SOC 2 and EU AI Act audit proofs.", bullet_style))
    story.append(Paragraph("• <b>Developer Ecosystem & Open Source:</b> Published and maintained official packages on <b>PyPI (<code>btp-guard</code>)</b> and <b>npm (<code>btp-guard</code>)</b>; built native adapters for CrewAI, LangGraph, AutoGen, and E2B Sandboxes.", bullet_style))
    story.append(Paragraph("• <b>Robust Quality & CI/CD:</b> Established automated CI/CD pipeline achieving 100% test coverage across 44+ automated unit tests and an adversarial 1,000,000-payload stress fuzzer with zero escapes.", bullet_style))
    story.append(Spacer(1, 4))

    # Job 2: Senior Full-Stack Engineer / Consultant
    j2_hdr = [
        [Paragraph("<b>Senior Full-Stack & Cloud Engineer</b> &bull; Distributed Systems & Web Solutions", role_title_style),
         Paragraph("2021 &ndash; 2024", role_date_style)]
    ]
    t_j2 = Table(j2_hdr, colWidths=[420, 128])
    t_j2.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 0)]))
    story.append(t_j2)
    story.append(Paragraph("Full-lifecycle development across enterprise web applications, API integrations, and cloud infrastructure", role_sub_style))
    story.append(Spacer(1, 2))

    story.append(Paragraph("• Designed, developed, and deployed resilient full-stack applications utilizing React/TypeScript frontends and Python/Node.js microservices, boosting client operational velocity by 40%.", bullet_style))
    story.append(Paragraph("• Architected scalable database schemas across PostgreSQL and MongoDB; optimized complex SQL queries and indexing strategies, reducing median API query latency by 65%.", bullet_style))
    story.append(Paragraph("• Built robust RESTful and WebSocket APIs for real-time dashboards, financial transaction feeds, and external enterprise API gateways with token-bucket rate limiting and RBAC.", bullet_style))
    story.append(Paragraph("• Managed end-to-end containerized deployments using Docker and Kubernetes on AWS (EC2, ECS, S3) with automated GitHub Actions CI/CD workflows.", bullet_style))
    story.append(Spacer(1, 4))

    # 5. GRANTS, CAPITAL & RECOGNITION
    story.append(Paragraph("GRANTS, CAPITAL & RECOGNITION", sec_hdr_style))
    story.append(Paragraph("• <b>Non-Dilutive Hyperscaler Grants & Founder Credits:</b> Awarded competitive non-dilutive founder backing and cloud computing grants from <b>Google Cloud for Startups</b>, <b>AWS Activate</b>, <b>MongoDB for Startups</b>, and <b>Microsoft for Startups Azure</b>.", bullet_style))
    story.append(Paragraph("• <b>Published Research & DOI:</b> Authored peer-reviewed academic preprint on deterministic execution bounds and epistemic provenance in autonomous AI systems (Zenodo DOI: 10.5281/zenodo.22076536).", bullet_style))
    story.append(Paragraph("• <b>Official AI Registry Selection:</b> Approved official manifest on Smithery.ai Anthropic MCP Registry for Claude Desktop / Cursor IDE developer workflows.", bullet_style))
    story.append(Spacer(1, 4))

    # 6. EDUCATION & CERTIFICATIONS
    story.append(Paragraph("EDUCATION & FOUNDATIONS", sec_hdr_style))
    edu_data = [
        [
            Paragraph("<b>B.S. in Computer Science / Software Engineering Background</b>", role_title_style),
            Paragraph("Continuous Specialized Training & Research", role_date_style)
        ]
    ]
    t_edu = Table(edu_data, colWidths=[420, 128])
    t_edu.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 0)]))
    story.append(t_edu)
    story.append(Paragraph("Specialization in Distributed Systems, Compiler Design, Web Technologies, Cryptographic Protocols, and Cloud Architecture.", role_sub_style))

    doc.build(story)
    print(f"[SUCCESS] 1-Page Resume PDF built at: {pdf_path}")

if __name__ == "__main__":
    generate_resume_pdf()
