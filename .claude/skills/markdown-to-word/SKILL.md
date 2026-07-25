---
name: markdown-to-word
description: Convert a markdown file to a professionally styled Word document
disable-model-invocation: true
argument-hint: [file-path]
---

# Markdown to Word Converter

Convert a markdown file (like a CV or report) to a professionally styled Word document (.docx) using the provided Python script.

## Workflow

### 1. Identify Target File
Identify the markdown file to be converted, typically passed as **$ARGUMENTS**.

### 2. Run the Conversion Script
The script takes the markdown path as an argument and writes the `.docx`
alongside it:

```powershell
python scripts/convert_cv.py <path-to-markdown-file>
```

### 3. Track Results
- ✅ Success: Verify the output `.docx` file has been generated successfully.
- ❌ Failure: Note any execution errors from the Python script.

### 4. Verify nothing was dropped
The converter is **section-aware**: it styles content based on which `##`
section it sits under. Always sanity-check that the paragraph count and the
section list in the `.docx` match the source markdown — a malformed line is
skipped rather than reported.

## Supported markdown constructs

| Markdown | Rendered as |
|---|---|
| `# Name` | 18pt bold, centred, `#1A365D` |
| `**Tagline**` (header, no email/link) | 11pt bold, centred, `#2C5F8A` |
| Header line containing an email or link | 9.5pt contact line, centred, hyperlinked |
| `## SECTION` | 12pt bold `#1A365D` + bottom border |
| `### Company \| Location` | 10.5pt bold `#111111` |
| `**Role \| Dates**` | 10pt bold `#555555` |
| Plain line under a role | 9.5pt italic `#555555` role brief |
| `` `Label`  content `` *or* `**Label:** content` | Bullet with bold label prefix |
| `**Category**` (skills) | 10pt bold `#111111` subheader |
| `- item` | 9.5pt `#333333` bullet |
| `*italic lead-in*` | 9.5pt italic `#555555` |
| `<div>` / raw HTML block tags | Skipped (GitHub-rendering hints only) |

Sections named PROFILE / SKILLS / EXPERIENCE / EDUCATION / HIGHLIGHTS get
bespoke treatment; **any other section** falls through to a generic renderer
using the same visual vocabulary, so a new section is never silently dropped.

Keep the whole contact line on **one line** in the markdown — a newline inside
a `[text](url)` link breaks it into literal markdown in the output.

## Requirements
- Python 3.8+
- `python-docx` package

## Output
- The Word document is generated in the target directory with a `.docx` extension.
- The script preserves margins, bullet points, headers, bold text, and clickable hyperlinks.

## Related
To produce a **PDF** of a CV, do not convert the markdown to PDF directly — use
the `generate-pdf` skill's `--cv` mode, which calls this script and then renders
the resulting `.docx` via LibreOffice. That is the pipeline behind the reference
CV PDFs, and it keeps the `.docx` and `.pdf` in sync.
