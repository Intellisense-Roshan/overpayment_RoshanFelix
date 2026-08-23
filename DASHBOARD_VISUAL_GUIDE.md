# DASHBOARD VISUAL GUIDE

This guide describes what you'll see in each section when you run the Streamlit dashboard.

---

## SECTION 1: HEADER

```
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║                 THE OVERPAYMENT SIGNAL                             ║
║          Explainable Investigation Prioritization                  ║
║                                                                    ║
║   ⚠️  Decision-support system — human investigation required.     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## SECTION 2: KEY METRICS (5 Cards in a Row)

```
┌─────────────┬──────────────┬──────────────┬───────────────┬────────────┐
│   4,200     │   24,756     │     138      │      20       │ $100,567.91│
│Total Cases  │Total Payments│Signal Cases  │Investigation │ Calculated │
│             │              │              │   Worklist    │ Financial  │
│             │              │              │               │Discrepancy │
└─────────────┴──────────────┴──────────────┴───────────────┴────────────┘
```

---

## SECTION 3: SIGNAL OVERVIEW

### Three Color-Coded Signal Cards

```
┌──────────────────┬──────────────────┬──────────────────┐
│  Post-Closure    │     Duplicate    │   Award Spike    │
│      60          │        46        │       32         │
│ Payments after   │Within-month      │Payments exceeding│
│ case closure     │duplicate disburse│authorized award  │
└──────────────────┴──────────────────┴──────────────────┘
```

### Pie Chart: Top-20 Signal Composition

```
                    ╔═══════════════════╗
              ╔═════╣  Award Spike      ║═════╗
              ║     ║   12 cases (60%)  ║     ║
              ║     ╚═══════════════════╝     ║
              ║                               ║
        ╔═════════════════╗           ╔═════════════════╗
        ║ Post-Closure    ║           ║   Duplicate     ║
        ║ 7 cases (35%)   ║           ║  1 case (5%)    ║
        ╚═════════════════╝           ╚═════════════════╝
```

---

## SECTION 4: INVESTIGATION WORKLIST

```
Top 20 Investigation Worklist

[ Interactive Table - Click row to select ]

Rank │ Case ID   │ Signal       │ Priority Score │ Fin. Discrepancy │ Status
─────┼───────────┼──────────────┼────────────────┼──────────────────┼───────────
1    │ C-31298   │ Award Spike  │ 99.63 / 100   │ $7,504.56        │ Active
2    │ C-32995   │ Award Spike  │ 91.46 / 100   │ $6,663.18        │ Active
3    │ C-33743   │ Award Spike  │ 87.50 / 100   │ $5,943.47        │ Active
4    │ C-34196   │ Post-Closure │ 87.18 / 100   │ $5,581.70        │ Closed
5    │ C-33263   │ Award Spike  │ 86.05 / 100   │ $6,919.42        │ Suspended
...  │ ...       │ ...          │ ...            │ ...               │ ...
20   │ C-34050   │ Award Spike  │ 71.30 / 100   │ $3,719.29        │ Active

[User selects a case by clicking on a row]
```

---

## SECTION 5: CASE DETAIL & EVIDENCE

### When User Selects Case #1 (C-31298):

```
Case ID: C-31298          │ Rank: #1           │ Priority Score: 99.63 / 100
─────────────────────────────────────────────────────────────────────────────
Primary Signal: Award Spike
Status: Active
Monthly Award: $746.45                    Total Financial Discrepancy: $7,504.56

This case is prioritized for human investigation based on observed transaction patterns. The system does not determine whether a payment was improper.

─────────────────────────────────────────────────────────────────────────────
WHY WAS THIS CASE SELECTED?
─────────────────────────────────────────────────────────────────────────────

Case C-31298 received 6 payments during the observation period, with 6 
exceeding twice the award relative to its recorded monthly award of $746.45. 
The largest payment was $2,211.51 (2.96x award), creating $7,504.56 in 
calculated financial discrepancy relative to the authorized award.

─────────────────────────────────────────────────────────────────────────────
KEY EVIDENCE POINTS
─────────────────────────────────────────────────────────────────────────────

