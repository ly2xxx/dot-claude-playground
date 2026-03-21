# Installation Guide - CV Polish Skill

**Quick setup for Claude Code or claude.ai**

---

## Option 1: Claude Code (CLI) - Recommended

### Step 1: Copy Skill to .claude/skills/

```powershell
# Windows PowerShell
Copy-Item -Recurse "C:\code\claude-notes\skill\cv-polish" -Destination "$HOME\.claude\skills\cv-polish"
```

```bash
# Linux/Mac
cp -r ~/code/claude-notes/skill/cv-polish ~/.claude/skills/cv-polish
```

---

### Step 2: Verify Installation

```bash
# List installed skills
ls ~/.claude/skills/

# You should see: cv-polish/
```

---

### Step 3: Add Your CV

```powershell
# Navigate to assets folder
cd ~/.claude/skills/cv-polish/assets/

# Copy your CV here
copy "C:\path\to\your\CV.docx" .
```

---

### Step 4: Test the Skill

Start Claude Code and try:

```
"Review my CV using the cv-polish skill"
```

Or simply:

```
"Polish my CV"
```

Claude should automatically detect and load the skill.

---

## Option 2: claude.ai (Web)

### Step 1: Create ZIP File

**Important:** The ZIP must contain the `cv-polish/` folder at root, not just its contents.

```powershell
# Windows PowerShell
Compress-Archive -Path "C:\code\claude-notes\skill\cv-polish" -DestinationPath "C:\Downloads\cv-polish.zip"
```

```bash
# Linux/Mac
cd ~/code/claude-notes/skill/
zip -r ~/Downloads/cv-polish.zip cv-polish/
```

---

### Step 2: Upload to claude.ai

1. Go to https://claude.ai
2. Click Settings (gear icon)
3. Select **Customize** → **Skills**
4. Click **Upload Skill**
5. Select `cv-polish.zip`
6. Wait for confirmation

---

### Step 3: Add Your CV

**Option A: Upload in Chat**
- Start a conversation
- Attach your CV file
- Say: "Review my CV"

**Option B: Google Drive/Dropbox**
- Share link to CV
- Say: "Review my CV at [link]"

---

## Installing Script Dependencies (Optional)

The `job_scraper.py` script requires additional Python libraries.

### Install with pip:

```bash
pip install requests beautifulsoup4
```

### Or use requirements file:

```bash
# Create requirements.txt
echo "requests>=2.28.0" > requirements.txt
echo "beautifulsoup4>=4.11.0" >> requirements.txt

# Install
pip install -r requirements.txt
```

**Note:** Skill works without these dependencies. You just won't be able to scrape job URLs (can paste descriptions instead).

---

## Updating the Skill

### Claude Code (CLI):

```powershell
# Replace with updated version
Remove-Item -Recurse "$HOME\.claude\skills\cv-polish"
Copy-Item -Recurse "C:\code\claude-notes\skill\cv-polish" -Destination "$HOME\.claude\skills\cv-polish"
```

---

### claude.ai (Web):

1. Delete old skill: Settings → Skills → Delete "cv-polish"
2. Create new ZIP with updated files
3. Upload new ZIP

**Important:** Bump the `version` field in SKILL.md when updating!

---

## Troubleshooting

### "Skill not found" or "Skill didn't trigger"

**Check folder structure:**
```
~/.claude/skills/cv-polish/
├── SKILL.md  ← This must exist at this path
├── scripts/
├── references/
└── assets/
```

**Try explicit trigger:**
```
"Use the cv-polish skill to review my resume"
```

---

### "Can't import requests in job_scraper.py"

Install dependencies:
```bash
pip install requests beautifulsoup4
```

Or skip URL scraping (paste job descriptions directly).

---

### "ZIP upload failed"

Make sure ZIP contains `cv-polish/` folder, not just contents:

**❌ Wrong structure:**
```
cv-polish.zip
├── SKILL.md
├── README.md
└── scripts/
```

**✅ Correct structure:**
```
cv-polish.zip
└── cv-polish/
    ├── SKILL.md
    ├── README.md
    └── scripts/
```

---

## Verification Checklist

After installation:

- [ ] `SKILL.md` exists in correct location
- [ ] Your CV is in `assets/` folder (for local testing)
- [ ] Skill triggers when you say "polish my CV"
- [ ] Reference guides load when needed (try "show me STAR formula")
- [ ] Scripts execute (if dependencies installed)

---

## Uninstalling

### Claude Code:
```powershell
Remove-Item -Recurse "$HOME\.claude\skills\cv-polish"
```

### claude.ai:
Settings → Skills → Delete "cv-polish"

**Note:** Your personal CV files in `assets/` are not automatically backed up. Copy them elsewhere before uninstalling!

---

## Next Steps

✅ **Installation complete!**

Now try:
1. **"Review my CV"** - General polish
2. **"Make my CV ATS-friendly"** - Check formatting
3. **"Help me rewrite this bullet: [paste text]"** - Improve achievements

---

**Need help?** Check `README.md` for full usage guide and examples.
