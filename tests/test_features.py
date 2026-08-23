"""Automated unit tests for feature engineering, signal detection, and data integrity."""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.loader import load_cases, load_payments
from src.features.engineer import (
    compute_payment_aggregates,
    compute_post_closure_signals,
    compute_duplicate_payment_signals,
    compute_award_ratio_signals,
    compute_payment_derived_adjustments,
    build_case_features,
)


class TestFeatureEngineering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases_path = Path("data/cases.csv")
        cls.payments_path = Path("data/payments.csv")
        if cls.cases_path.exists() and cls.payments_path.exists():
            cls.cases_df = load_cases(cls.cases_path)
            cls.payments_df = load_payments(cls.payments_path)
            cls.features_df = build_case_features(cls.cases_df, cls.payments_df)
        else:
            cls.cases_df = None
            cls.payments_df = None
            cls.features_df = None

    def test_join_integrity_and_row_count(self):
        """Verify all 4,200 cases are preserved in features without row loss or addition."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        self.assertEqual(len(self.features_df), 4200)
        self.assertEqual(self.features_df["case_id"].nunique(), 4200)

    def test_post_closure_calculation_on_synthetic_data(self):
        """Test post-closure detection logic with controlled synthetic cases."""
        synthetic_cases = pd.DataFrame([
            {"case_id": "C-1", "status": "Closed", "closure_month": "2025-08", "monthly_award": 500.0},
            {"case_id": "C-2", "status": "Active", "closure_month": np.nan, "monthly_award": 500.0},
            {"case_id": "C-3", "status": "Closed", "closure_month": "2025-10", "monthly_award": 500.0},
        ])
        synthetic_payments = pd.DataFrame([
            # C-1 payments: 2 valid, 2 post-closure
            {"payment_id": "P-1", "case_id": "C-1", "pay_month": "2025-07", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
            {"payment_id": "P-2", "case_id": "C-1", "pay_month": "2025-08", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
            {"payment_id": "P-3", "case_id": "C-1", "pay_month": "2025-09", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
            {"payment_id": "P-4", "case_id": "C-1", "pay_month": "2025-10", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
            # C-2 payments: Active, no post closure
            {"payment_id": "P-5", "case_id": "C-2", "pay_month": "2025-09", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
            # C-3 payments: Closed in 2025-10, payments in 2025-09, 2025-10 (0 post closure)
            {"payment_id": "P-6", "case_id": "C-3", "pay_month": "2025-09", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
            {"payment_id": "P-7", "case_id": "C-3", "pay_month": "2025-10", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
        ])
        pc_df = compute_post_closure_signals(synthetic_cases, synthetic_payments)
        self.assertEqual(len(pc_df), 1)
        self.assertEqual(pc_df.iloc[0]["case_id"], "C-1")
        self.assertEqual(pc_df.iloc[0]["post_closure_payment_count"], 2)
        self.assertEqual(pc_df.iloc[0]["post_closure_total_amount"], 1000.0)
        self.assertEqual(pc_df.iloc[0]["first_post_closure_month"], "2025-09")
        self.assertEqual(pc_df.iloc[0]["last_post_closure_month"], "2025-10")

    def test_duplicate_detection_on_synthetic_data(self):
        """Test duplicate payment identification on synthetic transactions."""
        synthetic_payments = pd.DataFrame([
            # C-1: identical amounts in same month (duplicate)
            {"payment_id": "P-1", "case_id": "C-1", "pay_month": "2025-08", "amount": 400.0, "method": "Transfer", "adjustment": "N"},
            {"payment_id": "P-2", "case_id": "C-1", "pay_month": "2025-08", "amount": 400.0, "method": "Card", "adjustment": "N"},
            # C-2: different amounts in same month (NOT duplicate)
            {"payment_id": "P-3", "case_id": "C-2", "pay_month": "2025-08", "amount": 400.0, "method": "Transfer", "adjustment": "N"},
            {"payment_id": "P-4", "case_id": "C-2", "pay_month": "2025-08", "amount": 300.0, "method": "Card", "adjustment": "N"},
            # C-3: single payment
            {"payment_id": "P-5", "case_id": "C-3", "pay_month": "2025-08", "amount": 400.0, "method": "Transfer", "adjustment": "N"},
        ])
        dup_df = compute_duplicate_payment_signals(synthetic_payments)
        self.assertEqual(len(dup_df), 1)
        self.assertEqual(dup_df.iloc[0]["case_id"], "C-1")
        self.assertEqual(dup_df.iloc[0]["duplicate_payment_count"], 1)
        self.assertEqual(dup_df.iloc[0]["duplicate_excess_amount"], 400.0)
        self.assertTrue(dup_df.iloc[0]["duplicate_involves_different_methods"])

    def test_ratio_and_spike_calculation(self):
        """Verify ratio calculations and spike thresholds on real data."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        # Known spike case C-31298
        c_spike = self.features_df[self.features_df["case_id"] == "C-31298"].iloc[0]
        self.assertGreater(c_spike["max_payment_to_award_ratio"], 2.5)
        self.assertGreater(c_spike["mean_payment_to_award_ratio"], 2.0)
        self.assertEqual(c_spike["payments_above_1_5x_count"], 6)

    def test_authoritative_payment_adjustments(self):
        """Verify payment adjustments are computed directly from payments.csv."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        total_adj_y = (self.payments_df["adjustment"] == "Y").sum()
        total_feature_adj = self.features_df["actual_adjustment_count"].sum()
        self.assertEqual(total_adj_y, total_feature_adj)
        self.assertEqual(total_adj_y, 3916)

    def test_signal_mutual_exclusivity(self):
        """Verify mutual exclusivity between the three major signal archetypes."""
        if self.features_df is None:
            self.skipTest("Data files not found")
        pc_mask = self.features_df["post_closure_payment_count"] > 0
        dup_mask = self.features_df["duplicate_payment_count"] > 0
        spike_mask = self.features_df["payments_above_1_5x_count"] > 0

        self.assertEqual(pc_mask.sum(), 60)
        self.assertEqual(dup_mask.sum(), 46)
        self.assertEqual(spike_mask.sum(), 32)

        # 0 overlap
        self.assertEqual((pc_mask & dup_mask).sum(), 0)
        self.assertEqual((pc_mask & spike_mask).sum(), 0)
        self.assertEqual((dup_mask & spike_mask).sum(), 0)
        self.assertEqual((pc_mask | dup_mask | spike_mask).sum(), 138)

    def test_zero_and_invalid_award_handling(self):
        """Verify ratio calculations handle 0 or negative awards safely without crashing."""
        synthetic_cases = pd.DataFrame([
            {"case_id": "C-0", "status": "Active", "closure_month": np.nan, "monthly_award": 0.0},
        ])
        synthetic_payments = pd.DataFrame([
            {"payment_id": "P-0", "case_id": "C-0", "pay_month": "2025-07", "amount": 500.0, "method": "Transfer", "adjustment": "N"},
        ])
        ratio_df = compute_award_ratio_signals(synthetic_cases, synthetic_payments)
        self.assertTrue(np.isnan(ratio_df.iloc[0]["max_payment_to_award_ratio"]))


if __name__ == "__main__":
    unittest.main()
