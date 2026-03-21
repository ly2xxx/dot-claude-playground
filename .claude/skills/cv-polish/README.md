# CV Polish - Production-Ready CV Optimization Skill

**A comprehensive Claude Code skill for polishing, tailoring, and optimizing CVs/resumes for job applications.**

---

## 🎯 What This Skill Does

Helps you create compelling, ATS-optimized CVs that get you interviews. Covers:

- ✅ **General Polish:** Structure, language, achievement quality
- ✅ **Job-Specific Tailoring:** Match CV to job requirements
- ✅ **ATS Optimization:** Pass Applicant Tracking Systems
- ✅ **Industry-Specific Guidance:** Tech, finance, consulting, startup, etc.
- ✅ **Achievement Strengthening:** Transform weak bullets into powerful accomplishments
- ✅ **Version Management:** Maintain multiple tailored versions

---

## 🚀 Quick Start

### 1. Install the Skill

**For Claude Code (CLI):**
```bash
# Copy this folder to your .claude/skills/ directory
cp -r cv-polish ~/.claude/skills/
```

**For claude.ai (Web):**
1. ZIP this folder (make sure `cv-polish/` is at root, not contents directly)
2. Go to Settings → Customize → Skills
3. Upload the ZIP file

---

### 2. Add Your CV

Place your current CV in the `assets/` folder:

```bash
# Example
assets/
└── CV_Yang_Li_Master_2026.docx
```

---

### 3. Start Using

**Example commands:**

```
"Review my CV and suggest improvements"

"Tailor my CV for this job: https://linkedin.com/jobs/12345"

"Make my CV ATS-friendly"

"Help me rewrite this bullet point: Managed team projects"

"Create a tech industry version of my CV"
```

---

## 📁 Skill Structure

```
cv-polish/
├── SKILL.md                          # Main skill logic (YAML + instructions)
├── README.md                         # This file
├── scripts/
│   └── job_scraper.py               # Extract job requirements from URLs
├── references/
│   ├── achievement-formulas.md      # STAR/CAR/PAR/XYZ frameworks
│   ├── ats-optimization.md          # ATS best practices
│   └── industry-guides/
│       └── tech.md                  # Tech/software engineering guidance
└── assets/
    ├── [Your CV files go here]
    ├── support-materials/           # Photos, videos, portfolio samples
    └── CV_CHANGELOG.md              # Version history
```

---

## 🔧 Scripts

### Job Scraper

**Extract job requirements from web pages:**

```bash
python scripts/job_scraper.py <URL>
```

**Supported sites:**
- Indeed
- Company career pages
- Generic job postings

**Note:** LinkedIn requires authentication (recommend copy-paste instead)

**Install dependencies:**
```bash
pip install requests beautifulsoup4
```

---

## 📚 Reference Guides

### Achievement Formulas (`references/achievement-formulas.md`)

