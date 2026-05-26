---
name: invoice-tracker
description: >-
  Categorize, audit and reconcile recurring service-charge / property-factor /
  managing-agent invoices and build a tax-ready cost-tracking spreadsheet. Use
  when the user has a set of periodic invoices (usually PDFs) from a property
  factor, managing agent, landlord, or service provider and wants to: break down
  cost per source/vendor and per category for each invoice, compare the current
  period against prior periods to flag anomalies (newly added or missing
  vendors, abnormally high/low amounts, charges dated outside the invoice
  period, stale service periods, duplicate lines, credits), reconcile each
  invoice to its stated total, and produce a spreadsheet for year-end tax
  returns. Triggers include: "analyze my quarterly invoices", "factor invoice",
  "service charge invoice", "common charge", "track these costs for tax",
  "highlight invoice anomalies", "categorize cost per vendor". Also triggers
  whenever the user provides a single new invoice PDF to extend an existing
  tracker — e.g. "here's this quarter's invoice", "add this invoice", "check my
  latest factor invoice" — in which case append it to the CSVs and re-run.
---

# Invoice Tracker

Turn a stack of repeating invoices into (1) a clean, categorized cost-tracking
spreadsheet for tax returns and (2) a point-in-time anomaly report for **each**
invoice, comparing it against the invoices dated before it.

## Division of labour (important)

- **Claude (you) reads the invoices.** PDF/image table extraction is *not*
  reliably deterministic, so you transcribe each invoice's line items into two
  flat CSVs. This is the only judgement step.
- **The script does everything deterministic.** `scripts/build_tracker.py`
  reads the CSVs and performs all calculation, categorization, anomaly
  detection, reconciliation and document writing. Never compute totals or
  "eyeball" anomalies by hand — let the script do it so results are repeatable.

## Workflow (first run / batch of invoices)

1. **Locate the invoices.** Ask the user where they are if not obvious. Pick a
   working folder for outputs (e.g. an `output/` folder next to the invoices).
   **Ignore anything under an `adhoc/` folder** (e.g. `assets/adhoc/`): those are
   one-off / non-quarterly documents the user keeps on purpose — never read them
   into the CSVs or count them toward the tracker.

2. **Read every invoice** with the Read tool. For each one capture: invoice
   number, invoice date, the charge period (From / To), and every charge line
   (category section header, date of charge, vendor/supplier, description, the
   full building amount, the apportionment share, and the owner's cost). Also
   capture the footer Sub-total / VAT / Invoice total for reconciliation.

3. **Write two CSVs** into the working folder using the schema below.
   `your_cost` is the figure that flows into the tax spreadsheet (the owner's
   apportioned, VAT-inclusive amount actually charged). Strip thousands
   separators from numbers; keep dates as `DD/MM/YYYY`; quote any field
   containing a comma.

4. **Run the analyzer:**
   ```
   python scripts/build_tracker.py --input-dir <working-folder>
   ```
   It writes `cost_tracker.xlsx` plus one `anomaly_report_<invoice_no>.md` per
   invoice into the same folder (override with `--output-dir`). Each invoice is
   analysed as its own "current" period, compared only against the invoices
   dated before it. Requires `openpyxl` (`pip install openpyxl`).

5. **Confirm reconciliation.** Each report's Reconciliation line (and the
   Summary sheet) must say it reconciles (line-items sum == stated invoice
   total, within £0.01). If one says DOES NOT RECONCILE you mis-transcribed a
   line — fix the CSV and re-run before reporting results.

6. **Summarize for the user.** Lead with the newest invoice's report (high
   severity findings first), explain the tax-year totals, and point them to
   `cost_tracker.xlsx` and the per-invoice reports.

## Adding a new invoice (the usual repeat trigger)

When the user later drops in a **single new invoice PDF** (the common case once a
tracker exists), do not start over:

1. **Find the existing CSVs** (`line_items.csv`, `invoices.csv`) in the working
   folder. If none exist, fall back to the first-run workflow above.
2. **Read the new PDF** and extract its rows exactly as in steps 2–3.
3. **Append** the new line rows to `line_items.csv` and the new footer row to
   `invoices.csv`. Skip the append if that `invoice_no` is already present
   (idempotent — never duplicate an invoice).
4. **Re-run** `build_tracker.py`. It re-derives chronological order from the
   period dates, so the new invoice becomes the current period automatically and
   gets its own `anomaly_report_<invoice_no>.md`; earlier reports are unchanged.
5. **Report** the new invoice's findings and the refreshed tax-year totals.

## CSV schemas

`invoices.csv` — one row per invoice (footer/header facts):

