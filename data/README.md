# Problem 6 — The Overpayment Signal
## Data pack

### Contents

| File | What it is |
|:--|:--|
| `cases.csv` | 4,200 cases. One row per case. |
| `payments.csv` | 24,756 payment records. Six months, July to December 2025. |

### `cases.csv`

| Column | Meaning |
|:--|:--|
| `case_id` | Case reference. Joins to `payments.csv`. |
| `district` | One of four district offices. |
| `household_size` | Number of people in the household. |
| `age_band` | Age band of the applicant. |
| `language_preference` | Preferred language for correspondence. |
| `tenure` | Housing tenure. |
| `opened_date` | When the case was opened. |
| `status` | `Active`, `Suspended` or `Closed`. |
| `closure_month` | Month of closure, where closed. Empty otherwise. |
| `monthly_award` | The award as recorded on the case. |
| `payment_adjustments` | Count of adjustments applied to payments over the period. |
| `contact_attempts` | Count of recorded contact attempts over the period. |
| `months_since_review` | Months since the last completed review. |

### `payments.csv`

| Column | Meaning |
|:--|:--|
| `payment_id` | Payment reference. |
| `case_id` | The case paid. |
| `pay_month` | Month of payment, `YYYY-MM`. |
| `amount` | Amount paid. |
| `method` | `Transfer` or `Card`. |
| `adjustment` | `Y` where the payment carried an adjustment. |

There are no labels. Nothing in this pack tells you which payments were improper — if it did, there would be no problem to solve. You are building a ranking, not fitting a classifier to known answers.

### The needs figures

For reference, the monthly needs figure by household size, from the policy manual:

| Household size | 1 | 2 | 3 | 4 | 5 | 6 |
|:--|--:|--:|--:|--:|--:|--:|
| Needs figure | $1,240 | $1,670 | $2,000 | $2,330 | $2,660 | $2,990 |

An award should not normally approach the full needs figure, because the award is the needs figure *less* the household's countable income.

### What you should know before you start

There are genuine improper-payment patterns in this data and they are findable. Most participants will find them. That part is not the discriminator.

You are given `age_band`, `language_preference`, `district` and `tenure`, and the floor requires you to check how your ranking behaves across them and to report what you find **honestly, whether or not it passes**.

Read that requirement literally. A fairness check that passes is a fine outcome. A fairness check that fails, reported clearly, with your account of why it happens and what you did or could not do about it, is an equally complete answer to the floor — and in some circumstances a better one. What does not meet the floor is a check you did not run, or ran and did not report.

The third floor requirement — a written statement of what this model must never be used to decide automatically — is not a formality. Write it as though it will be read by someone deciding whether to deploy this.

### Reminder

A change to the requirements lands on day two. You will not be told what it is.
