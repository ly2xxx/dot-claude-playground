---
name: cv-polish
version: 1.0.0
description: >
  Polish, optimize, and tailor CVs/resumes for job applications with ATS optimization
  and industry-specific best practices. Use when user mentions CV, resume, job application,
  ATS, career document, LinkedIn profile optimization, or asks to polish/review/tailor/improve
  their career documents. Also trigger when user uploads .docx, .pdf files with career-related
  content (employment history, skills, education sections), or shares job posting URLs asking
  for CV customization. Handles multi-stage workflows: analyze current CV → identify gaps →
  tailor to job description → optimize for ATS → polish language → verify formatting.
author: Helpful Bob
tags: [career, cv, resume, job-application, ats-optimization]
---

## 🎯 Core Use Cases

This skill handles six primary workflows:

### 1. **General CV Polish**
**User says:** "Can you review my CV and suggest improvements?"
- Analyze structure, language, achievements
- Check for clarity, conciseness, impact
- Suggest stronger action verbs
- Identify weak/vague statements

### 2. **Job-Specific Tailoring**
**User says:** "Tailor my CV for this role: [URL or job description]"
- Extract job requirements (use `scripts/job_scraper.py` for URLs)
- Map user's experience to job requirements
- Reorder/emphasize relevant achievements
- Add missing keywords naturally

### 3. **ATS Optimization**
**User says:** "Make my CV ATS-friendly" or "Will this pass ATS screening?"
- Check for ATS-killer formatting (tables, graphics, columns)
- Analyze keyword density vs job description
- Verify standard section headers
- Test file format compatibility

### 4. **Industry-Specific Optimization**
**User says:** "Optimize my CV for FAANG roles" or "Review for finance industry"
- Load relevant guide from `references/industry-guides/`
- Apply industry-specific terminology
- Adjust achievement emphasis (tech: impact & scale, finance: P&L & compliance)
- Format according to industry norms

### 5. **Achievement Strengthening**
**User says:** "Help me write better bullet points for my project experience"
- Apply STAR/CAR/PAR frameworks (see `references/achievement-formulas.md`)
- Quantify vague statements
- Add metrics and outcomes
- Transform responsibilities into achievements

### 6. **Multi-Version Management**
**User says:** "Create a version of my CV for startup vs corporate roles"
- Maintain master CV in `assets/`
- Generate tailored versions with different emphasis
- Track changes and versions

---

## 📋 Workflow

### Initial Assessment Phase

When user shares a CV document or requests review:

1. **Identify document location:**
   - Check `assets/` directory for existing CV
   - If user mentions file path, use that
   - If user uploads, note the file path

2. **Understand intent:**
   - General polish or job-specific tailoring?
   - Any specific concerns (ATS, format, language)?
   - Target industry/role/company?

3. **Quick scan:**
   - Read the CV document
   - Identify format (reverse chronological, functional, hybrid)
   - Note sections present (summary, experience, education, skills, etc.)

### Analysis Phase

4. **Run structural analysis:**
   - Check for standard sections
   - Verify chronological consistency
   - Identify formatting issues (if ATS-relevant)

5. **Content analysis:**
   - Evaluate achievement quality (quantified? impactful?)
   - Check for passive voice, weak verbs
   - Assess clarity and conciseness
   - Look for jargon overuse or buzzwords without substance

6. **Job matching (if applicable):**
   - If user provided job URL, run `scripts/job_scraper.py <URL>`
   - Extract: required skills, preferred qualifications, company culture keywords
   - If user pasted description, parse it directly
   - Map user's CV content to job requirements
   - Identify gaps and strengths

### Recommendation Phase

7. **Generate prioritized recommendations:**
   - **Critical:** ATS-killers, major gaps, factual errors
   - **High impact:** Weak achievements, missing keywords, poor structure
   - **Medium impact:** Language polish, redundancy, formatting consistency
   - **Low impact:** Minor wording tweaks, optional additions

8. **Provide examples:**
   - Show before/after for key changes
   - Explain WHY each change improves the CV
   - Quote relevant best practices from references

### Implementation Phase

9. **Collaborative revision:**
   - Work section-by-section
   - Ask for clarification when needed (quantifying achievements, missing context)
   - Suggest specific rewrites, get approval before finalizing
   - Maintain user's authentic voice

10. **Final review:**
    - Read the revised CV end-to-end
    - Check for consistency (formatting, tense, style)
    - Verify no repetition across sections
    - Confirm all user feedback incorporated

11. **Version management:**
    - Save revised version with clear naming: `CV_Yang_Li_Senior_Engineer_Google_2026-03-21.docx`
    - Keep original in `assets/archive/` for reference
    - Update `assets/CV_CHANGELOG.md` with changes made

