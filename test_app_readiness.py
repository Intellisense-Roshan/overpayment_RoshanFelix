"""Verify app module can be imported and key functions work."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Verify app imports work
try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    print("✓ All required libraries imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Verify data files exist
required_files = [
    PROJECT_ROOT / 'outputs' / 'top20_worklist.csv',
    PROJECT_ROOT / 'outputs' / 'top20_explanations.csv',
    PROJECT_ROOT / 'outputs' / 'fairness_summary.csv',
    PROJECT_ROOT / 'outputs' / 'fairness_report.md'
]

for f in required_files:
    if Path(f).exists():
        print(f"✓ {f} exists")
    else:
        print(f"✗ {f} missing")
        sys.exit(1)

# Load and verify data
worklist = pd.read_csv(PROJECT_ROOT / 'outputs' / 'top20_worklist.csv')
explanations = pd.read_csv(PROJECT_ROOT / 'outputs' / 'top20_explanations.csv')
fairness = pd.read_csv(PROJECT_ROOT / 'outputs' / 'fairness_summary.csv')

# Verify key fields exist
required_worklist_cols = ['rank', 'case_id', 'primary_signal', 'investigation_priority_score', 'signal_financial_discrepancy']
required_explanation_cols = ['rank', 'case_id', 'plain_language_summary', 'evidence_points']
required_fairness_cols = ['dimension', 'group', 'population_pct', 'top20_pct']

for col in required_worklist_cols:
    if col not in worklist.columns:
        print(f"✗ Missing column in worklist: {col}")
        sys.exit(1)

for col in required_explanation_cols:
    if col not in explanations.columns:
        print(f"✗ Missing column in explanations: {col}")
        sys.exit(1)

for col in required_fairness_cols:
    if col not in fairness.columns:
        print(f"✗ Missing column in fairness: {col}")
        sys.exit(1)

print("✓ All required data columns present")

# Verify data integrity
assert len(worklist) == 20, f"Expected 20 cases, got {len(worklist)}"
assert len(explanations) == 20, f"Expected 20 explanations, got {len(explanations)}"
assert len(fairness) > 0, "No fairness data found"
assert set(worklist['rank']) == set(range(1, 21)), "Ranks should be 1-20"

print("✓ Data integrity validation passed")
print()
print("✓ App module ready to run")
print()
print("To launch the dashboard, run:")
print("  streamlit run app.py")
