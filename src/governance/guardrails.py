"""Governance, Guardrails, and Non-Automation Policy Module.

Explicitly specifies, documents, and enforces the non-negotiable boundaries
defining what The Overpayment Signal system MUST NEVER decide automatically.
"""
from typing import List

PROHIBITED_AUTOMATED_ACTIONS: List[str] = [
    "Determine that a claimant committed fraud.",
    "Determine that a payment is legally improper.",
    "Automatically suspend claimant benefits.",
    "Automatically terminate a benefit case.",
    "Automatically issue a clawback or overpayment recovery demand.",
    "Automatically reduce a claimant's benefit award.",
    "Automatically contact law enforcement or refer for criminal prosecution.",
    "Automatically make an adverse eligibility decision.",
    "Use demographic characteristics to determine investigation priority.",
    "Treat the priority score as a probability of fraud.",
    "Treat a ranking position as proof of wrongdoing.",
]

PERMITTED_SYSTEM_SCOPE: List[str] = [
    "Identifies cases with observed payment-pattern signals from administrative data.",
    "Ranks cases to assist human caseworkers in prioritizing limited investigation capacity.",
    "Explains the observable transaction evidence behind the ranking in plain language.",
    "Provides transparent demographic fairness diagnostics across protected dimensions.",
    "Supports, but never replaces, human caseworker judgment and statutory due process.",
]

ADMINISTRATIVE_ACTIVITY_PRINCIPLE: str = (
    "Administrative activity is not automatically evidence of claimant wrongdoing."
)

ABSENCE_OF_SIGNAL_PRINCIPLE: str = (
    "Absence of a detected signal is not proof that a payment was legitimate."
)

TWO_TIER_DISTINCTION_PRINCIPLE: str = (
    "Investigator-confirmed findings are distinguished from algorithmic observations."
)

HUMAN_FEEDBACK_AUTHORITY_PRINCIPLE: str = (
    "Human feedback improves prioritization while preserving human decision authority and due process."
)

HUMAN_DECISION_WORKFLOW: str = (
    "HUMAN-IN-THE-LOOP INVESTIGATION WORKFLOW:\n"
    "  1. DATA INGESTION (cases.csv & payments.csv)\n"
    "       ↓\n"
    "  2. SIGNAL DETECTION (Post-Closure, Duplicates, Multiplier Spikes)\n"
    "       ↓\n"
    "  3. INVESTIGATION PRIORITY RANKING (Deterministic multi-criteria scoring)\n"
    "       ↓\n"
    "  4. HUMAN INVESTIGATOR REVIEW (Caseworker assigned priority worklist)\n"
    "       ↓\n"
    "  5. CASE RECORD & POLICY VERIFICATION (Caseworker audits file, policy & exceptions)\n"
    "       ↓\n"
    "  6. HUMAN DETERMINATION (Caseworker renders formal factual finding)\n"
    "       ↓\n"
    "  7. ADMINISTRATIVE ACTION IF APPROPRIATE (With full claimant notice & appeal rights)\n"
    "       ↓\n"
    "  8. INVESTIGATOR FEEDBACK LOOP (Case outcome feeds back into continuous policy tuning)"
)




def get_governance_statement() -> str:
    """Return formal statement of non-automated decision boundaries.

    Returns:
        str: Policy statement for deployment review.
    """
    lines = [
        "================================================================================",
        "GOVERNANCE & NON-AUTOMATION POLICY — THE OVERPAYMENT SIGNAL",
        "================================================================================",
        "The Overpayment Signal model is strictly an investigative prioritization tool",
        "designed to assist human caseworkers in allocating review capacity. It is NOT",
        "an automated adjudication or fraud-detection system.",
        "",
        "PROHIBITED ACTIONS -- THE SYSTEM MUST NEVER AUTOMATICALLY:",
    ]
    for idx, rule in enumerate(PROHIBITED_AUTOMATED_ACTIONS, start=1):
        lines.append(f"  {idx:2d}. {rule}")
        
    lines.extend([
        "",
        "PERMITTED SYSTEM SCOPE -- THE SYSTEM ONLY:",
    ])
    for item in PERMITTED_SYSTEM_SCOPE:
        lines.append(f"  - {item}")
        
    lines.extend([
        "",
        "KEY GOVERNANCE PRINCIPLES:",
        f"  - {ADMINISTRATIVE_ACTIVITY_PRINCIPLE}",
        f"  - {ABSENCE_OF_SIGNAL_PRINCIPLE}",
        f"  - {TWO_TIER_DISTINCTION_PRINCIPLE}",
        f"  - {HUMAN_FEEDBACK_AUTHORITY_PRINCIPLE}",
        "",
        HUMAN_DECISION_WORKFLOW,
        "================================================================================",
    ])
    return "\n".join(lines)




