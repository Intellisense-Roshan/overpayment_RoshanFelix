"""Data ingestion and validation module.

Handles loading of cases and payments data without mutating source files.
Encapsulates policy manual reference values (e.g. household needs figures).
"""
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

# Policy manual monthly needs schedule by household size
NEEDS_FIGURES = {
    1: 1240,
    2: 1670,
    3: 2000,
    4: 2330,
    5: 2660,
    6: 2990,
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


def load_cases(path: Optional[Path] = None) -> pd.DataFrame:
    """Load cases dataset without modifying source file.

    Args:
        path: Path to cases.csv. Defaults to data/cases.csv.

    Returns:
        pd.DataFrame: Cases dataset.
    """
    csv_path = path or DEFAULT_DATA_DIR / "cases.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Cases file not found at {csv_path}")
    df = pd.read_csv(csv_path)
    return df


def load_payments(path: Optional[Path] = None) -> pd.DataFrame:
    """Load payments dataset without modifying source file.

    Args:
        path: Path to payments.csv. Defaults to data/payments.csv.

    Returns:
        pd.DataFrame: Payments dataset.
    """
    csv_path = path or DEFAULT_DATA_DIR / "payments.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Payments file not found at {csv_path}")
    df = pd.read_csv(csv_path)
    return df


def load_all_data(data_dir: Optional[Path] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load both cases and payments datasets.

    Args:
        data_dir: Path to directory containing CSVs.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (cases_df, payments_df)
    """
    base = data_dir or DEFAULT_DATA_DIR
    cases_df = load_cases(base / "cases.csv")
    payments_df = load_payments(base / "payments.csv")
    return cases_df, payments_df
