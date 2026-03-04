---
name: markdown-to-pdf
description: Batch convert all markdown files in a directory to professional PDFs
disable-model-invocation: true
argument-hint: [directory-path]
---

# Markdown to PDF Batch Converter

Convert all markdown files in **$ARGUMENTS** to professionally styled PDFs.

## Workflow

### 1. Discover Markdown Files

List all `.md` files in the target directory.

**Exclude these special files:**
- `CLAUDE.md` (workspace memory)
- `AGENTS.md` (agent configuration)
- `MEMORY.md` (long-term memory)
- `SOUL.md` (persona configuration)
- `USER.md` (user profile)
- `TOOLS.md` (tool notes)
- `HEARTBEAT.md` (heartbeat configuration)
- `BOOTSTRAP.md` (bootstrap instructions)
- `SKILL.md` (skill definitions)
- `README.md` (documentation - optional, can be included if requested)

### 2. Convert Each File

For each discovered markdown file:

1. **Invoke the PDF generator:**
   ```
   /generate-pdf [path/to/file.md]
   ```

2. **Track results:**
   - ✅ Success: File path and output location
   - ❌ Failure: File path and error message

3. **Continue on errors** - Don't stop the batch if one file fails

### 3. Generate Summary Report

After processing all files, provide a summary:

```
📊 Conversion Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Successfully converted: X files
❌ Failed: Y files
📁 Output directory: output/pdfs/

Successful conversions:
  • guide.md → output/pdfs/guide.pdf
  • tutorial.md → output/pdfs/tutorial.pdf
  
Failed conversions:
  • broken.md - Invalid markdown syntax
```

## Usage Examples

### Convert all files in a directory
```
/markdown-to-pdf ./docs
```

### Convert files in current directory
```
/markdown-to-pdf .
```

### Convert files in a nested directory
```
/markdown-to-pdf ./projects/my-project/documentation
```

## Output

- All PDFs are saved to `output/pdfs/` directory
- Filenames match the source markdown files (e.g., `guide.md` → `guide.pdf`)
- Existing PDFs with the same name are overwritten

## Requirements

This skill requires the `generate-pdf` skill to be available.

The `generate-pdf` skill in turn requires:
- Python 3.8+
- `markdown` package
- `weasyprint` package

## Tips

**Before running:**
- Ensure all markdown files are well-formed
- Check that file paths don't contain special characters
- Large batches (50+ files) may take several minutes

**After running:**
- Check the summary for any failed conversions
- Review output PDFs in `output/pdfs/`
- Failed files can be fixed and re-run individually with `/generate-pdf`