• Authorized monthly award is $746.45.

• 6 of 6 observed payments exceeded 1.5x the authorized monthly award.

• Peak single-month payment was $2,211.51 in 2025-11 (2.96x the award, 
  Transaction ID: P-107667).

• Total cumulative excess above authorized award across all months is $7,504.56.

─────────────────────────────────────────────────────────────────────────────
TRANSACTION EVIDENCE
─────────────────────────────────────────────────────────────────────────────

┌─────────────────────┬──────────────────┬─────────────────────────────────┐
│ Payment Months      │ Payment Amounts  │ Transaction IDs                 │
├─────────────────────┼──────────────────┼─────────────────────────────────┤
│ 2025-07, 2025-08,   │ $2057.64,        │ P-107663, P-107664, P-107665,   │
│ 2025-09, 2025-10,   │ $1760.52,        │ P-107666, P-107667, P-107668    │
│ 2025-11, 2025-12    │ $2184.70, ...    │                                 │
└─────────────────────┴──────────────────┴─────────────────────────────────┘

─────────────────────────────────────────────────────────────────────────────
SIGNAL ANALYSIS: Award Spike
─────────────────────────────────────────────────────────────────────────────

Payments > 1.5× Award:   6
Payments > 2× Award:     6
Max Payment Ratio:       2.96×
```

---

## SECTION 6: FAIRNESS AUDIT

### Age Band Breakdown

```
AGE BAND ANALYSIS

Population % → Top-20 %
┌───────────────────────────────────────────────────────────────────┐
│ 18-29:   ████░░░░░░░░░░░░░░  16.7%  →  ██░░░░░░░░░░░░░░░░░░  5.0% │
│ 30-44:   █████████████████░░  26.5%  →  ████████████████████░░ 30.0%│
│ 45-59:   ████████████░░░░░░░  23.6%  →  ████████████░░░░░░░░░ 20.0%│
│ 60-74:   ███████████░░░░░░░░  20.8%  →  ████████████████████░░ 40.0%│
│ 75+:     ███████░░░░░░░░░░░░  12.4%  →  ██░░░░░░░░░░░░░░░░░░  5.0% │
└───────────────────────────────────────────────────────────────────┘

Detailed Fairness Table:
┌──────┬──────────────┬──────────────┬─────────────────┬───────────────────┐
│Group │ Population % │ Top-20 %     │ Selection Rate %│ Representation    │
├──────┼──────────────┼──────────────┼─────────────────┼───────────────────┤
│18-29 │ 16.7%        │ 5.0%         │ 0.14%           │ 0.30 (under-repr.)│
│30-44 │ 26.5%        │ 30.0%        │ 0.54%           │ 1.13 (balanced)   │
│45-59 │ 23.6%        │ 20.0%        │ 0.40%           │ 0.85 (under-repr.)│
│60-74 │ 20.8%        │ 40.0%        │ 0.92%           │ 1.92 (over-repr.) │
│75+   │ 12.4%        │ 5.0%         │ 0.19%           │ 0.40 (under-repr.)│
└──────┴──────────────┴──────────────┴─────────────────┴───────────────────┘
```

### All Dimensions (Scrollable)

- **AGE_BAND**: 5 groups analyzed
- **LANGUAGE_PREFERENCE**: 3 groups (English 70%, Spanish 20%, Other 10%)
- **DISTRICT**: 4 groups (Northgate over-represented, Weybridge under-represented)
- **TENURE**: 5 groups (Private tenancy over-represented, Owner-occupier under-represented)

**Key Note**: "Demographic attributes are NOT used in the investigation priority score."

---

## SECTION 7: GOVERNANCE & HUMAN DECISION BOUNDARY

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                   DECISION FLOW                                       ║
║                                                                       ║
║   System Analysis                                                     ║
║        ↓                                                               ║
║   Identifies payment anomalies                                        ║
║        ↓                                                               ║
║   Prioritizes cases by financial significance                         ║
║        ↓                                                               ║
║   Human Investigator                                                  ║
║        ↓                                                               ║
║   Reviews evidence and complete case records                          ║
║        ↓                                                               ║
║   Human determination of facts                                        ║
║        ↓                                                               ║
║   Administrative action (if appropriate)                              ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

─────────────────────────────────────────────────────────────────────────

CRITICAL LIMITATIONS

⚠️  This system does NOT:

• Determine fraud or improper payment
• Automatically suspend, terminate, reduce, or recover benefits
• Make final eligibility determinations
• Replace human investigator judgment
• Have access to case history or context beyond payment patterns
• Account for valid explanations or legitimate adjustments

─────────────────────────────────────────────────────────────────────────

WHO MAKES THE DECISION?

👤 Human investigator — with access to complete case records, applicant 
   statements, and administrative context — makes the determination 
   following established procedures.
```

