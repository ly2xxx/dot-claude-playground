# YANG LI

**victorlee2012.vl@gmail.com | Glasgow, UK | [LinkedIn](https://www.linkedin.com/in/yang-li-78917021/) | [AI Engineering Portfolio](https://github.com/ly2xxx/public-demo/blob/main/demo.md)**

---

## PROFILE

AI Solution Architect and Lead Software Engineer with 20+ years building resilient, secure production systems across investment banking, wealth management, and energy — now leading enterprise adoption of agentic AI. Combines hands-on production GenAI engineering (LangGraph, MCP, RAG, Claude Code/SKILL) with the security, observability, and governance discipline built over a career in regulated, high-stakes systems. Currently architects agentic developer tooling for 50+ engineering teams at Barclays; independently ships production-pattern AI systems — published to PyPI and Docker Hub — with self-hosted observability and automated evaluation built in from the start, not bolted on.

**Areas of Strength:** AI Solution Architecture & Governance | Secure & Responsible AI Design | Stakeholder Alignment & Executive Communication | Mentorship & Team Upskilling | Cross-functional Collaboration | Innovation Leadership

---

## TECHNICAL SKILLS

**Agentic AI & LLM Engineering**
`Proficient`  LangGraph · LangChain · Claude Code · Claude SKILL development · MCP (Model Context Protocol) tool development · RAG systems · Prompt engineering · LLM API orchestration · LangFlow
`Familiar`    Azure OpenAI concepts · FAISS · Weaviate · Pinecone · LangSmith

**Evaluation & Observability (AI-specific)**
`Proficient`  OpenTelemetry (OTEL) for LLM/agent tracing · Prometheus · Grafana · Tempo · pytest-bdd + DeepEval (LLM evaluation, tool-routing assertions) · ELK Stack
`Familiar`    LLM-as-judge evaluation design · multi-model cost/accuracy benchmarking

**Secure & Responsible AI**
`Proficient`  Data-sensitivity-based model routing (local vs. cloud) · privacy-aware telemetry design · read-only data-boundary design
`Familiar`    AI governance frameworks · responsible AI principles (bias awareness, explainability, human-in-the-loop)

**Cloud, Security & Platform Engineering**
`Proficient`  Docker · Helm · GitLab CI/CD · Python automation · security automation at scale (Wiz, 5,000+ repositories)
`Familiar`    AWS (EC2, ECS, EKS) · Terraform · Kubernetes · Red Hat OpenShift

**Languages & Core Engineering**
`Proficient`  Python (4+ yrs, AI/automation focus) · Java (10+ yrs, distributed systems) · SQL · RESTful API design (Swagger/OpenAPI)
`Familiar`    C/C++ · Kafka · Event-driven architecture · Microservices

---

## SELECTED AI ENGINEERING PORTFOLIO

*A self-directed engineering journey since 2023 — each stage solving a real enterprise AI-adoption blocker. Full write-up with source links: [github.com/ly2xxx/public-demo](https://github.com/ly2xxx/public-demo/blob/main/demo.md)*

- **md-mcp** — containerised MCP server exposing markdown knowledge bases to any MCP client. Published to [PyPI](https://pypi.org/project/md-mcp/) and Docker Hub, with a Helm chart, healthchecks, and a working pytest-bdd/DeepEval test suite verified across multiple LLMs
- **langgraph_ollama** — multi-agent RAG system (LangGraph + Ollama) with full self-hosted observability: OpenTelemetry traces every agent node and LLM call into Tempo, Prometheus, and Grafana — zero external dependencies, privacy-aware by design (call shape logged, never content)
- **Evaluation harness** — Gherkin specs → pytest-bdd → DeepEval, running the same behavioural test suite across a portfolio of models to select for cost and accuracy on evidence, not assumption

---

## WORK EXPERIENCE

### BARCLAYS | Glasgow, UK

**Platform Engineer / Senior Software Developer | May 2025 – Present**

Architect secure agentic developer tooling and enterprise GitLab CI/CD platform serving 50+ engineering teams running 500+ daily pipeline executions.

- Built a phased release-automation framework combining Python-based deterministic API filtering with agentic Claude SKILL/GitLab MCP root-cause scoring — cut pipeline triage from 100+ candidates to 10–20 (investigation time down 85%, 2+ hours → <15 minutes), automated evidence collection and Confluence publishing, and reduced total release time from 4 hours to 1, unlocking a 3× release-cadence increase (weekly → three releases a week)
- Co-developed Python-based security automation integrating Wiz vulnerability scanning across 5,000+ repositories on AWS EKS, reducing critical security exposure window from 14 days to <48 hours — mentored a junior engineer through the cloud deployment
- Optimised Docker workspace images for Coder cloud environments on AWS EC2 by 95% (11+ GB → 500 MB) using a UBI9-micro base, materially lowering infrastructure overhead
- Project-managed CIO deck automation for GFED Technology, leading a team of interns from requirements to implementation; reduced manual effort by 90% (20 hours → 2 hours)

**Senior Software Developer | Enterprise Architect | Nov 2024 – Apr 2025**

Pioneered enterprise GenAI adoption via locally-hosted LLM experimentation, balancing innovation with data-security compliance in a regulated banking environment.

- Led GenAI experimentation initiative using locally-hosted Ollama models (Llama 3, Mistral), eliminating cloud API costs (~$5K/month) while maintaining data-security compliance
- Developed a proof-of-concept LangFlow-based AI workflow for automated tech-asset discovery across 500+ enterprise applications, informing IT-asset rationalisation strategy
- Automated weekly asset-dependency mapping across 15 business units using Python, eliminating manual tracking and shortening architectural audit cycles
- Promoted AI-native development practices through demos and knowledge-sharing, upskilling engineers on prompt engineering, RAG systems, and local LLM deployment; founded and hosted Barclays' internal GenAI enthusiasts community

**Senior Developer & Technical Team Lead | Plan & Invest | Apr 2022 – Nov 2024**

Led architecture and delivery for the Plan & Invest wealth platform, decoupling backend release cycles from a bank-wide monolithic process through multi-stakeholder consensus.

- Won buy-in from a chain of senior stakeholders — including an initially change-averse release process owner — to pilot a decoupled, blue-green release architecture; accelerated release cadence from quarterly to monthly (4×) for the platform serving 100K+ wealth management clients
- Designed an API monitoring framework using Java AOP + OTEL + ELK to trace requests end to end across services, reducing L3 support response time from 45 min to <10 min and eliminating 80% of test-environment outages through proactive alerting
- Led a GenAI hackathon team of 8 engineers to prototype a personalised wealth-management assistant orchestrating LLMs on AWS
- Recruited and onboarded engineers with zero prior system knowledge, achieving full productivity within one quarter through structured knowledge transfer

**Senior Java Developer & Technical Team Lead | Little Book of Wonders, Barclays One | Apr 2015 – Apr 2022**

- Led development of critical Java backend features, growing the customer base 3× (30K → 90K users) while maintaining 99.9% uptime and sub-200ms API response times
- Drove AWS cloud migration for testing environments, achieving a 99.8% deployment success rate and cutting environment spin-up time from 2 days to 4 hours
- Promoted to dual-team technical lead (2018), managing 12 engineers across public-facing websites and backend Java microservices

---

### J.P. MORGAN | Glasgow, UK

**Senior Associate & Tech Lead | Jan 2007 – Apr 2015**

Architected and delivered Java-based high-frequency trading platforms for equity and credit derivatives.

- Architected Java-based high-frequency trade-capture platforms processing 10,000+ transactions/day with <5ms latency SLA
- Led the Platform Trading System (PTS) team as junior Tech Lead (2013–2015), managing 4 developers and delivering 12+ major features annually
- Designed and maintained resilient distributed applications across global infrastructure, contributing to performance tuning, fault tolerance, and operational stability in high-stakes financial systems
- Earned the Financial Derivatives Certification (Chartered Institute for Securities & Investment)
- Promoted twice (2008 Professional → Associate; 2013 Associate → Senior Associate) for sustained technical delivery in a high-volume financial engineering environment

---

### ADVANTAGE ENERGY SOLUTIONS LTD (AESL) | Edinburgh, UK

**Software Engineer | Jan 2003 – Jan 2007**

- Drove software development process maturity by implementing version control (SVN), CI pipelines, and a localisation framework, reducing deployment errors by 60%
- Built and maintained a customer-facing web platform using C++, XML, and XSLT on Windows Server, serving 500+ energy-consulting clients across 5 countries

---

## EDUCATION

**University of Strathclyde | Glasgow, UK**
Master of Business Administration (MBA) – Distinction | Oct 2018 – Jul 2022

- Research: Hybrid workforce productivity optimisation post-pandemic

**University of Glasgow | Glasgow, UK**
MSc, Electrical & Electronic Engineering | Oct 2002 – Jul 2003

- Thesis: Autonomous robot fleet for disaster recovery using C/C++ (legOS)

**Donghua University | Shanghai, China**
BSc, Industrial Automation Engineering | Oct 1998 – Jul 2002

- Capstone: Fuzzy logic control system outperforming a neural-network approach

---

## HIGHLIGHTS & CERTIFICATIONS

- **Production Agentic AI:** Built and shipped Claude Code integrations, MCP tooling, and custom Claude SKILLs at Barclays — plus an independent portfolio of published AI engineering artifacts (PyPI, Docker Hub)
- **Secure & Responsible AI:** Data-sensitivity-based local/cloud model routing, privacy-aware telemetry, read-only data boundaries — security-automation pedigree from leading Wiz vulnerability scanning across 5,000+ repositories
- **GitLab CI/CD at Scale:** Designed and scaled CI/CD automation serving 50+ engineering teams at Barclays; contributed to enterprise-wide GitLab Ultimate migration. [Barclays PLC case study](https://about.gitlab.com/customers/barclays-plc/)
- **J.P. Morgan Alumni:** 8-year tenure building Java distributed trading systems for equity and credit derivatives, prime-finance domain expertise
- **Financial Derivatives Certification** (CISI, 2010)
- **Speaker/Blogger:** Active technology blog since 2016 — [edisonideas.wordpress.com](https://edisonideas.wordpress.com) — covering AI, DevOps, and platform engineering
