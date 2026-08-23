"""Case Explainability Module for The Overpayment Signal.

Generates concise, evidence-grounded, plain-language explanations for prioritized cases.
Every narrative is strictly traceable to underlying payment transaction records.
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np


STANDARD_DISCLAIMER = (
    "This ranking identifies cases for investigation based on observed payment patterns. "
    "It does not determine whether a payment was improper. Human review is required."
)


def generate_case_explanation(
    case_row: pd.Series,
    case_payments: pd.DataFrame
) -> Dict[str, Any]:
    """Generate structured and plain-language explanation for a single ranked case.

    Args:
        case_row: Row from ranked DataFrame containing case metadata and scores.
        case_payments: Subset of payments.csv corresponding to this case_id.

    Returns:
        Dict[str, Any]: Structured explanation fields.
    """
    case_id = str(case_row['case_id'])
    rank = int(case_row.get('rank', 0))
    signal = str(case_row.get('primary_signal', 'None'))
    priority_score = float(case_row.get('investigation_priority_score', 0.0))
    financial_discrepancy = float(case_row.get('signal_financial_discrepancy', 0.0))
    monthly_award = float(case_row.get('monthly_award', 0.0))
    status = str(case_row.get('status', 'Active'))
    closure_month = str(case_row.get('closure_month', ''))
    
    # Sort payments chronologically
    sorted_pays = case_payments.sort_values(by=['pay_month', 'payment_id']).copy()
    
    evidence_points: List[str] = []
    plain_summary = ""
    relevant_months: List[str] = []
    relevant_amounts: List[str] = []
    relevant_payment_ids: List[str] = []
    
    if signal == 'Post-Closure':
        # Find post-closure payments
        pc_pays = sorted_pays[sorted_pays['pay_month'] > closure_month]
        pc_count = len(pc_pays)
        pc_total = pc_pays['amount'].sum()
        first_pc = pc_pays['pay_month'].min()
        last_pc = pc_pays['pay_month'].max()
        
        relevant_months = pc_pays['pay_month'].tolist()
        relevant_amounts = [f"${a:.2f}" for a in pc_pays['amount']]
        relevant_payment_ids = pc_pays['payment_id'].tolist()
        
        plain_summary = (
            f"Case {case_id} was recorded as closed in {closure_month}, but payments continued "
            f"in {first_pc} through {last_pc}, totaling ${pc_total:,.2f} across {pc_count} payment(s) "
            f"recorded after the case's closure month. This pattern is prioritized for human review."
        )
        evidence_points = [
            f"Case closure officially logged in {closure_month}.",
            f"{pc_count} automated payments were disbursed post-closure between {first_pc} and {last_pc}.",
            f"Total amount disbursed after closure month is ${pc_total:,.2f}.",
            f"Payment transactions involved: {', '.join(relevant_payment_ids)}."
        ]
        status_info = f"Closed (closure month: {closure_month})"
        
    elif signal == 'Duplicate':
        # Find duplicate months and transactions
        month_groups = sorted_pays.groupby('pay_month')
        dup_details = []
        for pm, grp in month_groups:
            if len(grp) > 1:
                amt_counts = grp['amount'].value_counts()
                for amt, cnt in amt_counts.items():
                    if cnt > 1:
                        dup_rows = grp[grp['amount'] == amt]
                        pids = dup_rows['payment_id'].tolist()
                        methods = dup_rows['method'].tolist()
                        dup_details.append({
                            'month': pm,
                            'amount': amt,
                            'count': cnt,
                            'pids': pids,
                            'methods': methods
                        })
                        relevant_months.append(pm)
                        relevant_amounts.extend([f"${amt:.2f}"] * cnt)
                        relevant_payment_ids.extend(pids)
                        
        dup_months_count = len(dup_details)
        total_dup_excess = sum(d['amount'] * (d['count'] - 1) for d in dup_details)
        dup_months_str = ", ".join([d['month'] for d in dup_details])
        
        plain_summary = (
            f"Case {case_id} received multiple identical disbursements within the same billing month. "
            f"This occurred across {dup_months_count} separate month(s) ({dup_months_str}), producing "
            f"${total_dup_excess:,.2f} in duplicate excess funds that warrant review."
        )
        evidence_points = [
            f"Identical duplicate payments recorded in {dup_months_count} separate month(s): {dup_months_str}.",
            f"Total duplicate excess amount is ${total_dup_excess:,.2f} across {len(relevant_payment_ids)} duplicate transaction records.",
            f"Payment methods used in duplicate months: {', '.join(sorted({m for d in dup_details for m in d['methods']}))}.",
            f"Duplicate transaction IDs: {', '.join(relevant_payment_ids)}."
        ]
        status_info = f"{status} (Active case with multiple within-month duplicate disbursements)"
        
    elif signal == 'Award Spike':
        sorted_pays['ratio'] = sorted_pays['amount'] / monthly_award
        max_pay = sorted_pays.loc[sorted_pays['ratio'].idxmax()]
        max_ratio = max_pay['ratio']
        pays_above_1_5x = (sorted_pays['ratio'] > 1.5).sum()
        pays_above_2x = (sorted_pays['ratio'] > 2.0).sum()
        total_excess = np.maximum(0.0, sorted_pays['amount'] - monthly_award).sum()
        
        relevant_months = sorted_pays['pay_month'].tolist()
        relevant_amounts = [f"${a:.2f}" for a in sorted_pays['amount']]
        relevant_payment_ids = sorted_pays['payment_id'].tolist()
        
        spike_desc = f"{pays_above_2x} exceeding twice the award" if pays_above_2x > 0 else f"{pays_above_1_5x} exceeding 1.5x the award"
        
        plain_summary = (
            f"Case {case_id} received {len(sorted_pays)} payments during the observation period, "
            f"with {spike_desc} relative to its recorded monthly award of ${monthly_award:,.2f}. "
            f"The largest payment was ${max_pay['amount']:,.2f} ({max_ratio:.2f}x award), creating "
            f"${total_excess:,.2f} in calculated financial discrepancy relative to the authorized award."
        )
        evidence_points = [
            f"Authorized monthly award is ${monthly_award:,.2f}.",
            f"{pays_above_1_5x} of {len(sorted_pays)} observed payments exceeded 1.5x the authorized monthly award.",
            f"Peak single-month payment was ${max_pay['amount']:,.2f} in {max_pay['pay_month']} ({max_ratio:.2f}x the award, Transaction ID: {max_pay['payment_id']}).",
            f"Total cumulative excess above authorized award across all months is ${total_excess:,.2f}."
        ]
        status_info = f"{status}"

    else:
        fb_status = case_row.get('investigator_review_status', 'UNREVIEWED_BY_INVESTIGATOR')
        fb_reason = case_row.get('investigator_feedback_reason', '')
        if fb_status == 'INVESTIGATOR_CONFIRMED_LEGITIMATE':
            plain_summary = f"Case {case_id}: INVESTIGATOR CONFIRMED LEGITIMATE based on human caseworker audit ({fb_reason})."
            evidence_points = [
                "Human caseworker determination: INVESTIGATOR_CONFIRMED_LEGITIMATE.",
                f"Audited Context: {fb_reason}"
            ]
        elif fb_status == 'CONFIRMED_DISCREPANCY':
            plain_summary = f"Case {case_id}: CONFIRMED DISCREPANCY based on human caseworker audit."
            evidence_points = ["Human caseworker determination: CONFIRMED_DISCREPANCY."]
        else:
            plain_summary = f"Case {case_id}: NO HARD SIGNAL DETECTED in payment records."
            evidence_points = [
                "No post-closure continuation, duplicate disbursement, or severe award multiplier spike detected.",
                "Absence of an algorithmic signal is not proof of legal legitimacy."
            ]
        status_info = status


    return {
        'rank': rank,
        'case_id': case_id,
        'primary_signal': signal,
        'investigation_priority_score': round(priority_score, 2),
        'signal_financial_discrepancy': round(financial_discrepancy, 2),
        'monthly_award': monthly_award,
        'status_info': status_info,
        'plain_language_summary': plain_summary,
        'evidence_points': evidence_points,
        'relevant_months': ", ".join(relevant_months),
        'relevant_amounts': ", ".join(relevant_amounts),
        'relevant_payment_ids': ", ".join(relevant_payment_ids),
        'disclaimer': STANDARD_DISCLAIMER
    }


def generate_top20_investigation_report(
    top20_df: pd.DataFrame,
    payments_df: pd.DataFrame
) -> Tuple[pd.DataFrame, str]:
    """Generate both machine-readable DataFrame and formatted Markdown report for Top 20 cases.

    Args:
        top20_df: Ranked DataFrame containing top 20 cases.
        payments_df: Full payments DataFrame.

    Returns:
        Tuple[pd.DataFrame, str]: (explanations_df, markdown_report)
    """
    explanations = []
    
    for _, row in top20_df.iterrows():
        cid = row['case_id']
        c_pays = payments_df[payments_df['case_id'] == cid]
        exp = generate_case_explanation(row, c_pays)
        explanations.append(exp)
        
    exp_df = pd.DataFrame(explanations)
    
    # Format comprehensive markdown report
    md_lines = [
        "# Top-20 Investigation Worklist & Case Explanations Report",
        "",
        "> **GOVERNANCE & AUDIT NOTICE:**",
        f"> {STANDARD_DISCLAIMER}",
        "",
        "---",
        "",
        "## Summary of Top-20 Priority Worklist",
        "",
        f"- **Total Priority Cases**: {len(exp_df)}",
        f"- **Total Financial Discrepancy Represented**: ${exp_df['signal_financial_discrepancy'].sum():,.2f}",
        f"- **Signal Breakdown**: { {k: int(v) for k, v in exp_df['primary_signal'].value_counts().items()} }",
        "",
        "---",
        "",
        "## Detailed Case Explanations",
        ""
    ]
    
    for exp in explanations:
        md_lines.append(f"### Rank {exp['rank']}: Case {exp['case_id']}")
        md_lines.append(f"- **Primary Signal**: `{exp['primary_signal']}`")
        md_lines.append(f"- **Investigation Priority Score**: **{exp['investigation_priority_score']:.2f} / 100.0**")
        md_lines.append(f"- **Calculated Financial Discrepancy**: **${exp['signal_financial_discrepancy']:,.2f}**")
        md_lines.append(f"- **Case Status**: {exp['status_info']}")
        md_lines.append(f"- **Authorized Monthly Award**: ${exp['monthly_award']:,.2f}")
        md_lines.append("")
        md_lines.append(f"**Plain-Language Casework Summary:**")
        md_lines.append(f"> {exp['plain_language_summary']}")
        md_lines.append("")
        md_lines.append("**Key Evidence Points:**")
        for ep in exp['evidence_points']:
            md_lines.append(f"- {ep}")
        md_lines.append("")
        md_lines.append(f"- **Relevant Payment Months**: `{exp['relevant_months']}`")
        md_lines.append(f"- **Relevant Transaction IDs**: `{exp['relevant_payment_ids']}`")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
    return exp_df, "\n".join(md_lines)

