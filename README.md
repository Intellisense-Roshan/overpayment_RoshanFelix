# The Overpayment Signal

## Live Demo

[Open the deployed Streamlit dashboard](https://intellisense-roshan-overpayment-roshanfelix-app-ru4iej.streamlit.app/)

An explainable, deterministic investigation-prioritization system designed to help caseworkers allocate limited audit capacity toward benefit cases with the highest financial exposure, clear transaction evidence, and persistent multi-month system breakdowns.

---

## 1. Project Overview & Problem Statement

Public benefit programs face significant improper-payment vulnerabilities, including continuing disbursements to closed cases, duplicate batch disbursements, and unauthorized award multiplier spikes. Because administrative records contain **no ground-truth fraud labels**, this problem cannot be solved with supervised classifiers or uncalibrated "fraud probabilities."

**The Overpayment Signal** implements a deterministic, multi-criteria prioritization architecture that:
1. Ingests and validates 4,200 benefit cases and 24,756 payment transactions without mutating raw data.
2. Isolates three mutually exclusive improper-payment signal archetypes: **Post-Closure Payments**, **In-Month Duplicates**, and **Severe Award Spikes**.
3. Ranks a **Top-20 Investigation Worklist** representing **$100,567.91 in calculated financial discrepancy** with 100% persistence across all top cases.
4. Produces plain-language, transaction-grounded casework explanations with exact payment IDs.
5. Audits demographic fairness across four dimensions (`age_band`, `language_preference`, `district`, `tenure`), identifying and avoiding deliberate proxy traps (e.g. contact attempts).
6. Codifies **strict non-automation governance guardrails** defining what the model must never decide automatically.

---

## 2. Governance & Strict Non-Automation Policy

> **CRITICAL POLICY BOUNDARY FOR DEPLOYMENT DECISION-MAKERS:**
> 
> The Overpayment Signal is exclusively an **investigative prioritization tool** built to assist human caseworkers in allocating review capacity. It is **NOT** an automated adjudication or fraud-detection system.

### The System MUST NEVER Automatically:
1. **Determine that a claimant committed fraud.**
2. **Determine that a payment is legally improper.**
3. **Automatically suspend claimant benefits.**
4. **Automatically terminate a benefit case.**
5. **Automatically issue a clawback or overpayment recovery demand.**
6. **Automatically reduce a claimant's benefit award.**
7. **Automatically contact law enforcement or refer for criminal prosecution.**
8. **Automatically make an adverse eligibility decision.**
9. **Use demographic characteristics to determine investigation priority.**
10. **Treat the priority score as a probability of fraud.**
11. **Treat a ranking position as proof of wrongdoing.**

### Human-in-the-Loop Investigation Workflow:
```
DATA INGESTION (cases.csv & payments.csv)
     ↓
SIGNAL DETECTION (Post-Closure, Duplicates, Multiplier Spikes)
     ↓
INVESTIGATION PRIORITY RANKING (Deterministic multi-criteria scoring)
     ↓
HUMAN INVESTIGATOR REVIEW (Caseworker audits case file, policy & exceptions)
     ↓
HUMAN FACTUAL DETERMINATION (Caseworker renders formal finding)
     ↓
ADMINISTRATIVE ACTION IF APPROPRIATE (With full due process & appeal rights)
```

---

## 3. Dataset Description

The system processes two read-only administrative datasets in `data/`:

| Dataset | Dimensions | Key Columns | Description |
| :--- | :--- | :--- | :--- |
| **`cases.csv`** | 4,200 rows $	imes$ 13 cols | `case_id`, `district`, `household_size`, `age_band`, `language_preference`, `tenure`, `status`, `closure_month`, `monthly_award` | Case metadata and authorized monthly award schedules. |
| **`payments.csv`** | 24,756 rows $	imes$ 6 cols | `payment_id`, `case_id`, `pay_month`, `amount`, `method`, `adjustment` | 6 months of transaction records (July–December 2025). |

---

## 4. Setup & Quickstart from a Clean Clone

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Standard virtual environment tools

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Intellisense-Roshan/overpayment_RoshanFelix.git
cd overpayment-signal

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Automated Test Suite (42 unit tests)
```bash
python -m unittest discover -s tests
```

### 4. Execute the End-to-End Pipeline
```bash
python -m src.pipeline
```

### 5. Launch the Investigation Dashboard UI
```bash
streamlit run app.py
```

The dashboard opens at `http://localhost:8501` and displays:
- Key metrics (4,200 cases, 24,756 payments, 138 signal cases)
- Signal archetypes overview (Post-Closure, Duplicate, Award Spike)
- Interactive top-20 investigation worklist
- Case detail & evidence viewer
- Demographic fairness audit across 4 dimensions
- Governance & human decision boundary statements

### Streamlit Community Cloud Deployment

The app is deployable from the public GitHub repository on Streamlit Community
Cloud with this configuration:

- Repository: `Intellisense-Roshan/overpayment_RoshanFelix`
- Branch: `main`
- Main file path: `app.py`

After deployment, Streamlit Community Cloud provides the public app URL. The
app reads the repository's `data/` and `outputs/` files using repository-relative
paths, so no local machine paths or secrets are required.

---

## 6. CLI Usage & Options

The command-line interface supports flexible orchestration:

```bash
# View non-automation policy statement and governance guardrails
python -m src.pipeline --governance-only

# Run pipeline with custom inputs and custom top-k
python -m src.pipeline --cases data/cases.csv --payments data/payments.csv --top-k 20 --output-dir outputs
```

---

## 7. Pipeline Architecture & Modular Structure

```
overpayment-signal/
├── data/                               # Raw datasets & policy manual (READ-ONLY)
│   ├── cases.csv                       # 4,200 case records
│   ├── payments.csv                    # 24,756 payment transactions
│   └── README.md                       # Data dictionary & needs schedule
├── src/                                # Core modular Python package
│   ├── __init__.py
│   ├── data/                           # Data loading, validation, and constants
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── features/                       # Signal detection & feature extraction
│   │   ├── __init__.py
│   │   └── engineer.py
│   ├── models/                         # Deterministic priority ranking
│   │   ├── __init__.py
│   │   └── ranking.py
│   ├── explainability/                 # Plain-language casework explainer
│   │   ├── __init__.py
│   │   └── explainer.py
│   ├── fairness/                       # Demographic parity auditing
│   │   ├── __init__.py
│   │   └── metrics.py
│   ├── governance/                     # Non-automation guardrails & policy
│   │   ├── __init__.py
│   │   └── guardrails.py
│   └── pipeline.py                     # Main CLI orchestrator
├── outputs/                            # Generated audit artifacts & reports
│   ├── top20_worklist.csv              # Prioritized Top-20 case worklist
│   ├── top20_explanations.csv          # Structured case explanations
│   ├── top20_investigator_report.md    # Formatted caseworker dossier
│   ├── fairness_summary.csv            # Demographic parity metrics table
│   ├── fairness_report.md              # Detailed fairness audit report
│   └── final_project_summary.md        # Comprehensive hackathon summary
├── tests/                              # Complete unit test suite (42 tests)
│   ├── __init__.py
│   ├── test_structure.py               # Ingestion & governance tests
│   ├── test_features.py                # Feature extraction & signal tests
│   ├── test_ranking.py                 # Determinism & ranking guardrail tests
│   ├── test_explainer.py               # Traceability & tone compliance tests
│   └── test_fairness.py                # Demographic metric & ratio tests
├── DECISIONS.md                        # Architecture & Modeling Decisions Log
├── AI-USAGE.md                         # Honest AI assistance disclosure
├── requirements.txt                    # Minimal dependencies
└── README.md                           # Operational documentation (this file)
```

---

## 8. Discovered Signal Archetypes & Feature Engineering

Three distinct, mutually exclusive signal archetypes were discovered:

1. **Post-Closure Payment Continuation (60 cases, 182 payments, $138,222.83)**:
   - Automated monthly payments continuing after a case's official `closure_month`.
2. **In-Month Duplicate Disbursements (46 cases, 62 months, $51,478.37)**:
   - Exact duplicate payment amounts issued within the same billing month (split between Card and Transfer or dual Transfers).
3. **Severe Payment/Award Multiplier Spikes (32 cases, 168 payments, $110,000.00+)**:
   - Monthly disbursements exceeding 1.5x to nearly 3.0x the authorized `monthly_award` and persisting across multiple months.

### Bypassing Unreliable Case Counters
`cases.csv` contains `payment_adjustments`, which has a **42.67% error rate** (1,792 mismatches) when compared to actual payment records in `payments.csv`. The feature engineering module calculates authoritative adjustment metrics directly from `payments.csv` (`actual_adjustment_count`, `adjustment_rate`).

---

## 9. Ranking Methodology (Balanced Multi-Criteria Scoring)

The investigation priority score ($0.0$ to $100.0$) is calculated deterministically:

$$\text{PriorityScore}_i = 100 \times \left( 0.50 \cdot S_{\text{financial}, i} + 0.30 \cdot S_{\text{persistence}, i} + 0.20 \cdot S_{\text{strength}, i} \right)$$

- **Financial Discrepancy ($S_{\text{financial}}$)**: Calculated financial discrepancy normalized against the dataset maximum ($D_{\max} = \$7,504.56$).
- **Persistence ($S_{\text{persistence}}$)**: Recurrence duration ($100\%$ of Top-20 cases have maximum persistence $S_{\text{persistence}} = 1.0$).
- **Evidence Strength ($S_{\text{strength}}$)**: Severity of the payment multiplier, duplicate proportion, or post-closure payment ratio.
- **Deterministic Tie-Breaking**: `(-PriorityScore, -FinancialDiscrepancy, -Persistence, case_id ASCII)`.

---

## 10. Explainability & Investigator Report

Every top-20 case is accompanied by a plain-language casework summary and exact transaction IDs in `outputs/top20_investigator_report.md`:
- **Example Rank 1 (`C-31298`)**: *"Case C-31298 received 6 payments during the observation period, with 6 exceeding twice the award relative to its recorded monthly award of $746.45. The largest payment was $2,211.51 (2.96x award), creating $7,504.56 in calculated financial discrepancy relative to the authorized award."*

---

## 11. Fairness Audit & Demographic Trap Investigation

Audited post-scoring across `age_band`, `language_preference`, `district`, and `tenure` (`outputs/fairness_report.md`):

| Dimension | Highest Representation Ratio | Lowest Representation Ratio | Audit Finding |
| :--- | :--- | :--- | :--- |
| **`age_band`** | `60-74` (1.92x / 8 cases) | `18-29` (0.30x / 1 case) | Potential disparity requiring review |
| **`language_preference`** | `Spanish` (1.65x / 4 cases) | `English` (0.90x / 14 cases) | Potential disparity requiring review |
| **`district`** | `Northgate` (1.50x / 8 cases) | `Weybridge` (0.64x / 3 cases) | Potential disparity requiring review |
| **`tenure`** | `Private tenancy` (1.52x / 6 cases) | `Owner-occupier` (0.26x / 1 case) | Potential disparity requiring review |

### The Deliberate Demographic Trap:
Naive models that incorporate `contact_attempts` as a suspiciousness proxy flag non-English claimants at **4.5x the base rate (55% Spanish / 40% Other)** because non-English claimants require more language accommodation calls. By strictly excluding administrative proxy features from scoring, our model completely avoids this artificial bias trap.

---

## 12. Testing & Code Quality

The repository contains 42 comprehensive unit tests covering:
- Ingestion schema validation and join integrity
- Feature calculation and signal mutual exclusivity
- Deterministic ranking and guardrail non-influence (demographics and proxies)
- Plain-language explanation accuracy and non-accusatory tone
- Fairness metric and representation ratio math

Run all tests:
```bash
python -m unittest discover -s tests
```

The three root-level `test_app_*.py` files are additional dashboard data/readiness
verification scripts and are not part of unittest discovery.

## 13. Day-2 Feedback and Human Review

The supplied investigator review is stored in `data/investigator_feedback.csv` and
loaded by the general `FeedbackStore`. The algorithmic `NO_HARD_SIGNAL` status is
kept separate from human outcomes such as `INVESTIGATOR_CONFIRMED_LEGITIMATE`.
Human review outcomes are never inferred from transaction data alone.

## 14. Known Limitations

- The six-month observation window cannot capture patterns outside July-December 2025.
- The ranking is an investigation-prioritization score, not a legal or fraud finding.
- Fairness metrics are descriptive audits of a 20-case sample; they do not establish causal disparity.
- Narrative case notes and external policy exceptions are outside the structured CSV inputs.
- Generated artifacts in `outputs/` are reproducible and should be regenerated after input changes.

## 15. Clean-Clone Run Sequence

From the repository root after installing `requirements.txt`, run:

```bash
python -m unittest discover -s tests
python -m src.pipeline
streamlit run app.py
```

The pipeline creates `outputs/top20_worklist.csv`, `outputs/top20_explanations.csv`,
`outputs/top20_investigator_report.md`, `outputs/fairness_summary.csv`,
`outputs/fairness_report.md`, and `outputs/investigator_feedback_log.csv`.
