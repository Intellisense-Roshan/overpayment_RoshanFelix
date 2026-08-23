"""Automated unit tests for investigation-priority ranking and scoring guardrails."""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.loader import load_cases, load_payments
from src.features.engineer import build_case_features
from src.models.ranking import compute_investigation_priority_scores, rank_investigation_cases


class TestInvestigationRanking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases_path = Path("data/cases.csv")
        cls.payments_path = Path("data/payments.csv")
        if cls.cases_path.exists() and cls.payments_path.exists():
            cls.cases_df = load_cases(cls.cases_path)
            cls.payments_df = load_payments(cls.payments_path)
            cls.features_df = build_case_features(cls.cases_df, cls.payments_df)
            cls.ranked_top20 = rank_investigation_cases(cls.features_df, top_k=20)
        else:
            cls.cases_df = None
            cls.payments_df = None
            cls.features_df = None
            cls.ranked_top20 = None

    def test_top20_count_and_uniqueness(self):
        """Verify top-20 worklist contains exactly 20 distinct cases."""
        if self.ranked_top20 is None:
            self.skipTest("Data files not found")
        self.assertEqual(len(self.ranked_top20), 20)
        self.assertEqual(self.ranked_top20["case_id"].nunique(), 20)
        self.assertEqual(list(self.ranked_top20["rank"]), list(range(1, 21)))

    def test_ranking_determinism_and_reproducibility(self):
        """Verify ranking is 100% deterministic across multiple runs."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        run1 = rank_investigation_cases(self.features_df, top_k=20)
        run2 = rank_investigation_cases(self.features_df, top_k=20)
        pd.testing.assert_frame_equal(run1, run2)

    def test_all_ranked_cases_exist_in_cases_dataset(self):
        """Verify all ranked cases are legitimate cases in cases.csv."""
        if self.ranked_top20 is None:
            self.skipTest("Data files not found")
        all_case_ids = set(self.cases_df["case_id"])
        for cid in self.ranked_top20["case_id"]:
            self.assertIn(cid, all_case_ids)

    def test_non_signal_cases_receive_zero_priority(self):
        """Verify cases without evidence receive zero priority score and are not promoted."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        scored_all = compute_investigation_priority_scores(self.features_df)
        non_signal = scored_all[scored_all["primary_signal"] == "None"]
        self.assertEqual(len(non_signal), 4062)
        self.assertTrue((non_signal["investigation_priority_score"] == 0.0).all())

    def test_demographic_fields_not_used_in_scoring(self):
        """Verify demographic fields have no mathematical influence on priority score."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        # Permute demographic fields randomly
        permuted_features = self.features_df.copy()
        permuted_features["age_band"] = np.random.permutation(permuted_features["age_band"].values)
        permuted_features["language_preference"] = np.random.permutation(permuted_features["language_preference"].values)
        permuted_features["district"] = np.random.permutation(permuted_features["district"].values)
        permuted_features["tenure"] = np.random.permutation(permuted_features["tenure"].values)

        scored_orig = compute_investigation_priority_scores(self.features_df)
        scored_perm = compute_investigation_priority_scores(permuted_features)

        np.testing.assert_array_almost_equal(
            scored_orig["investigation_priority_score"].values,
            scored_perm["investigation_priority_score"].values
        )

    def test_rejected_features_not_used_in_scoring(self):
        """Verify contact_attempts and months_since_review do not alter scoring."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        permuted_features = self.features_df.copy()
        permuted_features["contact_attempts"] = 999
        permuted_features["months_since_review"] = 999

        scored_orig = compute_investigation_priority_scores(self.features_df)
        scored_perm = compute_investigation_priority_scores(permuted_features)

        np.testing.assert_array_almost_equal(
            scored_orig["investigation_priority_score"].values,
            scored_perm["investigation_priority_score"].values
        )

    def test_signal_classification_integrity_in_top20(self):
        """Verify all top-20 cases belong to one of the three validated signal archetypes."""
        if self.ranked_top20 is None:
            self.skipTest("Data files not found")
        valid_signals = {"Post-Closure", "Duplicate", "Award Spike"}
        for sig in self.ranked_top20["primary_signal"]:
            self.assertIn(sig, valid_signals)

    def test_no_double_counting_of_financial_discrepancy(self):
        """Verify financial discrepancy strictly matches the specific signal excess."""
        if self.ranked_top20 is None:
            self.skipTest("Data files not found")
        for _, row in self.ranked_top20.iterrows():
            sig = row["primary_signal"]
            disc = row["signal_financial_discrepancy"]
            if sig == "Post-Closure":
                self.assertAlmostEqual(disc, row["post_closure_total_amount"])
                self.assertEqual(row["duplicate_excess_amount"], 0.0)
            elif sig == "Duplicate":
                self.assertAlmostEqual(disc, row["duplicate_excess_amount"])
                self.assertEqual(row["post_closure_total_amount"], 0.0)
            elif sig == "Award Spike":
                self.assertAlmostEqual(disc, row["total_excess_above_award"])
                self.assertEqual(row["post_closure_total_amount"], 0.0)
                self.assertEqual(row["duplicate_excess_amount"], 0.0)


if __name__ == "__main__":
    unittest.main()
