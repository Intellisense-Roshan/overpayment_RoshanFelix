# Architecture & Modeling Decisions Log

## The Overpayment Signal

---

## 1. Candidate Signal Selection Rationale

Three distinct, empirically validated improper-payment signal archetypes were identified and engineered from raw data:

### Signal 1: Post-Closure Payment Continuation
- **Definition**: Payments issued in months strictly following the case's recorded `closure_month`.
- **Rationale**: When a case is closed, entitlement terminates. Continuing disbursements represent automated billing failures where system termination triggers were not passed to the disbursement engine.
- **Scope & Financial Magnitude**: 60 cases, 182 payment transactions, totaling **$138,222.83** in unentitled payments.
- **Casework Language**: *"Post-closure payment requiring investigation"* (not auto-labeled as fraud).

### Signal 2: In-Month Duplicate Payment Disbursement
- **Definition**: Multiple payment records within the same `(case_id, pay_month)` having identical payment amounts.
- **Rationale**: Identical disbursements in the same billing cycle represent system double-dipping or duplicate batch runs (often split between Card and Transfer or dual Transfers).
- **Scope & Financial Magnitude**: 46 cases across 62 monthly occurrences, totaling **$51,478.37** in duplicate disbursements.

### Signal 3: Severe Payment/Award Multiplier Spikes
- **Definition**: Cases where individual payments exceed $1.5\times$ to nearly $3.0\times$ the authorized `monthly_award` and persist across multiple months.
- **Rationale**: Standard casework permits minor fluctuations ($\pm \$10\text{--}\$35$) for routine income offsets. Multipliers $\ge 1.5\times$ represent structural overpayment anomalies where disbursements massively outstrip entitlement while staying under household caps.
- **Scope & Financial Magnitude**: 32 cases (30 persistent across $\ge 3$ months), generating **$110,000+** in unauthorized excess funds.

---

## 2. Signal Exclusivity & Overlap Verification

Direct verification across all 4,200 cases confirmed that the three signal archetypes are **100% mutually exclusive**:

| Signal Archetype | Case Count | Total Financial Discrepancy | Overlap with Other Signals |
| :--- | :---: | :---: | :---: |
| **Post-Closure Payments** | 60 | $138,222.83 | 0 cases |
| **In-Month Duplicate Payments** | 46 | $51,478.37 | 0 cases |
| **Severe Award Spikes** | 32 | $110,000.00+ | 0 cases |
| **Total Distinct Flagged Cases** | **138** | **~$299,700+** | **0 intersections** |

Because there is zero overlap, individual signal excess metrics can be combined cleanly into `signal_financial_discrepancy` without risk of double-counting.

---

## 3. Investigation-Priority Ranking Objective

### Core Philosophy
- **NOT a Fraud Classifier**: There are no ground-truth improper payment labels. The system does not predict an uncalibrated "probability of fraud."
- **Prioritization Tool**: The ranking answers: *"Given that caseworkers can investigate only a limited number of cases, which cases represent the highest financial exposure, clearest evidence, and most persistent systemic breakdown?"*

---

## 4. Candidate Ranking Formulations Considered

Two transparent, deterministic multi-criteria scoring models were formulated and evaluated:

### Approach A: Financial-Dominant Scoring
$$\text{Score}_A = 0.70 \cdot S_{\text{financial}} + 0.20 \cdot S_{\text{persistence}} + 0.10 \cdot S_{\text{strength}}$$
- **Top 20 Discrepancy**: $102,911.98
- **Signal Breakdown**: 13 Award Spikes, 6 Post-Closure, 1 Duplicate.
- **Limitation**: Tends to overweight short-term high-award spikes over multi-month systemic post-closure disbursements.

