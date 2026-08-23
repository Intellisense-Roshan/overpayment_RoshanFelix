# The Overpayment Signal — Final Project Summary & Hackathon Dossier

---

## 1. Problem Statement

Public benefit programs face significant improper-payment risks, including continuing disbursements to closed cases, duplicate transaction issuance, and unauthorized payment multiplier spikes. Because administrative datasets lack ground-truth fraud labels, this challenge cannot be treated as a supervised classification task. 

**The Overpayment Signal** is an explainable, deterministic **investigation-prioritization system** designed to assist human caseworkers in allocating limited investigative capacity toward cases with the highest financial exposure, clear transaction evidence, and persistent multi-month breakdown.

---

## 2. Data Overview & Integrity (FACTS FROM DATA)

The project analyzes two official read-only administrative datasets:
- **`data/cases.csv`**: **4,200 unique benefit cases** across 13 schema columns.
- **`data/payments.csv`**: **24,756 payment transactions** spanning July–December 2025 across 6 schema columns.
- **Join Integrity**: 100% case-level referential integrity (4,200 unique cases in both files, 0 orphan payments).
- **Statutory Caps**: 100% of cases and payments fall below the policy manual's household needs figures ($1,240 to $2,990). Improper payments are driven by case-level entitlement violations and transaction glitches rather than statutory ceiling breaches.

---

## 3. Discovered Signal Archetypes (FACTS FROM DATA)

Through rigorous empirical analysis, three distinct, **100% mutually exclusive** improper-payment signal archetypes were isolated:

| Signal Archetype | Exact Definition | Verified Cases | Total Financial Discrepancy | Operational Breakdown Mode |
| :--- | :--- | :---: | :---: | :--- |
| **1. Post-Closure Payments** | Payments issued strictly after `closure_month` | **60 cases** (182 payments) | **$138,222.83** | Case officially closed, but automated disbursements failed to terminate. |
| **2. In-Month Duplicates** | Identical `amount` paid $>1$ time in same `(case_id, pay_month)` | **46 cases** (62 months) | **$51,478.37** | Double-batch disbursement (split between Card and Transfer or dual Transfers). |
| **3. Severe Award Spikes** | Monthly payments exceeding $1.5\times$ to nearly $3.0\times$ `monthly_award` | **32 cases** (168 payments) | **$110,000.00+** | Multiplier glitch where monthly payments consistently outstrip authorized award. |
| **Total Candidate Pool** | Unique cases with at least one signal | **138 cases** (3.29% of dataset) | **~$299,700+** | Zero mutual overlap across the three archetypes. |

---

## 4. Feature Engineering & Quality Controls (DESIGN DECISIONS)

1. **Bypassing Unreliable Case Counters**: `cases.csv` contains a `payment_adjustments` counter that has a **42.67% error rate** (1,792 mismatches) when compared to actual `'Y'` flags in `payments.csv`. Feature engineering computes authoritative adjustment metrics directly from `payments.csv` (`actual_adjustment_count`, `adjustment_rate`).
2. **Exclusion of Administrative Proxies**: `contact_attempts` and `months_since_review` were strictly excluded from scoring. High contact attempts reflect language/outreach needs rather than financial leakage, and review delays reflect agency backlog.
3. **Exclusion of Demographics**: `age_band`, `language_preference`, `district`, and `tenure` have zero mathematical influence on scoring and are reserved exclusively for post-ranking fairness auditing.
4. **Calculated Financial Discrepancy**: Distinct, non-overlapping financial discrepancy measures are computed per case, ensuring zero double-counting.

---

## 5. Investigation-Priority Ranking Methodology (DESIGN DECISIONS)

To balance immediate financial recovery with evidence strength and chronic systematic persistence, the system uses **Balanced Multi-Criteria Scoring (Approach B)**:

$$\text{PriorityScore}_i = 100 \times \left( 0.50 \cdot S_{\text{financial}, i} + 0.30 \cdot S_{\text{persistence}, i} + 0.20 \cdot S_{\text{strength}, i} \right)$$

- **Financial Impact ($S_{\text{financial}} \in [0, 1]$)**: Normalized calculated financial discrepancy against dataset maximum ($D_{\max} = \$7,504.56$).
- **Persistence ($S_{\text{persistence}} \in [0, 1]$)**: Normalized duration/recurrence of the anomaly ($100\%$ of the Top 20 have maximum persistence $S_{\text{persistence}} = 1.0$).
- **Evidence Strength ($S_{\text{strength}} \in [0, 1]$)**: Scaled severity of the payment multiplier, duplicate proportion, or post-closure payment ratio.
- **Non-Signal Cases**: All 4,062 non-signal cases receive a priority score of exactly `0.0`.
- **Deterministic Tie-Breaker**: Multi-key sort on `(-PriorityScore, -FinancialDiscrepancy, -Persistence, case_id ASCII)`.

---

## 6. Top-20 Investigation Worklist Summary (FACTS FROM DATA)

The finalized worklist is saved in `outputs/top20_worklist.csv`:
- **Total Cases**: 20
- **Total Calculated Financial Discrepancy**: **$100,567.91**
- **Signal Breakdown**: 12 Award Spikes (60%), 7 Post-Closure (35%), 1 In-Month Duplicate (5%).
- **Top 5 Priority Cases**:
  1. `C-31298` (Score: 99.63, Award Spike, Discrepancy: **$7,504.56**, 6/6 payments $> 2.0\times$ award, peak 2.96x).
  2. `C-32995` (Score: 91.46, Award Spike, Discrepancy: **$6,663.18**, 6/6 payments $> 2.0\times$ award, peak 2.71x).
  3. `C-33743` (Score: 87.50, Award Spike, Discrepancy: **$5,943.47**, 6/6 payments $> 2.0\times$ award, peak 2.79x).
  4. `C-34196` (Score: 87.18, Post-Closure, Discrepancy: **$5,581.70**, Closed 2025-08, 4 post-closure payments).
  5. `C-33263` (Score: 86.05, Award Spike, Discrepancy: **$6,919.42**, 6/6 payments $> 1.5\times$ award, peak 1.99x).

