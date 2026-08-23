"""Quick validation that app can load all data files."""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Test loading all data files used by the app
worklist = pd.read_csv(PROJECT_ROOT / 'outputs' / 'top20_worklist.csv')
explanations = pd.read_csv(PROJECT_ROOT / 'outputs' / 'top20_explanations.csv')
fairness = pd.read_csv(PROJECT_ROOT / 'outputs' / 'fairness_summary.csv')

print(f'✓ Top-20 Worklist: {len(worklist)} cases loaded')
print(f'✓ Explanations: {len(explanations)} cases loaded')
print(f'✓ Fairness Data: {len(fairness)} rows loaded')
print()
print(f'  Worklist columns: {list(worklist.columns)[:6]}...')
print(f'  Explanations columns: {list(explanations.columns)[:6]}...')
print(f'  Fairness dimensions: {fairness["dimension"].unique().tolist()}')
print()
print('✓ Dashboard data validation passed')