```
invoice_no,invoice_date,period_from,period_to,subtotal,vat,invoice_total,balance_bf,balance
```

`line_items.csv` — one row per charge line:

```
invoice_no,invoice_date,period_from,period_to,category,charge_date,vendor,description,total_amount,share,your_cost
```

- `category` = the invoice's own section header (Cleaning, Electricity, Repairs,
  Insurance, Management Fee, etc.). When line items continue onto a new page
  under no new header, keep the previous header.
- `total_amount` = full building charge; `share` = apportionment text like
  `1/35` or `1/1`; `your_cost` = the owner's column. Keep credits negative.

## Outputs

`cost_tracker.xlsx` sheets:
- **Summary** — per-invoice totals, reconciliation status, totals by tax year.
- **Line Items** — every line with a Tax year column, parsed service-period
  dates, and an anomaly Flags column; credits shaded green, flagged rows amber.
  Auto-filtered for slicing by category/vendor/tax year.
- **By Category** / **By Vendor** — cost matrices (rows × each invoice + total).
- **By Tax Year** — category × tax-year totals; the sheet to read off for a
  return.
- **Anomalies** — every finding across all invoices, with severity, type and detail.

`anomaly_report_<invoice_no>.md` — one self-contained report per invoice, each
with that invoice's reconciliation check, cost-by-category and cost-by-vendor
tables, and its anomalies (grouped by type, high severity first).

## Anomaly checks (all in the script)

Every per-line finding (charge date, stale service period, duplicate, cross-invoice duplicate) includes the owner's charged amount (`£your_cost`) in the detail string so that items can be located quickly on the original invoice.

- **Reconciliation mismatch** (high) — line items don't sum to the stated total.
- **Charge date outside invoice period** — date of charge is before/after the
  period; severity scales with the gap (>180d high, >31d medium, else low).
- **Stale service period** — the dd/mm/yyyy–dd/mm/yyyy range in the description
  ends before the quarter begins (e.g. a long-delayed catch-up bill).
- **Possible duplicate line** (high) — same vendor+description+amount+date twice
  in one invoice.
- **New vendor** / **Dropped vendor** — vendor appears for the first time, or a
  vendor seen in ≥2 prior periods is now absent (one-off contractors ignored).
- **Recurring item missing** — a line present in *every* prior period (matched
  by description signature, category-agnostic) is absent now.
- **Abnormal category / vendor total** — current vs prior-period mean outside
  the ratio band and above the materiality threshold.
- **Credit / negative line** — informational list of discounts/reversals.
- **Cross-invoice duplicate charge** (high/medium) — same vendor found charging for a substantially overlapping service period in both the current invoice and a prior one; high when amounts also match, medium otherwise. Only raised when the overlap exceeds 50 % of the shorter service period — consecutive quarterly contracts whose billing windows share a few days at the boundary are ignored as normal scheduling, not duplicates. Within the same invoice, "Possible duplicate line (same invoice)" is also extended to catch same vendor + same service period + same amount appearing under different description wording (e.g. a spurious "x2" suffix).

In each invoice's report that invoice is the "current" period, and drift checks
(new/dropped vendor, recurring-item-missing, abnormal totals) compare it only
against invoices dated before it. This point-in-time view means an older
invoice's report never changes when later invoices are added.

## Tuning (flags)

- `--tax-start-day` / `--tax-start-month` — tax-year boundary (default 6 April,
  UK). Set to `1` / `1` for a calendar year.
- `--high-ratio` (default 1.5) / `--low-ratio` (default 0.5) — value-anomaly
  band.
- `--material` (default 15) — minimum £ swing before a value anomaly is raised.

## Notes & assumptions

- Costs are tracked on `your_cost` (gross, VAT-inclusive) — what a
  non-VAT-registered owner claims as an expense.
- Tax-year assignment uses the **charge date** (accruals basis). A landlord on
  the cash basis can instead group by invoice/payment date using the Line Items
  sheet's other date columns.
- The script never invents figures; it only aggregates and compares the CSVs.
  Accuracy depends on faithful transcription in step 2.
- **Always skip files under any `adhoc/` folder** (e.g. `assets/adhoc/`). These
  are deliberately kept out of scope — do not extract, count, or reconcile them,
  whether on a first run or when adding a new invoice.
- `assets/` holds a worked example — four quarterly Newton Property "Common
  Charge" invoice PDFs; running the skill on them produces the files in
  `output/`: `line_items.csv`, `invoices.csv`, `cost_tracker.xlsx`, and one
  `anomaly_report_<invoice_no>.md` per invoice.
