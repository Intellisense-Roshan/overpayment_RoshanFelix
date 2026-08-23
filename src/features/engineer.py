"""Feature extraction and signal engineering module for The Overpayment Signal.

This module computes case-level features directly from cases.csv and payments.csv,
isolating three distinct improper-payment signal archetypes:
1. Post-closure continuing disbursements
2. In-month duplicate payment disbursements
3. Severe payment-to-award multiplier spikes

It also computes payment-derived adjustment metrics (avoiding unreliable case-level counters)
and strict financial discrepancy measures.
"""
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np


def compute_payment_aggregates(payments_df: pd.DataFrame) -> pd.DataFrame:
    """Compute base summary statistics per case from payments.csv.

    Args:
        payments_df: Raw payments DataFrame.

    Returns:
        pd.DataFrame: Case-level payment statistics.
    """
    agg_df = payments_df.groupby('case_id').agg(
        total_payment_amount=('amount', 'sum'),
        payment_count=('payment_id', 'count'),
        average_payment=('amount', 'mean'),
        maximum_payment=('amount', 'max'),
        minimum_payment=('amount', 'min'),
        payment_amount_variability=('amount', 'std'),
        months_with_payments=('pay_month', 'nunique')
    ).reset_index()
    # Replace NaN standard deviation with 0.0 for single-payment cases
    agg_df['payment_amount_variability'] = agg_df['payment_amount_variability'].fillna(0.0)
    return agg_df


def compute_post_closure_signals(cases_df: pd.DataFrame, payments_df: pd.DataFrame) -> pd.DataFrame:
    """Identify and quantify payments occurring strictly after case closure_month.

    Args:
        cases_df: Cases DataFrame containing status and closure_month.
        payments_df: Payments DataFrame.

    Returns:
        pd.DataFrame: Post-closure features indexed by case_id.
    """
    closed_cases = cases_df[cases_df['status'] == 'Closed'][['case_id', 'closure_month']].dropna(subset=['closure_month'])
    merged = payments_df.merge(closed_cases, on='case_id', how='inner')
    
    # Strictly post-closure payments
    post_closure_pays = merged[merged['pay_month'] > merged['closure_month']]
    
    if len(post_closure_pays) > 0:
        pc_agg = post_closure_pays.groupby('case_id').agg(
            post_closure_payment_count=('payment_id', 'count'),
            post_closure_total_amount=('amount', 'sum'),
            post_closure_month_count=('pay_month', 'nunique'),
            first_post_closure_month=('pay_month', 'min'),
            last_post_closure_month=('pay_month', 'max')
        ).reset_index()
    else:
        pc_agg = pd.DataFrame(columns=[
            'case_id', 'post_closure_payment_count', 'post_closure_total_amount',
            'post_closure_month_count', 'first_post_closure_month', 'last_post_closure_month'
        ])
    return pc_agg


def compute_duplicate_payment_signals(payments_df: pd.DataFrame) -> pd.DataFrame:
    """Detect cases with multiple identical payment amounts within the same pay_month.

    Args:
        payments_df: Payments DataFrame.

    Returns:
        pd.DataFrame: Duplicate payment features indexed by case_id.
    """
    month_groups = payments_df.groupby(['case_id', 'pay_month'])
    dup_rows = []
    
    for (case_id, pay_month), group in month_groups:
        if len(group) > 1:
            amt_counts = group['amount'].value_counts()
            for amt, count in amt_counts.items():
                if count > 1:
                    excess_count = count - 1
                    methods = list(group[group['amount'] == amt]['method'].unique())
                    dup_rows.append({
                        'case_id': case_id,
                        'pay_month': pay_month,
                        'dup_excess_count': excess_count,
                        'dup_excess_amount': amt * excess_count,
                        'is_multi_method': len(methods) > 1
                    })
                    
    if dup_rows:
        dup_df = pd.DataFrame(dup_rows)
        dup_agg = dup_df.groupby('case_id').agg(
            duplicate_payment_count=('dup_excess_count', 'sum'),
            duplicate_excess_amount=('dup_excess_amt' if 'dup_excess_amt' in dup_df else 'dup_excess_amount', 'sum'),
            duplicate_month_count=('pay_month', 'nunique'),
            duplicate_involves_different_methods=('is_multi_method', 'any')
        ).reset_index()
    else:
        dup_agg = pd.DataFrame(columns=[
            'case_id', 'duplicate_payment_count', 'duplicate_excess_amount',
            'duplicate_month_count', 'duplicate_involves_different_methods'
        ])
    return dup_agg


def compute_award_ratio_signals(cases_df: pd.DataFrame, payments_df: pd.DataFrame) -> pd.DataFrame:
    """Compute payment-to-award ratios and severe multiplier spike indicators.

    Args:
        cases_df: Cases DataFrame containing monthly_award.
        payments_df: Payments DataFrame.

    Returns:
        pd.DataFrame: Award ratio features per case.
    """
    merged = payments_df.merge(cases_df[['case_id', 'monthly_award']], on='case_id', how='left')
    
    # Guard against invalid / zero awards
    safe_award = np.where(merged['monthly_award'] > 0, merged['monthly_award'], np.nan)
    merged['pay_to_award_ratio'] = merged['amount'] / safe_award
    merged['excess_above_award'] = np.maximum(0.0, merged['amount'] - merged['monthly_award'])
    
    ratio_agg = merged.groupby('case_id').agg(
        max_payment_to_award_ratio=('pay_to_award_ratio', 'max'),
        mean_payment_to_award_ratio=('pay_to_award_ratio', 'mean'),
        total_excess_above_award=('excess_above_award', 'sum'),
        average_excess_above_award=('excess_above_award', 'mean'),
        payments_above_1_5x_count=('pay_to_award_ratio', lambda x: (x > 1.5).sum()),
        payments_above_2x_count=('pay_to_award_ratio', lambda x: (x > 2.0).sum())
    ).reset_index()
    
    return ratio_agg