---

## 7. Plain-Language Explainability (DESIGN DECISIONS)

Every top-20 case is accompanied by a plain-language narrative grounded in actual transaction records (`outputs/top20_investigator_report.md` and `outputs/top20_explanations.csv`):
- Avoids raw model jargon (no *"Persistence=1.0"*).
- Quotes exact authorized awards, peak payments, billing months, and transaction IDs (e.g. `P-107667`).
- Maintains a strictly objective, non-accusatory tone.
- Includes mandatory governance disclaimers.

---

## 8. Demographic Fairness Audit & Trap Investigation (FACTS & FINDINGS)

Audited across all four required dimensions (`outputs/fairness_report.md`):

1. **Age Band (`age_band`)**:
   - `60-74`: 40.0% of Top 20 (8 cases) vs 20.81% population (**1.92x representation ratio**). Driven by active high-dollar award spikes.
   - `18-29`: 5.0% of Top 20 (1 case) vs 16.69% population (**0.30x representation ratio**).
2. **Language Preference (`language_preference`)**:
   - `Spanish`: 20.0% of Top 20 (4 cases) vs 12.14% population (**1.65x representation ratio**).
   - `Other`: 10.0% of Top 20 (2 cases) vs 9.83% population (**1.02x representation ratio** — parity).
   - `English`: 70.0% of Top 20 (14 cases) vs 78.02% population (**0.90x representation ratio**).
3. **District (`district`)**:
   - `Northgate`: 40.0% of Top 20 (8 cases) vs 26.69% population (**1.50x representation ratio**). Driven by 4 post-closure continuation series logged in Northgate.
   - `Weybridge`: 15.0% of Top 20 (3 cases) vs 23.40% population (**0.64x representation ratio**).
4. **Housing Tenure (`tenure`)**:
   - `Private tenancy`: 30.0% of Top 20 (6 cases) vs 19.76% population (**1.52x representation ratio**).
   - `Owner-occupier`: 5.0% of Top 20 (1 case) vs 19.40% population (**0.26x representation ratio**).

### Investigation of the Deliberate Demographic Trap:
- **Trap Mechanism**: Naive models using `contact_attempts` as a suspiciousness proxy flag non-English claimants at **4.5x the base rate (55% Spanish / 40% Other)** because non-English claimants require more language accommodation calls.
- **Protection**: By excluding proxy variables from scoring, our model completely avoids this artificial bias trap.

---

## 9. Strict Governance & Decision Boundaries (DESIGN DECISIONS)

### The System MUST NEVER Automatically:
1. Determine that a claimant committed fraud.
2. Determine that a payment is legally improper.
3. Automatically suspend claimant benefits.
4. Automatically terminate a benefit case.
5. Automatically issue a clawback or overpayment recovery demand.
6. Automatically reduce a claimant's benefit award.
7. Automatically contact law enforcement or refer for criminal prosecution.
8. Automatically make an adverse eligibility decision.
9. Use demographic characteristics to determine investigation priority.
10. Treat the priority score as a probability of fraud.
11. Treat a ranking position as proof of wrongdoing.

### Human-in-the-Loop Investigation Workflow:
```
DATA INGESTION (cases.csv & payments.csv)
     ↓
SIGNAL DETECTION (Post-Closure, Duplicates, Multiplier Spikes)
     ↓
INVESTIGATION PRIORITY RANKING (Deterministic multi-criteria scoring)
     ↓
HUMAN INVESTIGATOR REVIEW (Caseworker audits file, policy & exceptions)
     ↓
HUMAN FACTUAL DETERMINATION (Caseworker renders formal finding)
     ↓
ADMINISTRATIVE ACTION IF APPROPRIATE (With full due process & appeal rights)
```

---

## 10. Limitations (LIMITATIONS)

1. **No Ground Truth**: Ranking prioritizes evidence-backed discrepancy, not judicial guilt.
2. **Small Top-20 Sample ($N=20$)**: Each case represents 5.0% of the worklist; a single case shift alters representation ratios by $\pm 0.25	ext{--}0.45	ext{x}$.
3. **Observation Window**: Analysis is bounded by the 6-month window (July–December 2025).

---

## 11. Future Improvements & Day-2 Extensibility (FUTURE IMPROVEMENTS)

1. **Stratified Casework Allocation**: Optional workflow balancing across district offices or language groups if casework capacity requires uniform geographic deployment.
2. **Longitudinal Expansion**: Ingestion of multi-year payment histories when available.
3. **Automated Audit Logging**: Real-time logging of caseworker review determinations back into the system.

---

## 12. Clean-Clone Reproducibility Instructions

```bash
# 1. Clone repository
git clone <repo-url>
cd overpayment-signal

# 2. Set up virtual environment
python -m venv .venv
# On Windows PowerShell: .venv\Scripts\Activate.ps1
# On Linux/macOS: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run automated test suite (42 tests)
python -m unittest discover -s tests

# 5. Execute full end-to-end pipeline
python -m src.pipeline
```
