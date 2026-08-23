# Demographic Fairness & Representation Audit Report

> **AUDIT SCOPE & GOVERNANCE OBJECTIVE:**
> This audit measures selection rates, representation ratios, and score distributions
> across four demographic and administrative dimensions (`age_band`, `language_preference`,
> `district`, and `tenure`). Demographic variables were strictly excluded from the scoring model.
> Observed disparities are reported honestly without distortion or artificial suppression.

---

## Executive Summary of Fairness Findings

| Dimension | Most Over-Represented Group | Rep Ratio | Most Under-Represented Group | Rep Ratio | Audit Classification |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **`age_band`** | `60-74` (8 cases / 40.0%) | 1.92x | `18-29` (1 cases / 5.0%) | 0.30x | Potential disparity requiring review |
| **`language_preference`** | `Spanish` (4 cases / 20.0%) | 1.65x | `English` (14 cases / 70.0%) | 0.90x | Potential disparity requiring review |
| **`district`** | `Northgate` (8 cases / 40.0%) | 1.50x | `Weybridge` (3 cases / 15.0%) | 0.64x | Potential disparity requiring review |
| **`tenure`** | `Private tenancy` (6 cases / 30.0%) | 1.52x | `Owner-occupier` (1 cases / 5.0%) | 0.26x | Potential disparity requiring review |

---

## 1. Small Sample Size Context ($N=20$)

> **IMPORTANT STATISTICAL CAVEAT:**
> In a sample of $N=20$ cases, **a single case represents 5.0 percentage points**.
> A shift of just 1–2 cases creates substantial percentage-level swings in representation ratios.
> For example, 4 Spanish-speaking cases represents 20.0% of the top 20, compared to an expected proportional baseline of 2.4 cases (12.14%).
> All percentages must be interpreted alongside their absolute underlying counts.

---

## 2. Demographic Dimension Deep-Dives

### Dimension: `age_band`

| Group | Pop Count | Pop % | Top-20 Count | Top-20 % | Rep Ratio | Selection Rate | Rate vs Base Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **18-29** | 701 | 16.69% | 1 | 5.00% | **0.30x** | 0.143% | 0.30x |
| **30-44** | 1,112 | 26.48% | 6 | 30.00% | **1.13x** | 0.540% | 1.13x |
| **45-59** | 992 | 23.62% | 4 | 20.00% | **0.85x** | 0.403% | 0.85x |
| **60-74** | 874 | 20.81% | 8 | 40.00% | **1.92x** | 0.915% | 1.92x |
| **75+** | 521 | 12.40% | 1 | 5.00% | **0.40x** | 0.192% | 0.40x |

**Signal & Score Breakdown across All 4,200 Cases for `age_band`:**

| Group | Total Cases | Flagged Cases | Award Spikes | Post-Closure | Duplicates | Mean Discrepancy ($) | Mean Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 18-29 | 701 | 22 | 6 | 8 | 8 | $62.40 | 1.31 |
| 30-44 | 1,112 | 41 | 9 | 17 | 15 | $85.97 | 1.67 |
| 45-59 | 992 | 22 | 4 | 7 | 11 | $47.27 | 0.94 |
| 60-74 | 874 | 34 | 10 | 17 | 7 | $110.32 | 2.12 |
| 75+ | 521 | 19 | 3 | 11 | 5 | $75.37 | 1.68 |

---

### Dimension: `language_preference`

| Group | Pop Count | Pop % | Top-20 Count | Top-20 % | Rep Ratio | Selection Rate | Rate vs Base Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | 3,277 | 78.02% | 14 | 70.00% | **0.90x** | 0.427% | 0.90x |
| **Other** | 413 | 9.83% | 2 | 10.00% | **1.02x** | 0.484% | 1.02x |
| **Spanish** | 510 | 12.14% | 4 | 20.00% | **1.65x** | 0.784% | 1.65x |

**Signal & Score Breakdown across All 4,200 Cases for `language_preference`:**

| Group | Total Cases | Flagged Cases | Award Spikes | Post-Closure | Duplicates | Mean Discrepancy ($) | Mean Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| English | 3,277 | 106 | 27 | 45 | 34 | $74.03 | 1.49 |
| Other | 413 | 12 | 1 | 7 | 4 | $69.91 | 1.38 |
| Spanish | 510 | 20 | 4 | 8 | 8 | $98.94 | 1.96 |

---

### Dimension: `district`