def compute_payment_derived_adjustments(payments_df: pd.DataFrame) -> pd.DataFrame:
    """Compute authoritative adjustment features directly from payments.csv.

    Bypasses the unreliable cases.csv payment_adjustments field.

    Args:
        payments_df: Payments DataFrame.

    Returns:
        pd.DataFrame: Adjustment features per case.
    """
    # Base adjustment counts
    adj_agg = payments_df.groupby('case_id').agg(
        actual_adjustment_count=('adjustment', lambda x: (x == 'Y').sum()),
        adjustment_rate=('adjustment', lambda x: (x == 'Y').mean())
    ).reset_index()
    
    # Months with adjustments
    adj_pays = payments_df[payments_df['adjustment'] == 'Y']
    if len(adj_pays) > 0:
        adj_month_agg = adj_pays.groupby('case_id').agg(
            adjustment_month_count=('pay_month', 'nunique'),
            adjustment_amount_total=('amount', 'sum')
        ).reset_index()
        adj_agg = adj_agg.merge(adj_month_agg, on='case_id', how='left')
    else:
        adj_agg['adjustment_month_count'] = 0
        adj_agg['adjustment_amount_total'] = 0.0
        
    adj_agg['adjustment_month_count'] = adj_agg['adjustment_month_count'].fillna(0).astype(int)
    adj_agg['adjustment_amount_total'] = adj_agg['adjustment_amount_total'].fillna(0.0)
    return adj_agg


def build_case_features(cases_df: pd.DataFrame, payments_df: pd.DataFrame) -> pd.DataFrame:
    """Extract all validated features and signal indicators for each case.

    Args:
        cases_df: Raw cases DataFrame.
        payments_df: Raw payments DataFrame.

    Returns:
        pd.DataFrame: Comprehensive feature table with 4,200 rows.
    """
    cases = cases_df.copy()
    
    # 1. Base payment aggregates
    pay_agg = compute_payment_aggregates(payments_df)
    
    # 2. Award ratios and spikes
    ratio_agg = compute_award_ratio_signals(cases, payments_df)
    
    # 3. Post-closure continuation signals
    pc_agg = compute_post_closure_signals(cases, payments_df)
    
    # 4. Same-month duplicate payment signals
    dup_agg = compute_duplicate_payment_signals(payments_df)
    
    # 5. Payment-derived adjustments
    adj_agg = compute_payment_derived_adjustments(payments_df)
    
    # 6. Expected active months & authorized expected total award
    def calculate_expected_months(row):
        if row['status'] == 'Closed' and pd.notna(row['closure_month']):
            try:
                m = int(str(row['closure_month']).split('-')[1])
                return max(1, m - 6) # July(7)->1, Aug(8)->2, etc.
            except (ValueError, IndexError):
                return 6
        return 6
        
    cases['expected_active_months'] = cases.apply(calculate_expected_months, axis=1)
    cases['expected_total_award'] = cases['monthly_award'] * cases['expected_active_months']
    
    # Merge all feature tables
    features = cases.merge(pay_agg, on='case_id', how='left')
    features = features.merge(ratio_agg, on='case_id', how='left')
    features = features.merge(pc_agg, on='case_id', how='left')
    features = features.merge(dup_agg, on='case_id', how='left')
    features = features.merge(adj_agg, on='case_id', how='left')
    
    # Fill missing signal values with zeros
    features['post_closure_payment_count'] = features['post_closure_payment_count'].fillna(0).astype(int)
    features['post_closure_total_amount'] = features['post_closure_total_amount'].fillna(0.0)
    features['post_closure_month_count'] = features['post_closure_month_count'].fillna(0).astype(int)
    
    features['duplicate_payment_count'] = features['duplicate_payment_count'].fillna(0).astype(int)
    features['duplicate_excess_amount'] = features['duplicate_excess_amount'].fillna(0.0)
    features['duplicate_month_count'] = features['duplicate_month_count'].fillna(0).astype(int)
    features['duplicate_involves_different_methods'] = features['duplicate_involves_different_methods'].fillna(False).astype(bool)
    
    # Calculate net discrepancy (Actual total paid minus expected authorized entitlement)
    features['net_excess_paid'] = features['total_payment_amount'] - features['expected_total_award']
    
    # Categorize primary candidate signal
    def assign_primary_signal(row):
        if row['post_closure_payment_count'] > 0:
            return 'Post-Closure'
        elif row['duplicate_payment_count'] > 0:
            return 'Duplicate'
        elif row['payments_above_1_5x_count'] > 0:
            return 'Award Spike'
        return 'None'
        
    features['primary_signal'] = features.apply(assign_primary_signal, axis=1)
    
    return features

