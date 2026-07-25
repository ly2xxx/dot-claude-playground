---
name: generate-pdf
description: Generate a professional PDF from a markdown file. Use when converting .md files to .pdf format or when user requests PDF generation.
argument-hint: [filename.md]
---

# PDF Generator

Convert $ARGUMENTS to a professional PDF document.

## ⚠️ Pick the right pipeline first

| Input | Use | Why |
|---|---|---|
| **A CV / résumé** | `--cv` | Produces the house CV style |
| Docs, guides, notes, cheatsheets | default | General document styling |

**Do not use the default pipeline for a CV.** It has no notion of CV sections,
justifies body text, renders section headings at document scale, and turns
`` `backtick` `` labels into red code boxes. The result looks visibly worse than
the reference CVs.

## Process — CV (`--cv`)

Pipeline: **markdown → .docx → .pdf**

1. `python scripts/convert.py --cv "$ARGUMENTS"`
   - Step 1 delegates to the sibling **markdown-to-word** skill
     (`../markdown-to-word/scripts/convert_cv.py`) for CV-aware .docx styling
   - Step 2 converts that .docx to PDF with headless LibreOffice
2. **Both** `.docx` and `.pdf` are written **beside the source `.md`**
3. Report both locations

This is the pipeline that produced the reference CVs — verify by checking their
metadata (`Author: python-docx`, `Producer: LibreOffice`). Any CV PDF whose
producer reads `xhtml2pdf` was built the wrong way.

Because the .docx is an intermediate artifact, `--cv` keeps the Word and PDF
versions in sync automatically — never generate them by separate routes.

## Process — general documents (default)

1. **Read the markdown file**: $ARGUMENTS
2. **Convert to styled HTML**: markdown extensions (tables, code blocks, TOC) + professional CSS
3. **Generate PDF**: `python scripts/convert.py "$ARGUMENTS"` → `output/pdfs/[filename].pdf`
4. **Report location**

### Styling applied (default pipeline only)

- **Fonts**: Georgia (body), Helvetica (headings)
- **Margins**: 1 inch all around
- **Code blocks**: Syntax highlighting with left border
- **Tables**: Professional borders and spacing

## Examples

```
/generate-pdf docs/guide.md
→ Creates: output/pdfs/guide.pdf

/generate-pdf --cv assets/YL-CV-2026-AI.md
→ Creates: assets/YL-CV-2026-AI.docx  and  assets/YL-CV-2026-AI.pdf
```

## Requirements

- Python 3.8+
- `markdown` package (MD parsing)
- `xhtml2pdf` package (default pipeline PDF rendering — **not** weasyprint;
  weasyprint needs native GTK/Pango/Cairo libraries that are absent on Windows
  and fails at runtime with `OSError: cannot load library 'libgobject-2.0-0'`)
- For `--cv`: `python-docx` **and** LibreOffice installed

```bash
pip install markdown xhtml2pdf python-docx
```