| Group | Pop Count | Pop % | Top-20 Count | Top-20 % | Rep Ratio | Selection Rate | Rate vs Base Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Ash Hill** | 663 | 15.79% | 3 | 15.00% | **0.95x** | 0.452% | 0.95x |
| **Calder Central** | 1,433 | 34.12% | 6 | 30.00% | **0.88x** | 0.419% | 0.88x |
| **Northgate** | 1,121 | 26.69% | 8 | 40.00% | **1.50x** | 0.714% | 1.50x |
| **Weybridge** | 983 | 23.40% | 3 | 15.00% | **0.64x** | 0.305% | 0.64x |

**Signal & Score Breakdown across All 4,200 Cases for `district`:**

| Group | Total Cases | Flagged Cases | Award Spikes | Post-Closure | Duplicates | Mean Discrepancy ($) | Mean Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Ash Hill | 663 | 22 | 11 | 4 | 7 | $99.40 | 1.69 |
| Calder Central | 1,433 | 50 | 11 | 25 | 14 | $81.81 | 1.64 |
| Northgate | 1,121 | 43 | 6 | 23 | 14 | $81.18 | 1.74 |
| Weybridge | 983 | 23 | 4 | 8 | 11 | $48.61 | 1.04 |

---

### Dimension: `tenure`

| Group | Pop Count | Pop % | Top-20 Count | Top-20 % | Rep Ratio | Selection Rate | Rate vs Base Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **No fixed abode** | 855 | 20.36% | 5 | 25.00% | **1.23x** | 0.585% | 1.23x |
| **Owner-occupier** | 815 | 19.40% | 1 | 5.00% | **0.26x** | 0.123% | 0.26x |
| **Private tenancy** | 830 | 19.76% | 6 | 30.00% | **1.52x** | 0.723% | 1.52x |
| **Resident with family** | 824 | 19.62% | 4 | 20.00% | **1.02x** | 0.485% | 1.02x |
| **Social tenancy** | 876 | 20.86% | 4 | 20.00% | **0.96x** | 0.457% | 0.96x |

**Signal & Score Breakdown across All 4,200 Cases for `tenure`:**

| Group | Total Cases | Flagged Cases | Award Spikes | Post-Closure | Duplicates | Mean Discrepancy ($) | Mean Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| No fixed abode | 855 | 27 | 7 | 13 | 7 | $76.48 | 1.57 |
| Owner-occupier | 815 | 28 | 4 | 17 | 7 | $77.86 | 1.62 |
| Private tenancy | 830 | 24 | 7 | 7 | 10 | $75.59 | 1.44 |
| Resident with family | 824 | 32 | 12 | 7 | 13 | $89.47 | 1.68 |
| Social tenancy | 876 | 27 | 2 | 16 | 9 | $64.62 | 1.37 |

---

## 3. Investigation of the Deliberate Demographic Trap

The problem documentation notes: *"A straightforward model using obvious features will flag one group at roughly 3x the base rate."*

### Investigation Findings:
1. **The Trap Mechanism**: When naive models incorporate administrative outreach (`contact_attempts`) or raw activity counters as risk proxies, they flag non-English speaking claimants at **4.5x the base rate (55% Spanish / 40% Other)** because non-English claimants require more caseworker contact attempts for language accommodation.
2. **Our Model's Protection**: By strictly excluding `contact_attempts`, `months_since_review`, and case-level adjustment counters, our ranking avoids this trap. The Spanish selection rate in our ranking is 1.65x (4 cases vs 2.4 expected), while `Other` languages are at parity (1.02x, 2 cases vs 2.0 expected).
3. **Underlying Driver**: The 4 Spanish-speaking cases in the top 20 represent high-dollar anomalies with clear evidence: Case `C-31298` ($7,504.56 spike, Rank 1), Case `C-33263` ($6,919.42 spike, Rank 5), Case `C-33980` ($4,488.39 duplicate across 4 months, Rank 10), and Case `C-33201` ($5,476.48 spike, Rank 11).

---

## 4. Governance & Fairness Conclusions

- **Demographic Independence in Scoring**: Demographic features were excluded from the mathematical ranking formula. The observed representation disparities are reported for human review; exclusion alone does not establish absence of disparate impact.
- **Casework Due Process**: Caseworkers investigating the top 20 must apply uniform evidentiary standards regardless of the applicant's age, language, district, or housing tenure.
- **Mitigation Recommendation**: In Stage 7 / future iterations, policy-makers can consider optional post-ranking stratified capacity allocation across districts or language groups if administrative workload distribution requires it.