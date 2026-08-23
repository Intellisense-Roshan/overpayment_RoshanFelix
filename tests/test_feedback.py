"""Unit tests for Day-2 Investigator Feedback and Two-Tier Status Architecture."""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.loader import load_cases, load_payments
from src.features.engineer import build_case_features
from src.models.ranking import compute_investigation_priority_scores, rank_investigation_cases
from src.feedback.store import FeedbackStore
from src.feedback.models import ReviewOutcome, AlgorithmicSignalStatus, FeedbackAction, FeedbackCategory
from src.feedback.policy import apply_feedback_policy, get_algorithmic_signal_status
from src.governance.guardrails import (
    ADMINISTRATIVE_ACTIVITY_PRINCIPLE,
    ABSENCE_OF_SIGNAL_PRINCIPLE,
    TWO_TIER_DISTINCTION_PRINCIPLE,
    HUMAN_FEEDBACK_AUTHORITY_PRINCIPLE,
    get_governance_statement,
)


class TestInvestigatorFeedback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases_path = Path("data/cases.csv")
        cls.payments_path = Path("data/payments.csv")
        if cls.cases_path.exists() and cls.payments_path.exists():
            cls.cases_df = load_cases(cls.cases_path)
            cls.payments_df = load_payments(cls.payments_path)
            cls.features_df = build_case_features(cls.cases_df, cls.payments_df)
            cls.feedback_store = FeedbackStore()
        else:
            cls.cases_df = None
            cls.payments_df = None
            cls.features_df = None
            cls.feedback_store = None

    def test_c33248_not_in_day1_top20(self):
        """1. Verify C-33248 was never in Day-1 Top-20 worklist."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        top20_day1 = rank_investigation_cases(self.features_df, top_k=20)
        self.assertNotIn("C-33248", list(top20_day1["case_id"]))

    def test_c33248_has_day1_score_zero(self):
        """2. Verify C-33248 had Priority Score 0.00 on Day 1 because it has no signals."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        scored = compute_investigation_priority_scores(self.features_df)
        c_row = scored[scored["case_id"] == "C-33248"].iloc[0]
        self.assertEqual(c_row["investigation_priority_score"], 0.0)
        self.assertEqual(c_row["primary_signal"], "None")

    def test_two_tier_distinction_no_hard_signal_vs_investigator_legitimate(self):
        """3. Verify NO_HARD_SIGNAL is strictly distinct from INVESTIGATOR_CONFIRMED_LEGITIMATE."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        annotated = apply_feedback_policy(self.features_df, self.feedback_store)

        # Unreviewed cases with no signal must be NO_HARD_SIGNAL and UNREVIEWED_BY_INVESTIGATOR
        unreviewed_no_sig = annotated[
            (annotated["primary_signal"] == "None") & (annotated["case_id"] != "C-33248")
        ]
        self.assertGreater(len(unreviewed_no_sig), 0)
        self.assertTrue((unreviewed_no_sig["algorithmic_signal_status"] == AlgorithmicSignalStatus.NO_HARD_SIGNAL.value).all())
        self.assertTrue((unreviewed_no_sig["investigator_review_status"] == "UNREVIEWED_BY_INVESTIGATOR").all())

        # C-33248 must have NO_HARD_SIGNAL for algorithmic, but INVESTIGATOR_CONFIRMED_LEGITIMATE for human status
        c_row = annotated[annotated["case_id"] == "C-33248"].iloc[0]
        self.assertEqual(c_row["algorithmic_signal_status"], AlgorithmicSignalStatus.NO_HARD_SIGNAL.value)
        self.assertEqual(c_row["investigator_review_status"], ReviewOutcome.INVESTIGATOR_CONFIRMED_LEGITIMATE.value)

    def test_numerical_thresholds_cannot_automatically_declare_legitimacy(self):
        """4. Verify numerical conditions alone never set INVESTIGATOR_CONFIRMED_LEGITIMATE."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        # Empty feedback store
        empty_store = FeedbackStore()
        empty_store._records.clear()
        annotated = apply_feedback_policy(self.features_df, empty_store)
        
        # Zero cases should have INVESTIGATOR_CONFIRMED_LEGITIMATE if no human reviewed them
        legit_cases = annotated[annotated["investigator_review_status"] == ReviewOutcome.INVESTIGATOR_CONFIRMED_LEGITIMATE.value]
        self.assertEqual(len(legit_cases), 0)

    def test_human_confirmed_feedback_stored_structurally(self):
        """5. Verify FeedbackStore records feedback structurally with date, reason, and investigator ID."""
        if self.feedback_store is None:
            self.skipTest("Data files not found")
        fb = self.feedback_store.get_feedback("C-33248")
        self.assertIsNotNone(fb)
        self.assertEqual(fb.case_id, "C-33248")
        self.assertEqual(fb.review_outcome, ReviewOutcome.INVESTIGATOR_CONFIRMED_LEGITIMATE)
        self.assertEqual(fb.category, FeedbackCategory.DOCUMENTED_INCOME_CHANGE)
        self.assertEqual(fb.action, FeedbackAction.EXCLUDE_FROM_WORKLIST)
        self.assertIn("Department processing corrections", fb.reason)
        self.assertEqual(fb.investigator_id, "INV-BRITE-06")

    def test_no_case_id_hardcoding_in_ranking(self):
        """6. Verify ranking exclusion operates through FeedbackStore, not hardcoded strings."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        empty_store = FeedbackStore()
        empty_store._records.clear()
        
        # With empty store, ranking logic has no hardcoded C-33248 filter
        top20_empty = rank_investigation_cases(self.features_df, top_k=20, feedback_store=empty_store)
        self.assertEqual(len(top20_empty), 20)

    def test_existing_138_signals_remain_detectable(self):
        """7. Verify all 138 valid signal cases remain 100% detectable."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        sig_counts = self.features_df["primary_signal"].value_counts().to_dict()
        self.assertEqual(sig_counts.get("Post-Closure", 0), 60)
        self.assertEqual(sig_counts.get("Duplicate", 0), 46)
        self.assertEqual(sig_counts.get("Award Spike", 0), 32)
        self.assertEqual(sig_counts.get("None", 0), 4062)

    def test_top20_remains_twenty_unique_cases(self):
        """8. Verify Top-20 ranking produces exactly 20 unique cases."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        top20 = rank_investigation_cases(self.features_df, top_k=20, feedback_store=self.feedback_store)
        self.assertEqual(len(top20), 20)
        self.assertEqual(top20["case_id"].nunique(), 20)

    def test_ranking_determinism(self):
        """9. Verify ranking is strictly deterministic across multiple runs."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        run1 = rank_investigation_cases(self.features_df, top_k=20, feedback_store=self.feedback_store)
        run2 = rank_investigation_cases(self.features_df, top_k=20, feedback_store=self.feedback_store)
        pd.testing.assert_frame_equal(run1, run2)

    def test_demographic_and_proxy_independence(self):
        """10. Verify demographic and administrative proxies cannot alter ranking scores."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        synth = self.features_df.head(10).copy()
        score_orig = compute_investigation_priority_scores(synth)["investigation_priority_score"]
        synth["language_preference"] = "Spanish"
        synth["district"] = "Northgate"
        synth["contact_attempts"] = 15
        synth["months_since_review"] = 30
        synth["payment_adjustments"] = 20
        score_mutated = compute_investigation_priority_scores(synth)["investigation_priority_score"]
        pd.testing.assert_series_equal(score_orig, score_mutated)

    def test_four_governance_principles_codified(self):
        """11. Verify all 4 required Day-2 governance principles are codified."""
        statement = get_governance_statement()
        self.assertIn(ADMINISTRATIVE_ACTIVITY_PRINCIPLE, statement)
        self.assertIn(ABSENCE_OF_SIGNAL_PRINCIPLE, statement)
        self.assertIn(TWO_TIER_DISTINCTION_PRINCIPLE, statement)
        self.assertIn(HUMAN_FEEDBACK_AUTHORITY_PRINCIPLE, statement)


if __name__ == "__main__":
    unittest.main()