---

## 🔧 Tools & Scripts

### `scripts/job_scraper.py`

**Purpose:** Extract job requirements from web pages (LinkedIn, Indeed, company career sites)

**Usage:**
```bash
python scripts/job_scraper.py <URL>
```

**Returns JSON with:**
- Job title
- Company name
- Required skills
- Preferred qualifications
- Job description (full text)
- Keywords (extracted via NLP)

**When to use:** User says "tailor my CV for this job: [URL]"

---

### `scripts/cv_analyzer.py` (Future Enhancement)

**Purpose:** Automated ATS compatibility check

**Usage:**
```bash
python scripts/cv_analyzer.py <cv_file_path>
```

**Returns:**
- ATS compatibility score
- Problematic formatting elements
- Keyword density analysis
- Section header validation

**When to use:** User asks "Is my CV ATS-friendly?"

---

## 📚 Reference Guides

### Industry-Specific Guidelines

Load the appropriate guide when user mentions target industry:

- **Tech/Software:** `references/industry-guides/tech.md`
  - Emphasis: Impact, scale, technologies, open-source contributions
  - Formats: GitHub links encouraged, side projects valued

- **Finance/Banking:** `references/industry-guides/finance.md`
  - Emphasis: P&L impact, regulatory compliance, risk management
  - Formats: Conservative, quantified results, certifications prominent

- **Consulting:** `references/industry-guides/consulting.md`
  - Emphasis: Problem-solving, client impact, frameworks used
  - Formats: Action-oriented, structured, frameworks/methodologies highlighted

- **Startup:** `references/industry-guides/startup.md`
  - Emphasis: Ownership, scrappiness, multi-hat wearing, adaptability
  - Formats: Flexible, personality-forward, growth metrics

- **Healthcare:** `references/industry-guides/healthcare.md`
  - Emphasis: Patient outcomes, compliance, certifications, research
  - Formats: Detailed credentials, publications, clinical experience

- **Academia/Research:** `references/industry-guides/academia.md`
  - Emphasis: Publications, grants, teaching, research impact
  - Formats: CV-style (longer), citations, academic honors

### Achievement Writing Formulas

**File:** `references/achievement-formulas.md`

Detailed frameworks for transforming weak bullet points:
- **STAR:** Situation, Task, Action, Result
- **CAR:** Challenge, Action, Result
- **PAR:** Problem, Action, Result
- **XYZ Formula:** Accomplished [X] as measured by [Y], by doing [Z]

### ATS Optimization Rules

**File:** `references/ats-optimization.md`

Comprehensive checklist:
- Formatting do's and don'ts
- Standard section headers ATS systems recognize
- File format recommendations (.docx vs .pdf)
- Keyword optimization without stuffing
- How to test CV against ATS

### Company Culture Guides

**File:** `references/company-cultures/`

When user targets specific companies:
- **FAANG:** `faang.md` - Scale, impact, leadership principles
- **Top Consulting:** `consulting-firms.md` - Structured thinking, client focus
- **Unicorn Startups:** `unicorns.md` - Growth mindset, ownership
- **Traditional Corporate:** `corporate.md` - Stability, process orientation

---

## 🎨 Language & Style Guidelines

### Action Verb Categories

**Achievement-focused (prefer these):**
- Delivered, Drove, Achieved, Accelerated, Optimized, Transformed
- Reduced, Increased, Generated, Saved, Improved, Streamlined
- Led, Spearheaded, Championed, Launched, Built, Created

**Avoid weak/passive verbs:**
- ❌ Responsible for, Helped with, Assisted in, Involved in, Worked on
- ❌ Participated, Contributed, Supported, Handled

### Quantification Principles

**Always quantify when possible:**
- Time: "Reduced processing time from 2 hours to 15 minutes"
- Money: "Generated $2M in additional revenue"
- People: "Led team of 8 engineers across 3 time zones"
- Scale: "Served 10M+ daily active users"
- Percentage: "Improved system reliability from 95% to 99.9%"

**If exact numbers unavailable, use ranges or approximations:**
- "Managed portfolio of 50+ client accounts"
- "Reduced error rates by over 80%"
- "Supported user base of 100K+"

### Voice & Tone

- **Active voice, not passive:** "Led migration" not "Migration was led"
- **Past tense for previous roles:** "Developed", "Managed", "Achieved"
- **Present tense for current role:** "Develop", "Manage", "Lead"
- **No personal pronouns:** Skip "I", "me", "my" - implied by CV format
- **Concise, not verbose:** "Optimized database queries" not "Was responsible for the optimization of various database queries"

---

## 🚨 ATS Red Flags to Avoid

