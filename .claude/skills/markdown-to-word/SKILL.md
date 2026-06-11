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
Invoke the Python script to perform the conversion:

```powershell
python scripts/convert_cv.py
```
*(Note: If you need to run this on an arbitrary file, you may need to update the script to accept a file-path argument, as it currently has fixed paths configured).*

### 3. Track Results
- ✅ Success: Verify the output `.docx` file has been generated successfully.
- ❌ Failure: Note any execution errors from the Python script.

## Requirements
- Python 3.8+
- `python-docx` package

## Output
- The Word document is generated in the target directory with a `.docx` extension.
- The script preserves margins, bullet points, headers, bold text, and clickable hyperlinks.
