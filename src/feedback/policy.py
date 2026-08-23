"""Two-tier policy engine separating algorithmic signal observation from human investigator determinations."""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
from src.feedback.store import FeedbackStore
from src.feedback.models import (
    ReviewOutcome,
    AlgorithmicSignalStatus,
    FeedbackAction,
    FeedbackCategory,
)


def get_algorithmic_signal_status(case_row: pd.Series) -> AlgorithmicSignalStatus:
    """Determine algorithmic signal status strictly from observable payment data.

    Returns an objective observation of whether transaction anomalies were detected.
    Does NOT declare legal legitimacy or culpability.

    Args:
        case_row: Series containing engineered features for a single case.

    Returns:
        AlgorithmicSignalStatus: Anomaly status or NO_HARD_SIGNAL.
    """
    sig = case_row.get("primary_signal", "None")
    if sig == "Post-Closure":
        return AlgorithmicSignalStatus.POST_CLOSURE_CONTINUATION
    elif sig == "Duplicate":
        return AlgorithmicSignalStatus.IN_MONTH_DUPLICATE
    elif sig == "Award Spike":
        return AlgorithmicSignalStatus.SEVERE_AWARD_SPIKE
    else:
        return AlgorithmicSignalStatus.NO_HARD_SIGNAL


def apply_feedback_policy(
    features_df: pd.DataFrame,
    feedback_store: Optional[FeedbackStore] = None
) -> pd.DataFrame:
    """Apply two-tier status tracking across all cases.

    Tier 1 (Algorithmic): Algorithmic Signal Status (e.g. NO_HARD_SIGNAL or SEVERE_AWARD_SPIKE).
    Tier 2 (Human): Investigator Review Status (e.g. INVESTIGATOR_CONFIRMED_LEGITIMATE or UNREVIEWED).

    Never automatically converts NO_HARD_SIGNAL into INVESTIGATOR_CONFIRMED_LEGITIMATE.

    Args:
        features_df: Case features DataFrame.
        feedback_store: Repository of human investigator reviews.

    Returns:
        pd.DataFrame: Annotated DataFrame with explicit two-tier statuses.
    """
    df = features_df.copy()

    if feedback_store is None:
        feedback_store = FeedbackStore()

    # Tier 1: Algorithmic Signal Status
    df["algorithmic_signal_status"] = df.apply(
        lambda r: get_algorithmic_signal_status(r).value, axis=1
    )

    # Tier 2: Human Investigator Status
    df["investigator_review_status"] = "UNREVIEWED_BY_INVESTIGATOR"
    df["feedback_action"] = "NONE"
    df["is_administratively_cleared"] = False
    df["investigator_feedback_reason"] = ""

    for idx, row in df.iterrows():
        cid = row["case_id"]
        fb = feedback_store.get_feedback(cid)
        if fb:
            df.at[idx, "investigator_review_status"] = fb.review_outcome.value
            df.at[idx, "feedback_action"] = fb.action.value
            df.at[idx, "is_administratively_cleared"] = (fb.action == FeedbackAction.EXCLUDE_FROM_WORKLIST)
            df.at[idx, "investigator_feedback_reason"] = fb.reason

    return df

