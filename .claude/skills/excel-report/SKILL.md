---
name: excel-report
description: Generate a structured markdown summary report from a CSV or Excel file. Use this skill whenever a user provides a data file (.csv, .xlsx, .xls) and asks for a summary, report, overview, analysis, or wants to understand what's in the data. Also use when someone says things like "what's in this spreadsheet", "summarize this data", "give me a report on this file", or "break down this CSV for me".
---

# Excel Report Generator

Produce a clear, structured markdown report from any tabular data file (CSV, XLSX, XLS).

## Process

### 1. Load the Data

Read the file using pandas:

```python
import pandas as pd

# For CSV
df = pd.read_csv("path/to/file.csv")

# For Excel
df = pd.read_excel("path/to/file.xlsx")
```

If the file fails to parse (encoding issues, malformed rows), try common fallbacks:
- `encoding='latin-1'` for CSV
- `sheet_name=0` to grab just the first sheet for multi-sheet Excel files

Mention in the report if only a subset of sheets was analyzed.

### 2. Profile the Data

Gather these basic statistics — they form the backbone of the report:

- **Shape**: row count, column count
- **Column types**: which columns are numeric, categorical, datetime, or text
- **Missing values**: count and percentage per column (flag any column over 20% missing)
- **Numeric summaries**: min, max, mean, median, standard deviation for each numeric column
- **Categorical summaries**: unique value count, top 3-5 most frequent values for each categorical column
- **Outliers**: for numeric columns, flag values beyond 1.5x the interquartile range

### 3. Identify Key Findings

Look at the profiling results and call out anything interesting:

- Columns with many missing values (data quality concern)
- Numeric columns with extreme outliers or high variance
- Categorical columns dominated by a single value (low information)
- Obvious patterns (e.g., a column that looks like an ID vs. one that looks like a measurement)

The goal is to give someone who has never seen this data a quick sense of what's notable — think of it like a first-pass data quality check combined with a high-level summary.

### 4. Write the Report

Use this exact template structure:

```markdown
# Data Report: [Filename]

## Executive Summary
A 2-3 sentence overview: what the data appears to represent, its size, and the
single most notable finding.

## Data Overview
| Property | Value |
|----------|-------|
| Rows     | X     |
| Columns  | Y     |
| File type| CSV/XLSX |

### Column Descriptions
A table listing each column, its detected type, non-null count, and a brief
description of what it appears to contain.

## Key Findings
Bullet points covering:
- Notable statistics (means, distributions)
- Data quality issues (missing values, duplicates)
- Outliers with specific values cited
- Dominant categories or patterns

## Recommendations
Practical next steps based on the findings — things like:
- "Column X has 35% missing values — consider imputation or exclusion"
- "The 'Status' column has only 2 unique values — may work well as a filter"
- "Revenue column has 3 outliers above $1M — verify these are real"
```

### 5. Save and Display

1. Save the report to `output/reports/[filename]-report.md`
2. Display the full report in the conversation

## Tips

- Keep the language plain and jargon-free — the reader may not be technical
- Cite specific numbers rather than vague statements ("mean of 42.3" not "the average is moderate")
- If the dataset is very large (>100k rows), note that the analysis covers the full dataset but the report focuses on the most relevant patterns
- For Excel files with multiple sheets, analyze the first sheet by default and mention the others exist
