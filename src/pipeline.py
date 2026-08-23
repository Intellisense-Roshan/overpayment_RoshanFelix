"""End-to-End Orchestration Pipeline and CLI for The Overpayment Signal.

Executes data validation, feature engineering, deterministic investigation ranking,
plain-language case explanation generation, and demographic fairness auditing.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from src.data.loader import load_cases, load_payments
from src.data.loader import PROJECT_ROOT
from src.features.engineer import build_case_features
from src.models.ranking import rank_investigation_cases, compute_investigation_priority_scores
from src.explainability.explainer import generate_top20_investigation_report
from src.fairness.metrics import evaluate_demographic_fairness, generate_fairness_markdown_report
from src.governance.guardrails import get_governance_statement


def parse_args():
    parser = argparse.ArgumentParser(
        description="The Overpayment Signal — Investigation Prioritization & Audit Pipeline"
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=PROJECT_ROOT / "data" / "cases.csv",
        help="Path to cases.csv (default: data/cases.csv)",
    )
    parser.add_argument(
        "--payments",
        type=Path,
        default=PROJECT_ROOT / "data" / "payments.csv",
        help="Path to payments.csv (default: data/payments.csv)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
        help="Number of top priority cases to generate (default: 20)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs",
        help="Directory to save output reports and CSVs (default: outputs)",
    )
    parser.add_argument(
        "--governance-only",
        action="store_true",
        help="Display the model non-automation governance statement and exit.",
    )
    return parser.parse_args()


def run_pipeline(
    cases_path: Path = PROJECT_ROOT / "data" / "cases.csv",
    payments_path: Path = PROJECT_ROOT / "data" / "payments.csv",
    top_k: int = 20,
    output_dir: Path = PROJECT_ROOT / "outputs",
) -> dict:
    """Execute full end-to-end pipeline.

    Args:
        cases_path: Path to cases CSV.
        payments_path: Path to payments CSV.
        top_k: Number of prioritized cases.
        output_dir: Destination folder for artifacts.

    Returns:
        dict: Summary statistics and paths of generated artifacts.
    """
    print("=" * 80)
    print("THE OVERPAYMENT SIGNAL -- INVESTIGATION PRIORITIZATION PIPELINE")
    print("=" * 80)

    
    # 1. Ingestion & Validation
    print(f"\n[1/5] Ingesting datasets...")
    print(f"      Cases file    : {cases_path}")
    print(f"      Payments file : {payments_path}")
    cases_df = load_cases(cases_path)
    payments_df = load_payments(payments_path)
    print(f"      [+] Loaded {len(cases_df):,} cases and {len(payments_df):,} payment transactions.")
    
    # Relational integrity check
    case_ids_cases = set(cases_df['case_id'])
    case_ids_pays = set(payments_df['case_id'])
    if case_ids_cases != case_ids_pays:
        raise ValueError("Referential integrity mismatch between cases.csv and payments.csv")
    print("      [+] 100% case-level referential integrity verified.")
    
    # 2. Feature Engineering & Signal Detection
    print(f"\n[2/5] Engineering features and detecting signal archetypes...")
    features_df = build_case_features(cases_df, payments_df)
    sig_counts = features_df['primary_signal'].value_counts().to_dict()
    print(f"      [+] Signal detection complete: {sig_counts}")
        
    # 3. Investigation Priority Ranking & Feedback Policy
    print(f"\n[3/6] Applying investigator feedback policy and ranking Top {top_k} worklist...")
    from src.feedback.store import FeedbackStore
    from src.feedback.policy import apply_feedback_policy
    
    feedback_store = FeedbackStore()
    annotated_features = apply_feedback_policy(features_df, feedback_store)
    top_k_df = rank_investigation_cases(annotated_features, top_k=top_k, feedback_store=feedback_store)
    scored_all_df = compute_investigation_priority_scores(annotated_features)
    total_discrepancy = float(top_k_df['signal_financial_discrepancy'].sum())
    print(f"      [+] Feedback store active with {len(feedback_store.get_all_feedback())} documented review outcomes.")
    print(f"      [+] Top {top_k} worklist produced.")
    print(f"      [+] Total calculated financial discrepancy in Top {top_k}: ${total_discrepancy:,.2f}")
    print(f"      [+] Signal breakdown in Top {top_k}: {top_k_df['primary_signal'].value_counts().to_dict()}")
    
    # 4. Case Explainability & Caseworker Report
    print(f"\n[4/6] Generating plain-language case explanations and audit report...")
    exp_df, md_report = generate_top20_investigation_report(top_k_df, payments_df)
    print(f"      [+] Generated {len(exp_df)} structured case narratives with transaction IDs.")
    
    # 5. Demographic Fairness Audit
    print(f"\n[5/6] Auditing demographic fairness across 4 dimensions...")
    fairness_df = evaluate_demographic_fairness(cases_df, top_k_df)
    fairness_report_md = generate_fairness_markdown_report(cases_df, top_k_df, scored_all_df)
    print(f"      [+] Demographic audit complete across age_band, language_preference, district, tenure.")
    
    # 6. Save Artifacts & Feedback Log
    print(f"\n[6/6] Saving output artifacts and investigator feedback log...")
    output_dir.mkdir(parents=True, exist_ok=True)
    worklist_path = output_dir / "top20_worklist.csv"
    explanations_path = output_dir / "top20_explanations.csv"
    investigator_report_path = output_dir / "top20_investigator_report.md"
    fairness_summary_path = output_dir / "fairness_summary.csv"
    fairness_report_path = output_dir / "fairness_report.md"
    feedback_log_path = output_dir / "investigator_feedback_log.csv"
    
    top_k_df.to_csv(worklist_path, index=False)
    exp_df.to_csv(explanations_path, index=False)
    with open(investigator_report_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    fairness_df.to_csv(fairness_summary_path, index=False)
    with open(fairness_report_path, "w", encoding="utf-8") as f:
        f.write(fairness_report_md)
    feedback_store.to_dataframe().to_csv(feedback_log_path, index=False)
        
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION COMPLETE -- OUTPUT ARTIFACTS SAVED:")
    print("=" * 80)
    print(f"  1. Priority Worklist       : {worklist_path.resolve()}")
    print(f"  2. Structured Explanations : {explanations_path.resolve()}")
    print(f"  3. Investigator Report     : {investigator_report_path.resolve()}")
    print(f"  4. Fairness Summary        : {fairness_summary_path.resolve()}")
    print(f"  5. Fairness Audit Report   : {fairness_report_path.resolve()}")
    print(f"  6. Feedback Review Log     : {feedback_log_path.resolve()}")
    print("=" * 80)
    
    return {
        "top_k_cases": len(top_k_df),
        "total_discrepancy": total_discrepancy,
        "signal_breakdown": top_k_df['primary_signal'].value_counts().to_dict(),
        "worklist_path": worklist_path,
        "explanations_path": explanations_path,
        "investigator_report_path": investigator_report_path,
        "fairness_summary_path": fairness_summary_path,
        "fairness_report_path": fairness_report_path,
        "feedback_log_path": feedback_log_path,
    }


def main():
    args = parse_args()

    if args.governance_only:
        print(get_governance_statement())
        sys.exit(0)

    try:
        run_pipeline(
            cases_path=args.cases,
            payments_path=args.payments,
            top_k=args.top_k,
            output_dir=args.output_dir,
        )
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

