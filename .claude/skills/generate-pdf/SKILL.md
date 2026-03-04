---
name: generate-pdf
description: Generate a professional PDF from a markdown file. Use when converting .md files to .pdf format or when user requests PDF generation.
disable-model-invocation: true
argument-hint: [filename.md]
---

# PDF Generator

Convert $ARGUMENTS to a professional PDF document.

## Process

1. **Read the markdown file**: $ARGUMENTS
2. **Convert to styled HTML**:
   - Parse markdown with proper extensions (tables, code blocks, TOC)
   - Apply professional styling
3. **Generate PDF**:
   - Run conversion script: `python scripts/convert.py "$ARGUMENTS"`
   - Output to `output/pdfs/[filename].pdf`
4. **Report location** of generated PDF

## Styling Applied

- **Fonts**: Georgia (body), Helvetica (headings)
- **Margins**: 1 inch all around
- **Page numbers**: Bottom center
- **Code blocks**: Syntax highlighting with left border
- **Tables**: Professional borders and spacing

## Output

PDFs are saved to `output/pdfs/` directory with the same base filename as the input markdown.

**Example:**
```
/generate-pdf docs/guide.md
→ Creates: output/pdfs/guide.pdf
```

## Requirements

The conversion script requires:
- Python 3.8+
- `markdown` package (for MD parsing)
- `weasyprint` package (for PDF generation)

Install with:
```bash
pip install markdown weasyprint
```
