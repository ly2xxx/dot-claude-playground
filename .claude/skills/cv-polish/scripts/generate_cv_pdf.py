"""Generate a professional PDF from the CV markdown content."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

output_dir = r"h:\code\yl\dot-claude-playground\.claude\skills\cv-polish\output\pdfs"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "CV_Yang_Li_2026.pdf")

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=18 * mm,
    rightMargin=18 * mm,
    topMargin=15 * mm,
    bottomMargin=15 * mm,
)

DARK = colors.HexColor("#1a1a2e")
ACCENT = colors.HexColor("#2c5f8a")
MID_GRAY = colors.HexColor("#666666")

name_style = ParagraphStyle("Name", fontSize=22, textColor=DARK, spaceAfter=2,
                             fontName="Helvetica-Bold", alignment=TA_CENTER)
tagline_style = ParagraphStyle("Tagline", fontSize=10, textColor=ACCENT, spaceAfter=6,
                                fontName="Helvetica", alignment=TA_CENTER)
section_style = ParagraphStyle("Section", fontSize=11, textColor=ACCENT, spaceBefore=10,
                                spaceAfter=3, fontName="Helvetica-Bold")
org_style = ParagraphStyle("Org", fontSize=10, textColor=DARK, spaceAfter=1,
                            fontName="Helvetica-Bold")
role_style = ParagraphStyle("Role", fontSize=9.5, textColor=MID_GRAY, spaceAfter=3,
                             fontName="Helvetica-Oblique")
bullet_style = ParagraphStyle("Bullet", fontSize=9, textColor=DARK, spaceAfter=3,
                               fontName="Helvetica", leading=13,
                               leftIndent=10, firstLineIndent=-10)
sub_section_style = ParagraphStyle("SubSection", fontSize=9.5, textColor=DARK, spaceBefore=5,
                                    spaceAfter=2, fontName="Helvetica-Bold")
profile_style = ParagraphStyle("Profile", fontSize=9, textColor=DARK, spaceAfter=3,
                                fontName="Helvetica", leading=13)
spec_style = ParagraphStyle("Spec", fontSize=8.5, textColor=ACCENT, spaceAfter=4,
                              fontName="Helvetica-Oblique")
edu_title_style = ParagraphStyle("EduTitle", fontSize=9.5, textColor=DARK, spaceAfter=1,
                                  fontName="Helvetica-Bold")


def section_header(text):
    return [
        Spacer(1, 4),
        Paragraph(text.upper(), section_style),
        HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=4),
    ]


story = []

# Header
story.append(Paragraph("YANG LI", name_style))
story.append(Paragraph("Platform Engineer | GitLab CI/CD &amp; AI/ML Infrastructure", tagline_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=6))

# Profile
story += section_header("Profile")
story.append(Paragraph(
    "Platform engineer with 20+ years building resilient systems and 1+ year architecting GitLab CI/CD platforms "
    "and SRE automation tools. Currently serving 20+ engineering teams with Python-based developer platforms that "
    "reduced deployment failure investigation time by 85% and accelerated release evidence collection by 70%. "
    "Experienced in GenAI experimentation, vulnerability automation, and observability tooling.",
    profile_style))
story.append(Paragraph(
    "<b>Specialized in:</b> GitLab CI/CD Platform Architecture | Python DevOps Automation | SRE &amp; Release Engineering | "
    "GenAI Integration (LangFlow, Ollama, RAG) | Developer Experience &amp; Productivity",
    spec_style))

# Technical Skills
story += section_header("Technical Skills")

skills_data = [
    ("Platform &amp; Infrastructure", [
        "CI/CD Platforms: GitLab CI/CD, GitHub Actions, Jenkins",
        "Containerization: Docker (working knowledge of Kubernetes, AWS ECS)",
        "Infrastructure as Code: CHEF, learning Terraform and CloudFormation",
        "Cloud Platforms: AWS (EC2, RDS, S3, Lambda), Azure, PaaS solutions",
    ]),
    ("AI/ML Operations &amp; Tooling", [
        "Vector Databases: FAISS, Weaviate, ChromaDB, Pinecone, AWS OpenSearch",
        "ML Infrastructure: Model versioning, experiment tracking, feature stores",
        "Automation: Python (4+ years), Bash, Groovy, PowerShell",
        "AI Integration: LLM API orchestration, prompt engineering, RAG systems",
    ]),
    ("Observability &amp; Reliability", [
        "Monitoring &amp; Logging: ELK Stack, Prometheus, Grafana, Tableau, OpenTelemetry (OTEL)",
        "APM &amp; Tracing: Distributed tracing, performance monitoring",
        "Incident Response: Automated root cause analysis, knowledge base scoring systems",
    ]),
    ("Development &amp; APIs", [
        "Languages: Python, Java, C/C++, SQL",
        "API Architecture: RESTful API design, microservices, event-driven systems",
        "Databases: PostgreSQL, Oracle, AWS RDS, vector databases",
    ]),
]

for group_name, items in skills_data:
    story.append(Paragraph(group_name, sub_section_style))
    for item in items:
        story.append(Paragraph(f"&#8226; {item}", bullet_style))

# Work Experience
story += section_header("Work Experience")

story.append(Paragraph("BARCLAYS WEALTH MANAGEMENT | Glasgow, UK", org_style))

barclays_roles = [
    (
        "Platform Engineer / Senior Software Developer | May 2025 – Present (11 months)",
        [
            "Built GitLab CI/CD developer platform serving 20+ engineering teams with 500+ daily pipeline executions, "
            "reducing deployment failure investigation time by 85% (from 2+ hours to &lt;15 minutes) through automated "
            "log analysis and intelligent root cause detection",
            "Developed Python-based SRE automation tools: vulnerability identification system scanning 100+ repositories "
            "weekly, reducing critical security exposure window from 14 days to &lt;48 hours; and release automation "
            "framework reducing evidence collection from 3.5 hours to 1 hour per release",
            "Designed GitLab pipeline monitoring dashboard with real-time failure analytics, enabling proactive incident "
            "response and reducing MTTR by 60% across platform teams",
            "Experimented with MCP-based Claude skill development for DevOps automation, building custom tools for "
            "cross-team pipeline visibility and knowledge base-backed failure analysis",
        ]
    ),
    (
        "Senior Software Developer | Enterprise Architect | Nov 2024 – Apr 2025 (6 months)",
        [
            "Led GenAI experimentation initiative for corporate tech stack rationalization using locally-hosted Ollama "
            "models (Llama 3, Mistral), eliminating cloud API costs (~$5K/month) while maintaining data security compliance",
            "Developed proof-of-concept LangFlow-based AI workflows for automated tech asset discovery and categorization; "
            "explored consolidation across 500+ enterprise applications (limited by opensource LLM capabilities at the time)",
            "Built Python automation tools for enterprise architecture analysis: application dependency mapping reducing "
            "manual documentation effort by 70%, technology stack duplication detection across 15 business units",
            "Promoted AI-native development practices through demos and knowledge-sharing sessions, upskilling junior "
            "developers on prompt engineering, RAG systems, and local LLM deployment",
        ]
    ),
    (
        "Senior Developer &amp; Technical Team Lead | Apr 2022 – Nov 2024 (2.5 years)",
        [
            "Accelerated release cadence from quarterly to monthly (4x improvement) by designing decoupled backend "
            "release architecture, enabling independent service deployments for Plan and Invest platform serving 100K+ clients",
            "Implemented downstream API monitoring framework using Java AOP + ELK + Tableau, reducing L3 support "
            "response time from 45min to &lt;10min and eliminating 80% of test environment outages",
            "Led GenAI hackathon team (8 engineers) developing AI-powered code review assistant with ChatGPT integration, "
            "reducing review cycle time by 35% and later adopted across 3 divisions serving 200+ developers",
            "Recruited and onboarded team of 6 engineers, achieving full productivity within 1 quarter through structured "
            "knowledge transfer program",
            "Championed early adoption of GitHub Copilot and ChatGPT, achieving 25% faster feature delivery across "
            "50+ person engineering organization",
        ]
    ),
    (
        "Senior Java Developer &amp; Technical Team Lead | Nov 2016 – Apr 2022 (5.5 years)",
        [
            "Drove AWS cloud migration for Little Book of Wonders (LBOW) testing environments with automated CHEF "
            "deployment, achieving 99.8% deployment success rate and reducing environment spin-up from 2 days to 4 hours",
            "Led development of critical features growing LBOW customer base 3x (30K to 90K users) while maintaining "
            "99.9% uptime and sub-200ms API response times",
            "Successfully upgraded Adobe AEM infrastructure (v6.0 to v6.3) for customer-facing platform with zero "
            "downtime serving 100K+ users",
            "Promoted to dual-team technical lead (2018) managing 12 engineers across public websites and backend "
            "Java microservices",
        ]
    ),
]

for role_title, bullets in barclays_roles:
    story.append(Paragraph(role_title, role_style))
    for b in bullets:
        story.append(Paragraph(f"&#8226; {b}", bullet_style))
    story.append(Spacer(1, 3))

story.append(Paragraph("J.P. MORGAN | Glasgow, UK", org_style))
story.append(Paragraph("Senior Associate &amp; Team Lead | Jan 2007 – Apr 2015", role_style))
for b in [
    "Transitioned from C++ to Java to architect high-frequency trading platforms for equity and credit derivatives, "
    "processing 10K+ transactions/day with &lt;5ms latency SLA",
    "Led Platform Trading System (PTS) team as Tech Lead (2013–2015), managing 6 developers and delivering 12+ "
    "major features annually across distributed microservices architecture",
    "Achieved derivative trading certification while building domain expertise in technical implementation and "
    "business requirements",
    "Promoted twice (2008 Professional→Associate, 2013 Associate→Senior Associate) for exceptional technical delivery",
]:
    story.append(Paragraph(f"&#8226; {b}", bullet_style))

story.append(Spacer(1, 5))

story.append(Paragraph("ADVANTAGE ENERGY SOLUTIONS LTD (AESL) | Edinburgh, UK", org_style))
story.append(Paragraph("Software Engineer | Feb 2004 – Jan 2007", role_style))
for b in [
    "Drove software development process maturity by implementing version control (SVN), CI pipelines, and "
    "localization framework, reducing deployment errors by 60%",
    "Built and maintained customer-facing web platform using C#, XML, XSLT on Windows Server, serving 500+ "
    "energy consulting clients across 5 countries",
]:
    story.append(Paragraph(f"&#8226; {b}", bullet_style))

# Education
story += section_header("Education")

edu_entries = [
    ("University of Strathclyde | Glasgow, UK",
     "Master of Business Administration (MBA) – Distinction | Oct 2018 – Jul 2022",
     "Research: Hybrid workforce productivity optimization post-pandemic"),
    ("University of Glasgow | Glasgow, UK",
     "MSc, Electrical &amp; Electronic Engineering | Oct 2002 – Jul 2003",
     "Thesis: Autonomous robot fleet for disaster recovery using C/C++ (legOS)"),
    ("Donghua University | Shanghai, China",
     "BSc, Industrial Automation Engineering | Oct 1998 – Jul 2002",
     "Capstone: Fuzzy logic control system outperforming neural network approach"),
]

for inst, degree, note in edu_entries:
    story.append(Paragraph(inst, edu_title_style))
    story.append(Paragraph(degree, role_style))
    story.append(Paragraph(f"&#8226; {note}", bullet_style))

# Achievements & Certifications
story += section_header("Key Achievements &amp; Certifications")
for b in [
    "GitLab CI/CD Architecture Expert: Designed and scaled pipeline automation serving 20+ teams",
    "Derivative Trading Certification (J.P. Morgan, 2011)",
    "AWS Solutions Architect (In progress, exp. completion Q2 2026)",
    "Speaker/Blogger: Active technology blog since 2016 (edisonideas.wordpress.com) focusing on AI, DevOps, and platform engineering",
]:
    story.append(Paragraph(f"&#8226; {b}", bullet_style))

doc.build(story)
print(f"PDF generated successfully: {output_path}")
