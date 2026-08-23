"""Automated unit tests for fairness evaluation and demographic parity metrics."""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.loader import load_cases, load_payments
from src.features.engineer import build_case_features
from src.models.ranking import rank_investigation_cases
from src.fairness.metrics import (
    compute_population_baselines,
    evaluate_demographic_fairness,
    DEFAULT_DEMOGRAPHIC_DIMENSIONS
)


class TestFairnessAuditing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases_path = Path("data/cases.csv")
        cls.payments_path = Path("data/payments.csv")
        if cls.cases_path.exists() and cls.payments_path.exists():
            cls.cases_df = load_cases(cls.cases_path)
            cls.payments_df = load_payments(cls.payments_path)
            cls.features_df = build_case_features(cls.cases_df, cls.payments_df)
            cls.top20_df = rank_investigation_cases(cls.features_df, top_k=20)
            cls.audit_summary = evaluate_demographic_fairness(cls.cases_df, cls.top20_df)
        else:
            cls.cases_df = None
            cls.payments_df = None
            cls.features_df = None
            cls.top20_df = None
            cls.audit_summary = None

    def test_population_counts_sum_to_4200(self):
        """Verify population counts across all demographic dimensions sum to 4,200."""
        if self.cases_df is None:
            self.skipTest("Data files not found")
        baselines = compute_population_baselines(self.cases_df)
        for dim, b_df in baselines.items():
            self.assertEqual(b_df["population_count"].sum(), 4200)
            self.assertAlmostEqual(b_df["population_pct"].sum(), 100.0, places=1)

    def test_top20_counts_sum_to_20(self):
        """Verify top-20 counts across all demographic dimensions sum to 20."""
        if self.audit_summary is None:
            self.skipTest("Data files not found")
        for dim in DEFAULT_DEMOGRAPHIC_DIMENSIONS:
            sub = self.audit_summary[self.audit_summary["dimension"] == dim]
            self.assertEqual(sub["top20_count"].sum(), 20)
            self.assertAlmostEqual(sub["top20_pct"].sum(), 100.0, places=1)

    def test_representation_ratio_calculation(self):
        """Verify representation ratio math: top20_pct / population_pct."""
        if self.audit_summary is None:
            self.skipTest("Data files not found")
        for _, row in self.audit_summary.iterrows():
            expected_ratio = round(row["top20_pct"] / row["population_pct"], 2)
            self.assertAlmostEqual(row["representation_ratio"], expected_ratio, places=2)

    def test_selection_rate_calculation(self):
        """Verify selection rate math: top20_count / population_count."""
        if self.audit_summary is None:
            self.skipTest("Data files not found")
        for _, row in self.audit_summary.iterrows():
            expected_rate = round(row["top20_count"] / row["population_count"], 6)
            self.assertAlmostEqual(row["selection_rate"], expected_rate, places=6)

    def test_four_required_dimensions_present(self):
        """Verify audit covers exactly age_band, language_preference, district, and tenure."""
        if self.audit_summary is None:
            self.skipTest("Data files not found")
        dimensions_in_summary = set(self.audit_summary["dimension"].unique())
        self.assertEqual(dimensions_in_summary, set(DEFAULT_DEMOGRAPHIC_DIMENSIONS))


if __name__ == "__main__":
    unittest.main()
