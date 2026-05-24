# Invoice Tracker

A Claude Code skill that turns a stack of repeating service-charge / property-factor
invoices into a **tax-ready cost-tracking spreadsheet** plus a **point-in-time
anomaly report for each invoice**.

## What it does

- Categorises cost per source/vendor and per category for every invoice.
- Reconciles each invoice's line items to its stated total.
- Flags anomalies vs. earlier periods: new / dropped vendors, missing recurring
  items, abnormally high/low amounts, charges dated outside the invoice period,
  stale service periods, duplicate lines, and credits.
- Produces `cost_tracker.xlsx` (Summary, Line Items, By Category, By Vendor,
  By Tax Year, Anomalies) and one `anomaly_report_<invoice_no>.md` per invoice.

## How the work is split

- **Claude reads the PDFs** and transcribes each invoice into two CSVs
  (`line_items.csv`, `invoices.csv`) — the only judgement step.
- **`scripts/build_tracker.py` does the rest deterministically**: all
  calculation, anomaly detection, reconciliation and document writing.

## How to use it

Requirement: `pip install openpyxl`

**First run (a batch of invoices)** — just ask Claude, e.g.
> "Analyze my quarterly factor invoices in this folder and build a cost tracker."

Claude reads each PDF, writes the CSVs, then runs:

```bash
python scripts/build_tracker.py --input-dir <working-folder>
```

**Add a new invoice later** — drop the new PDF in and say:
> "Add this invoice" / "Here's this quarter's invoice."

Claude appends it to the existing CSVs (skipping it if already present) and
re-runs. The new invoice gets its own report; earlier reports don't change.

## Useful flags

| Flag | Default | Purpose |
|---|---|---|
| `--tax-start-day` / `--tax-start-month` | `6` / `4` | Tax-year boundary (UK 6 Apr). Use `1`/`1` for calendar year. |
| `--high-ratio` / `--low-ratio` | `1.5` / `0.5` | Value-anomaly band vs. prior-period average. |
| `--material` | `15` | Minimum £ swing before a value anomaly is raised. |
| `--output-dir` | input dir | Where to write outputs. |

## Notes

- Costs are tracked on `your_cost` (the owner's apportioned, VAT-inclusive
  amount). Tax-year assignment uses the **charge date** (accruals basis).
- Files under `assets/adhoc/` are **ignored** — keep one-off / non-quarterly
  documents there so they don't count toward the tracker.
- `assets/` holds a worked example (four Newton Property "Common Charge"
  invoices); `output/` shows what the skill produces.

See `SKILL.md` for the full schema, anomaly rules and step-by-step workflow.