---

## SECTION 8: FOOTER

```
════════════════════════════════════════════════════════════════════════

     The Overpayment Signal — Investigation prioritization, not 
                     automated adjudication.

════════════════════════════════════════════════════════════════════════
```

---

## INTERACTIVE FEATURES SHOWN

### Feature: Case Selection Dropdown

```
Select a case to view details:

▼ Rank 1: Case C-31298 (Award Spike)
  Rank 2: Case C-32995 (Award Spike)
  Rank 3: Case C-33743 (Award Spike)
  Rank 4: Case C-34196 (Post-Closure)
  ... [18 more options]
```

**When user selects a different case**: All evidence sections update to show new case data.

### Feature: Charts Hover Tooltips

Plotly charts show interactive tooltips when hovering:
- Signal pie chart: Shows signal type and case count
- Fairness bar charts: Shows dimension, group, population %, top-20 %, and ratio

### Feature: Responsive Design

Dashboard adapts to screen size:
- Desktop (1440px): Full width, 5-column metrics
- Laptop (1280px): Full width, optimal spacing
- Projector (1024px): Large text, clear layout

---

## DATA VALUES DISPLAYED

### From top20_worklist.csv:
- Rank, Case ID, Primary Signal
- Investigation Priority Score (0-100)
- Signal Financial Discrepancy ($)
- Status (Active/Closed/Suspended)
- Monthly Award ($)
- Payment statistics (count, amounts, ratios)
- Signal-specific fields

### From top20_explanations.csv:
- Plain-language summaries (pre-generated, not new)
- Evidence points (structured, not generated)
- Transaction IDs (exact, verifiable)
- Relevant months and amounts

### From fairness_summary.csv:
- Age band, Language preference, District, Tenure
- Population count & percentage
- Top-20 count & percentage
- Representation ratio
- Selection rate

---

## COLOR SCHEME

Professional, accessible palette:

- **Primary**: Dark Blue (#1f3864) — Headers, metric values, section titles
- **Accent 1**: Red (#d73027) — Post-Closure signal
- **Accent 2**: Orange (#fc8d59) — Duplicate signal
- **Accent 3**: Light Yellow (#fee090) — Award Spike signal
- **Background**: White (#ffffff) — Content cards
- **Text**: Dark Gray (#333) — Body text
- **Borders**: Light Gray (#e0e0e0) — Dividers

---

## EXPECTED HACKATHON DEMONSTRATION FLOW

1. **Open app**: `streamlit run app.py` → Browser opens at localhost:8501
2. **Scroll through header**: Show title and disclaimer
3. **Point to metrics**: Discuss dataset size and top-20 financial exposure
4. **Show signal overview**: Explain three archetypes
5. **Demonstrate case selection**: Click Rank 1 case (C-31298)
6. **Walk through evidence**: Show transaction IDs, amounts, months
7. **Point to fairness audit**: "Note age 60-74 over-represented"
8. **Emphasize governance**: "System never makes final decision"
9. **Select another case**: Rank 4 (Post-Closure) to show different signal
10. **Conclude**: "This supports human investigator, not replace"

**Total Demo Time**: ~10 minutes

---

**Visual Guide Complete**

This guide shows what you'll see when you run the dashboard. Every element reads from the actual generated outputs.