### Approach B: Balanced Multi-Criteria Scoring (SELECTED)
$$\text{Score}_B = 0.50 \cdot S_{\text{financial}} + 0.30 \cdot S_{\text{persistence}} + 0.20 \cdot S_{\text{strength}}$$
- **Top 20 Discrepancy**: $100,567.91
- **Signal Breakdown**: 12 Award Spikes, 7 Post-Closure, 1 Duplicate.
- **Why Selected**:
  1. **Systemic Persistence**: 100% of cases in the Top 20 have maximum persistence ($S_{\text{persistence}} = 1.0$), ensuring investigators focus on chronic multi-month issues rather than one-off outliers.
  2. **Signal Diversity**: Increases representation of clear procedural post-closure cases (from 6 to 7) while preserving the single most severe multi-month duplicate case (`C-33980`, $4,488.39 duplicate excess across 4 months).
  3. **High Recovery Value**: Retains over $100,500+ in actionable discrepancy (97.7% of Approach A's dollar total) with significantly higher evidence confidence.

---

## 5. Mathematical Scoring Formula & Component Definitions

For each case $i$, the composite Investigation Priority Score (0.0 to 100.0) is:

$$\text{PriorityScore}_i = 100 \times \left( 0.50 \cdot S_{\text{financial}, i} + 0.30 \cdot S_{\text{persistence}, i} + 0.20 \cdot S_{\text{strength}, i} \right)$$

### 1. Financial Impact ($S_{\text{financial}}$)
$$S_{\text{financial}, i} = \frac{D_i}{\max_{j}(D_j)}$$
where $D_i$ is the calculated excess dollar discrepancy:
- Post-Closure: $D_i = \text{post\_closure\_total\_amount}$
- Duplicate: $D_i = \text{duplicate\_excess\_amount}$
- Award Spike: $D_i = \text{total\_excess\_above\_award}$
- Non-Signal Cases: $D_i = 0.0$ ($\implies S_{\text{financial}} = 0.0$)

### 2. Persistence / Recurrence ($S_{\text{persistence}}$)
- Post-Closure: $\min(1.0, \text{post\_closure\_month\_count} / 4.0)$
- Duplicate: $\min(1.0, \text{duplicate\_month\_count} / 4.0)$
- Award Spike: $\min(1.0, \text{payments\_above\_1\_5x\_count} / 6.0)$
- Non-Signal Cases: $0.0$

### 3. Evidence Strength ($S_{\text{strength}}$)
- Post-Closure: $\min(1.0, (\text{post\_closure\_payment\_count} / \text{payment\_count}) / 0.667)$
- Duplicate: $\min(1.0, (\text{duplicate\_excess\_amount} / \text{total\_payment\_amount}) \times 2.0 \times (1.2 \text{ if multi-method else } 1.0))$
- Award Spike: $\min(1.0, \max(0.0, (\text{max\_ratio} - 1.0) / 2.0))$
- Non-Signal Cases: $0.0$

---

## 6. Deterministic Tie-Breaking Rule

To guarantee 100% reproducibility, ties in priority score are resolved sequentially by:
1. `investigation_priority_score` (Descending)
2. `signal_financial_discrepancy` (Descending in dollars)
3. `norm_persistence` (Descending)
4. `case_id` (Ascending lexicographically, e.g. `C-30001` before `C-30002`)

---

## 7. Plain-Language Case Explainability & Traceability

### Design Principles:
1. **Plain Language for Human Caseworkers**: Explanations translate statistical and transaction anomalies into plain English without exposing raw feature jargon.
2. **Strict Evidence Grounding**: Every summary statement, dollar sum, date, and ratio is directly computed from raw records in `cases.csv` and `payments.csv`.
3. **Full Transaction Traceability**: Every explanation explicitly references all relevant payment transaction IDs, payment amounts, and billing months.
4. **Non-Judicial & Non-Accusatory Tone**: Explanations describe observable anomalies rather than asserting fraud or guilt.
5. **Standard Governance Disclaimer**: All artifacts include:
   > *"This ranking identifies cases for investigation based on observed payment patterns. It does not determine whether a payment was improper. Human review is required."*

---

## 8. Demographic Fairness Audit & Representation Evaluation

### Methodology:
The ranking was audited post-scoring across four demographic and administrative dimensions: `age_band`, `language_preference`, `district`, and `tenure`.

### Audit Findings:
1. **`age_band`**:
   - `60-74` represents 40.0% of Top 20 (8 cases) vs 20.81% population (Rep Ratio: 1.92x).
   - Driven by the concentration of large award spike cases among older active households.
2. **`language_preference`**:
   - `Spanish` represents 20.0% of Top 20 (4 cases) vs 12.14% population (Rep Ratio: 1.65x).
   - `English` represents 70.0% (14 cases) vs 78.02% (Rep Ratio: 0.90x).
   - `Other` represents 10.0% (2 cases) vs 9.83% (Rep Ratio: 1.02x).
3. **`district`**:
   - `Northgate` represents 40.0% of Top 20 (8 cases) vs 26.69% population (Rep Ratio: 1.50x), driven by Northgate logging 4 of the 7 post-closure continuation series.
   - `Weybridge` represents 15.0% (3 cases) vs 23.40% population (Rep Ratio: 0.64x).
4. **`tenure`**:
   - `Private tenancy` represents 30.0% (6 cases) vs 19.76% population (Rep Ratio: 1.52x).
   - `Owner-occupier` represents 5.0% (1 case) vs 19.40% population (Rep Ratio: 0.26x).

### Investigation of the Deliberate Demographic Trap:
- **Trap Identified in Naive Models**: Models that use administrative contact attempts (`contact_attempts`) as a risk proxy flag non-English claimants at **4.5x the base rate (55% Spanish / 40% Other)** because non-English claimants naturally require more caseworker calls.
- **Protection in Our Architecture**: By strictly excluding `contact_attempts` and `months_since_review` from scoring, our model completely avoids this artificial bias trap.

### Statistical Caveat on Small Sample ($N=20$):
In a sample of 20 cases, each single case accounts for exactly 5.0 percentage points. A shift of just 1 case alters the representation ratio by $approx \pm 0.25	ext{--}0.45	ext{x}$.

---

## 9. Excluded & Rejected Variables

| Variable | Reason for Exclusion |
| :--- | :--- |
| **`age_band`, `language_preference`, `district`, `tenure`** | **Protected/Administrative Demographics**: Excluded to prevent algorithmic bias; reserved strictly for independent fairness auditing. |
| **`cases.payment_adjustments`** | **Data Inconsistency**: 42.67% error rate compared to `payments.csv`. |
| **`contact_attempts`** | **Proxy Risk**: Measures administrative outreach, not financial discrepancy. Induces 4.5x non-English demographic trap if used. |
| **`months_since_review`** | **Administrative Delay**: Reflects agency backlog rather than claimant misconduct. |

---

## 10. Known Limitations

1. **No Ground Truth**: Ranking prioritizes evidence-backed discrepancy, not judicial guilt.
2. **Casework Due Process**: All top-20 cases must undergo human caseworker review before any administrative action.
3. **Data Horizon**: Analysis is bounded by the 6-month observation window (July–December 2025).
4. **Small Sample Fluctuations**: Top-20 representation ratios are sensitive to single-case shifts ($1	ext{ case} = 5\%$).

---

## 11. Day-2 Surprise Challenge — Investigator Feedback

### A. What the Challenge Revealed
The Day-2 Surprise Challenge presented a real-world caseworker audit of case **`C-33248`** in which an investigator concluded:
- The case **should NOT have been on the investigation worklist**.
- Payment variation was **legitimate and timely reported** due to household employment changes.
- The 5 adjustments recorded in `cases.csv` were **Department processing corrections**, not claimant wrongdoing.
- The 7 contact attempts were driven by **language assistance/communication needs** (Spanish-speaking household).
- Warning: Repeatedly sending "busy files" with high administrative activity burns caseworker trust and clogs investigation capacity.

### B. What Happened with Case `C-33248`
- **Authorized Monthly Award**: \$994.32 (\$5,965.92 expected over 6 months).
- **Total Payments Received**: \$5,666.70 across 6 months.
- **Net Excess Paid**: **-\$299.22** (household was actually underpaid relative to full entitlement).
- **Max Single Payment**: \$1,043.76 (only 1.05× award, representing routine monthly income adjustments).
- **Hard Signal Counts**: 0 Post-Closure, 0 Duplicates, 0 Multiplier Spikes.

### C. Why `C-33248` Was NOT a Day-1 False Referral from Our Model
- **Day-1 Top-20 Rank**: **Not in Top-20** (ranked 3,281 out of 4,200).
- **Day-1 Priority Score**: **`0.00`**.
- **Day-1 Architecture Alignment**: On Day 1, we recognized that `contact_attempts`, `months_since_review`, and `cases.payment_adjustments` are unreliable administrative counters that do not represent overpayment risk. Consequently, our signal-based model had already assigned `C-33248` a Priority Score of 0.00 on Day 1.

### D. What Naive Models Could Get Wrong (The Administrative Proxy Trap)
- In naive models that score cases using activity proxies (e.g. high contact attempts, adjustment counts, or raw variance), `C-33248` is pushed to the top of the worklist because it has 7 contact attempts and 5 recorded adjustments.
- Across the 4,200 cases, there are **98 "busy files"** ($\ge 5$ contacts, $\ge 3$ adjustments). **87.8% of these files belong to non-English speaking households** (53.1% Spanish, 34.7% Other, 12.2% English). Using administrative activity as a risk proxy creates an artificial **4.5× bias trap against non-English claimants**.

### E. What Day-2 Adds to Our System
1. **Bi-Directional Feedback Store (`src/feedback/store.py`)**: A structured repository to log human caseworker findings (`INVESTIGATOR_CONFIRMED_LEGITIMATE`, `CONFIRMED_DISCREPANCY`, `DEPARTMENTAL_PROCESSING_ERROR`, `PENDING_INVESTIGATION`).
2. **Two-Tier Status Architecture (`src/feedback/policy.py`)**: Explicitly decouples algorithmic observations from human determinations.
3. **Four Core Governance Principles (`src/governance/guardrails.py`)**:
   - *"Administrative activity is not automatically evidence of claimant wrongdoing."*
   - *"Absence of a detected signal is not proof that a payment was legitimate."*
   - *"Investigator-confirmed findings are distinguished from algorithmic observations."*
   - *"Human feedback improves prioritization while preserving human decision authority and due process."*
4. **Structured Audit Trail**: Automatic generation of `outputs/investigator_feedback_log.csv`.

### F. Why `NO_HARD_SIGNAL` and `INVESTIGATOR_CONFIRMED_LEGITIMATE` Are Strictly Different
- **`NO_HARD_SIGNAL` (Tier 1: Algorithmic Observation)**: The model observes no post-closure continuation, duplicate disbursement, or severe award multiplier spike in the payment records. This is a descriptive observation of available data — **it is NOT proof of legal legitimacy**.
- **`INVESTIGATOR_CONFIRMED_LEGITIMATE` (Tier 2: Human Determination)**: A human caseworker with access to the complete case file, employer verifications, and Department records audited the case and rendered a factual finding of legitimacy.
- **Strict Boundary**: The system **never** automatically converts `NO_HARD_SIGNAL` into `INVESTIGATOR_CONFIRMED_LEGITIMATE` based on numerical thresholds alone.

### G. How Future Investigator Feedback Is Captured
Caseworkers record review outcomes into the `FeedbackStore` with their investigator ID, review date, finding category, and narrative rationale. When new payment batches arrive, the ranking pipeline checks the `FeedbackStore` to respect caseworker determinations and avoid re-referring cleared files without human authorization.

### H. Remaining Limitations
1. **No Direct Access to Case Notes**: The model operates strictly on structured database tables and formal feedback logs; it cannot read narrative free-text in case management software.
2. **Human Caseworker Due Process**: Algorithmic signals provide prioritization only; all legal, eligibility, and clawback decisions remain exclusively with human adjudicators.

