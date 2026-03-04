---
name: data-analyzer
description: Analyze financial datasets using standard accounting methods. Use when user uploads a CSV and says "analyze financial data" or "run audit".
version: 1.0
license: MIT
---

# Data Analyzer

## Instructions
1.  **Ingest Data**: Read the CSV file provided by the user.
2.  **Load Glossary**: Read `resources/financial_glossary.csv` to understand specific term definitions if columns are ambiguous.
3.  **Execute Analysis**: Run the analysis script on the user's file:
    ```bash
    python scripts/analyze_data.py --input [USER_FILE.csv]
    ```
4.  **Report**: Summarize the output from the script and highlight any anomalies found.