Learn to write powerful bullet points using:
- **STAR:** Situation → Task → Action → Result
- **CAR:** Challenge → Action → Result  
- **PAR:** Problem → Action → Result
- **XYZ:** Accomplished [X] as measured by [Y], by doing [Z] (Google's formula)

Includes 50+ before/after examples across industries.

---

### ATS Optimization (`references/ats-optimization.md`)

Complete guide to passing Applicant Tracking Systems:
- Formatting dos and don'ts
- File format recommendations
- Keyword optimization strategies
- Section header standards
- Testing methods

**Quick test:** Copy-paste your CV into plain text editor. If it's gibberish, ATS will fail.

---

### Industry Guides (`references/industry-guides/`)

Loaded on-demand when you target specific industries:
- **Tech/Software:** Scale, impact, GitHub, tech stack
- **Finance:** (Coming soon) P&L, regulations, certifications
- **Consulting:** (Coming soon) Frameworks, client impact
- **Startup:** (Coming soon) Ownership, scrappiness, equity

---

## 💡 Usage Examples

### Example 1: General Polish

**You say:**
> "Can you review my CV? It's in the assets folder called CV_Yang_Li_2026.docx"

**Skill does:**
1. Reads your CV
2. Analyzes structure, language, achievements
3. Identifies weak bullet points
4. Suggests specific improvements with before/after examples
5. Checks ATS compatibility

---

### Example 2: Job-Specific Tailoring

**You say:**
> "I want to apply for this role: https://example.com/careers/senior-engineer. Tailor my CV."

**Skill does:**
1. Runs `job_scraper.py` to extract requirements
2. Maps your experience to job requirements
3. Identifies gaps and strengths
4. Reorders/emphasizes relevant achievements
5. Adds missing keywords naturally
6. Generates tailored version

---

### Example 3: ATS Check

**You say:**
> "Is my CV ATS-friendly?"

**Skill does:**
1. Checks for ATS red flags (tables, graphics, text boxes)
2. Verifies standard section headers
3. Tests file format compatibility
4. Analyzes keyword density
5. Provides specific fixes

---

### Example 4: Achievement Strengthening

**You say:**
> "Help me improve this bullet: Managed team and completed projects on time"

**Skill does:**
1. Asks discovery questions (team size? what projects? outcomes?)
2. Applies STAR/CAR/PAR framework
3. Quantifies the achievement
4. Suggests: "Led cross-functional team of 8 (4 engineers, 3 designers, 1 PM) delivering 5 major features across 3 product releases, achieving 95% on-time delivery rate and reducing average sprint velocity variability by 30%"

---

## 🎓 Skill Design Principles

This skill follows production-ready patterns from: [**How to Build a Production-Ready Claude Code Skill**](https://towardsdatascience.com/how-to-build-a-production-ready-claude-code-skill/)

### Progressive Disclosure
- Metadata (name/description) always in context
- SKILL.md body loaded when triggered
- References loaded on-demand (industry guides, formulas)

### Deterministic Processing
- `job_scraper.py` handles web scraping
- Future: `cv_analyzer.py` for ATS checks

### Realistic Use Cases
- Designed around how people actually ask for CV help
- Messy, casual prompts ("yo can u look at my resume?")
- Not just clean, polished requests

---

## 🛠️ Extending This Skill

### Add More Industry Guides

Create new files in `references/industry-guides/`:
- `finance.md`
- `consulting.md`
- `healthcare.md`
- `academia.md`

Follow the template from `tech.md`.

---

### Improve Job Scraper

Enhance `scripts/job_scraper.py`:
- Add more site-specific parsers (Glassdoor, Monster, etc.)
- Improve keyword extraction (use spaCy or similar)
- Add sentiment analysis (company culture insights)

---

### Add CV Analyzer Script

Create `scripts/cv_analyzer.py`:
- Parse .docx files
- Check ATS compatibility
- Analyze keyword density
- Generate match scores

---

## 🔒 Privacy & Security

### Your CV is Private

- The `assets/` folder is in `.gitignore`
- CV files stay local on your machine
- Only you and Claude (running locally) see your CV

### Safe to Share (This Skill)

You can share this skill folder with others. Just:
1. Remove your personal CV files from `assets/`
2. ZIP the folder
3. Share!

Others get the skill logic, guides, and scripts - not your personal documents.

---

## 📊 Success Metrics

A well-polished CV should achieve:
- [ ] 80%+ achievements quantified
- [ ] No weak action verbs ("responsible for", "helped with")
- [ ] All ATS red flags eliminated
- [ ] 70%+ keyword match to target job (use jobscan.co to verify)
- [ ] Interview request rate >10% (industry standard: 2-5%)

---

## 🆘 Troubleshooting

### "Skill didn't trigger"

**Check your prompt includes keywords:**
- CV, resume, job application, polish, review, tailor, optimize
- Or upload a .docx/.pdf file (triggers automatically)

**Try explicit:** "Use the cv-polish skill to review my resume"

---

### "Job scraper failed"

**LinkedIn URLs don't work:**
- LinkedIn requires authentication
- Solution: Copy-paste job description directly

**Other sites:**
- Install dependencies: `pip install requests beautifulsoup4`
- Some sites block scrapers - copy-paste as fallback

---

### "Can't find my CV file"

**Skill looks in these locations:**
1. `assets/` directory in skill folder
2. Path you specify: "My CV is at C:\Documents\CV.docx"
3. Recently uploaded files

**Make sure to specify exact filename if multiple CVs exist**

---

## 📞 Support & Feedback

Found a bug? Want a feature?
- Open an issue (if this was on GitHub)
- Or just tell Claude: "The cv-polish skill should also do [X]"

---

## 📖 Further Reading

- [How to Build a Production-Ready Claude Code Skill](https://towardsdatascience.com/how-to-build-a-production-ready-claude-code-skill/) - Skill design principles
- [Google's Resume Guide](https://www.google.com/about/careers/applications/how-we-hire/) - XYZ formula
- [Jobscan](https://www.jobscan.co/) - ATS testing tool

---

## 🎉 Ready to Get Started?

1. **Add your CV** to `assets/` folder
2. **Tell Claude:** "Review my CV using the cv-polish skill"
3. **Follow the guidance** and iterate!

Good luck with your job search! 🚀
