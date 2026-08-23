"""Investigation Priority Ranking Module for The Overpayment Signal.

Produces a deterministic, explainable top-k case worklist for human caseworker investigation.
Balances financial impact (recovery magnitude), anomaly persistence (duration),
and evidence strength across verified signal archetypes.
"""
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np


def compute_investigation_priority_scores(
    features_df: pd.DataFrame,
    financial_weight: float = 0.50,
    persistence_weight: float = 0.30,
    strength_weight: float = 0.20,
) -> pd.DataFrame:
    """Compute deterministic investigation priority scores for all cases.

    Args:
        features_df: Case features DataFrame from src.features.engineer.
        financial_weight: Weight for normalized financial discrepancy (default: 0.50).
        persistence_weight: Weight for anomaly recurrence/duration (default: 0.30).
        strength_weight: Weight for evidence severity (default: 0.20).

    Returns:
        pd.DataFrame: Features table with normalized score components and priority score.
    """
    df = features_df.copy()
    
    # 1. Financial Discrepancy ($) per verified signal
    def get_signal_discrepancy(row: pd.Series) -> float:
        sig = row.get('primary_signal', 'None')
        if sig == 'Post-Closure':
            return float(row.get('post_closure_total_amount', 0.0))
        elif sig == 'Duplicate':
            return float(row.get('duplicate_excess_amount', 0.0))
        elif sig == 'Award Spike':
            return float(row.get('total_excess_above_award', 0.0))
        return 0.0
        
    df['signal_financial_discrepancy'] = df.apply(get_signal_discrepancy, axis=1)
    
    # Normalize financial component against max discrepancy in dataset
    max_discrepancy = df['signal_financial_discrepancy'].max()
    if max_discrepancy > 0:
        df['norm_financial'] = df['signal_financial_discrepancy'] / max_discrepancy
    else:
        df['norm_financial'] = 0.0
        
    # 2. Persistence Component [0.0 to 1.0]
    def get_persistence(row: pd.Series) -> float:
        sig = row.get('primary_signal', 'None')
        if sig == 'Post-Closure':
            # Max possible post-closure months is 4 (Aug-Dec for July closure)
            return min(1.0, float(row.get('post_closure_month_count', 0)) / 4.0)
        elif sig == 'Duplicate':
            # Max duplicate months in dataset is 4
            return min(1.0, float(row.get('duplicate_month_count', 0)) / 4.0)
        elif sig == 'Award Spike':
            # Max possible spike months is 6
            return min(1.0, float(row.get('payments_above_1_5x_count', 0)) / 6.0)
        return 0.0
        
    df['norm_persistence'] = df.apply(get_persistence, axis=1)
    
    # 3. Evidence Strength Component [0.0 to 1.0]
    def get_strength(row: pd.Series) -> float:
        sig = row.get('primary_signal', 'None')
        if sig == 'Post-Closure':
            # Post-closure payment ratio scaled (4 post-closure pays / 6 total = 0.667 -> 1.0)
            pay_cnt = max(1, int(row.get('payment_count', 1)))
            pc_cnt = int(row.get('post_closure_payment_count', 0))
            return min(1.0, (pc_cnt / pay_cnt) / 0.667)
        elif sig == 'Duplicate':
            # Duplicate amount proportion relative to total disbursements, with multi-method boost
            tot_amt = max(1.0, float(row.get('total_payment_amount', 1.0)))
            dup_amt = float(row.get('duplicate_excess_amount', 0.0))
            boost = 1.2 if row.get('duplicate_involves_different_methods', False) else 1.0
            return min(1.0, (dup_amt / tot_amt) * 2.0 * boost)
        elif sig == 'Award Spike':
            # Multiplier intensity scaled above 1.0 (ratio 3.0 -> 1.0)
            ratio = float(row.get('max_payment_to_award_ratio', 1.0))
            return min(1.0, max(0.0, (ratio - 1.0) / 2.0))
        return 0.0
        
    df['norm_strength'] = df.apply(get_strength, axis=1)
    
    # 4. Composite Investigation Priority Score (0.0 to 100.0)
    df['investigation_priority_score'] = (
        financial_weight * df['norm_financial'] +
        persistence_weight * df['norm_persistence'] +
        strength_weight * df['norm_strength']
    ) * 100.0
    
    return df


def rank_investigation_cases(
    features_df: pd.DataFrame,
    top_k: int = 20,
    financial_weight: float = 0.50,
    persistence_weight: float = 0.30,
    strength_weight: float = 0.20,
    feedback_store: Optional[Any] = None,
) -> pd.DataFrame:
    """Rank cases and produce prioritized investigation worklist.

    Uses deterministic tie-breaking:
    1. Highest investigation_priority_score
    2. Highest signal_financial_discrepancy ($)
    3. Highest norm_persistence
    4. Lexicographical case_id (ascending)

    Args:
        features_df: Feature DataFrame for all cases.
        top_k: Number of highest-priority cases to return (default: 20).
        financial_weight: Weight for financial component.
        persistence_weight: Weight for persistence component.
        strength_weight: Weight for evidence strength component.
        feedback_store: Optional FeedbackStore instance to filter documented non-action cases.

    Returns:
        pd.DataFrame: Top-k cases ordered by priority score with assigned rank.
    """
    scored_df = compute_investigation_priority_scores(
        features_df,
        financial_weight=financial_weight,
        persistence_weight=persistence_weight,
        strength_weight=strength_weight,
    )

    # Exclude cases that have been reviewed and administratively cleared if feedback store provided
    if feedback_store is not None:
        excluded_ids = {fb.case_id for fb in feedback_store.get_all_feedback() if fb.action.value == "EXCLUDE_FROM_WORKLIST"}
        if excluded_ids:
            scored_df = scored_df[~scored_df['case_id'].isin(excluded_ids)]
    
    # Deterministic multi-column sort
    ranked = scored_df.sort_values(
        by=['investigation_priority_score', 'signal_financial_discrepancy', 'norm_persistence', 'case_id'],
        ascending=[False, False, False, True]
    ).head(top_k).copy()
    
    ranked.insert(0, 'rank', range(1, len(ranked) + 1))
    return ranked