### Formatting Issues

❌ **Don't use:**
- Tables for layout (ATS often can't parse)
- Text boxes (content gets lost)
- Headers/footers for important info
- Graphics, charts, images (except logo if absolutely needed)
- Multiple columns (confuses parsing)
- Fancy fonts (stick to Arial, Calibri, Times New Roman)

✅ **Do use:**
- Simple, single-column layout
- Standard bullet points (•)
- Clear section headers (EXPERIENCE, EDUCATION, SKILLS)
- Consistent formatting throughout
- Standard date formats (MM/YYYY or Month YYYY)

### File Format

- **Preferred:** .docx (most compatible)
- **Acceptable:** .pdf (if job posting doesn't specify .docx)
- **Never:** .pages, .txt, .rtf, .jpg

### Section Headers

Use standard headers ATS systems recognize:
- ✅ **EXPERIENCE** or **WORK EXPERIENCE**
- ❌ Not "My Journey" or "Professional Background"
- ✅ **EDUCATION**
- ❌ Not "Academic Credentials" or "Where I Studied"
- ✅ **SKILLS**
- ❌ Not "Technical Toolkit" or "What I Bring"

---

## 🎓 Quality Checklist

Before finalizing, verify:

### Content Quality
- [ ] Every bullet point starts with strong action verb
- [ ] At least 70% of achievements are quantified
- [ ] No vague statements ("various", "multiple", "several")
- [ ] No jargon without context
- [ ] Achievements > responsibilities
- [ ] Recent experience most detailed (inverse recency)

### Structure & Formatting
- [ ] Sections in logical order (typically: Summary → Experience → Education → Skills)
- [ ] Consistent formatting (bullet style, date format, spacing)
- [ ] Reverse chronological within sections
- [ ] No gaps in employment explained (if relevant)
- [ ] Length appropriate (1 page for <10 years, 2 pages for 10-20 years)

### Language & Clarity
- [ ] No typos or grammatical errors
- [ ] Active voice throughout
- [ ] Consistent verb tense (past for old roles, present for current)
- [ ] No first-person pronouns ("I", "me", "my")
- [ ] Concise (no unnecessary words)

### ATS Compatibility
- [ ] Simple, single-column layout
- [ ] Standard section headers
- [ ] No tables, text boxes, or graphics (except minimal design elements)
- [ ] Standard fonts (10-12pt)
- [ ] .docx or .pdf format
- [ ] Keywords from job description included naturally

### Job Alignment (if tailored)
- [ ] Top 3-5 job requirements clearly addressed
- [ ] Relevant keywords included (not stuffed)
- [ ] Most relevant experience emphasized/reordered
- [ ] Skills section matches job requirements

---

## 💡 Pro Tips

### When User Seems Stuck

**If user says:** "I don't know how to describe what I did"
**Do this:** Ask discovery questions:
- What problem were you trying to solve?
- What was the situation before you started?
- What specific actions did you take?
- What was the measurable outcome?
- Who benefited and how?

### Handling Sensitive Topics

**Career gaps:** Don't hide, briefly explain if >6 months
- "Career break for family care"
- "Sabbatical for professional development"
- "Consulting/freelance work (details available upon request)"

**Job hopping:** Emphasize growth and skill development
- Group short stints under "Consulting Projects"
- Highlight progression in responsibilities
- Focus on cumulative impact across roles

**Lack of formal experience:** Leverage projects, volunteer work, side hustles
- Open-source contributions
- Freelance projects
- Volunteer leadership roles
- Personal projects with measurable outcomes

### Version Control Best Practices

Maintain in `assets/CV_CHANGELOG.md`:
```markdown
## Version History

### v3.2 - 2026-03-21 - Tailored for Google Senior Engineer
- Emphasized scale (10M+ users, 99.9% uptime)
- Added Kubernetes/GCP keywords
- Reordered projects to highlight distributed systems
- Quantified all performance improvements

### v3.1 - 2026-03-15 - ATS Optimization Pass
- Removed table-based layout
- Simplified to single column
- Standardized section headers
- Converted to .docx format

### v3.0 - 2026-03-01 - Major Content Refresh
- Added recent project: AI-powered recommendation engine
- Quantified all achievements (added metrics)
- Removed dated skills (Flash, IE6 support)
- Updated education section (added MBA)
```

---

## 🔄 Continuous Improvement

### After Each Session

1. **Ask for feedback:** "Did this meet your needs? What could be better?"
2. **Document common requests:** Update this SKILL.md if patterns emerge
3. **Refine scripts:** Improve job scraper accuracy based on failed extractions
4. **Expand references:** Add new industry guides as needed

### Metrics to Track (Mental Note)

- Success rate of tailored CVs (user gets interviews?)
- Common pain points (where do users struggle most?)
- Script accuracy (job scraper, ATS analyzer)
- Coverage gaps (industries/roles not well supported)

---

## 📁 Assets Management

### Directory Structure

```
assets/
├── CV_Yang_Li_Master_2026.docx          # Master version (most comprehensive)
├── CV_Yang_Li_Tech_Senior_2026.docx     # Tech-optimized version
├── CV_Yang_Li_Consulting_2026.docx      # Consulting-optimized version
├── CV_CHANGELOG.md                       # Version history and changes
├── support-materials/
│   ├── headshot_professional.jpg        # For LinkedIn/portfolio
│   ├── intro_video.mp4                  # Optional video intro
│   ├── portfolio_samples/               # Work samples, if relevant
│   └── recommendations.pdf              # References/testimonials
└── archive/
    └── [older versions with dates]
```

### Asset Guidelines

**Master CV:**
- Most comprehensive version
- Include ALL experience, projects, achievements
- Source of truth for generating tailored versions

**Tailored Versions:**
- Derived from master
- Emphasize different aspects for different targets
- Named clearly: `CV_[Name]_[Target]_[Date].docx`

**Support Materials:**
- Keep originals (high-res photos, uncompressed videos)
- Compress/optimize only for actual use
- Update regularly (photo not older than 2 years)

---

## 🛠️ Troubleshooting

### Common Issues

**Issue:** User's achievements are vague/weak
**Solution:** Use discovery questions (see "When User Seems Stuck")

**Issue:** Job scraper fails to extract from URL
**Solution:** Ask user to paste job description directly, improve scraper next iteration

**Issue:** CV is too long (>2 pages but <20 years experience)
**Solution:**
1. Remove older/less relevant roles (keep only title, company, dates)
2. Reduce bullet points for earlier roles (keep 2-3 most impressive)
3. Remove obvious skills (e.g., "Microsoft Office" for senior roles)
4. Consolidate similar achievements

**Issue:** User wants to include everything
**Solution:** Explain "relevance > completeness" principle. Maintain master CV with everything, generate tailored versions for applications.

**Issue:** Conflict between ATS optimization and visual appeal
**Solution:** Create two versions:
- ATS-optimized (.docx) for online applications
- Visually polished (.pdf) for in-person/email sharing

---

## 📞 Examples of Realistic User Prompts

Practice with these messy, realistic scenarios:

1. **Casual request:**
   > "yo can u look at my cv? its kinda old and i wanna apply for this job at amazon but idk if its good enough"

2. **Job URL provided:**
   > "I just saw this posting on LinkedIn https://linkedin.com/jobs/12345 and want to apply tonight. My CV is in my downloads folder I think, called Yang_CV_final_v3_REAL.docx. Can you help me tailor it?"

3. **Vague frustration:**
   > "I keep applying but never hear back. What's wrong with my resume?? (attached)"

4. **Specific concern:**
   > "My friend said my CV won't pass ATS because I used a template from Canva with graphics. Is that true? How do I fix it?"

5. **Multi-part request:**
   > "ok so I need to update my experience section with my new role (started 3 months ago as senior data scientist), also I finished my MBA last year so that needs to go in, AND I want to apply for this VP Analytics role at Uber. Can you help with all of that?"

---

## 🎯 Success Criteria

A successful CV polish session results in:

1. **User feels confident** submitting the CV
2. **Measurable improvements:**
   - 80%+ achievements quantified (up from baseline)
   - All action verbs strong (no "responsible for", "helped with")
   - ATS red flags eliminated
   - Keywords from job description naturally integrated
3. **Clear deliverables:**
   - Polished CV saved in `assets/`
   - Changelog updated
   - User knows what changed and why
4. **Next steps defined:**
   - "Submit to Job X by [date]"
   - "Get feedback from [mentor/peer]"
   - "Create LinkedIn profile matching this version"

---

## 🚀 Quick Start for User

**First time using this skill:**

1. Place your current CV in `assets/` folder
2. If applying for specific job, have URL or job description ready
3. Tell me: "Review my CV" or "Tailor my CV for [job title] at [company]"
4. I'll guide you through the process!

**Common commands:**
- `"Polish my CV"` → General review and improvements
- `"Tailor my CV for this job: [URL]"` → Job-specific optimization
- `"Make my CV ATS-friendly"` → Check and fix ATS issues
- `"Help me rewrite this bullet point: [paste text]"` → Improve specific achievement
- `"Create a tech industry version of my CV"` → Industry-specific variant

---

**Ready to polish your CV?** Let me know when you'd like to start! 🚀
