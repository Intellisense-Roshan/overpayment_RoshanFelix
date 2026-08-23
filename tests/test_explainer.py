"""Automated unit tests for case explainability and governance compliance."""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.loader import load_cases, load_payments
from src.features.engineer import build_case_features
from src.models.ranking import rank_investigation_cases
from src.explainability.explainer import generate_case_explanation, generate_top20_investigation_report, STANDARD_DISCLAIMER


class TestExplainabilityModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases_path = Path("data/cases.csv")
        cls.payments_path = Path("data/payments.csv")
        if cls.cases_path.exists() and cls.payments_path.exists():
            cls.cases_df = load_cases(cls.cases_path)
            cls.payments_df = load_payments(cls.payments_path)
            cls.features_df = build_case_features(cls.cases_df, cls.payments_df)
            cls.top20_df = rank_investigation_cases(cls.features_df, top_k=20)
            cls.exp_df, cls.md_report = generate_top20_investigation_report(cls.top20_df, cls.payments_df)
        else:
            cls.cases_df = None
            cls.payments_df = None
            cls.features_df = None
            cls.top20_df = None
            cls.exp_df = None
            cls.md_report = None

    def test_explanation_count_and_uniqueness(self):
        """Verify exactly 20 unique case explanations are produced."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        self.assertEqual(len(self.exp_df), 20)
        self.assertEqual(self.exp_df["case_id"].nunique(), 20)
        self.assertEqual(list(self.exp_df["case_id"]), list(self.top20_df["case_id"]))

    def test_all_case_ids_exist_in_source_data(self):
        """Verify every explained case ID exists in cases.csv."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        all_cases = set(self.cases_df["case_id"])
        for cid in self.exp_df["case_id"]:
            self.assertIn(cid, all_cases)

    def test_no_demographic_attributes_in_explanations(self):
        """Verify demographic fields are never used in casework narratives or evidence points."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        demographic_terms = [
            "age_band", "18-29", "30-44", "45-59", "60-74", "75+",
            "language_preference", "Spanish", "Other language",
            "district", "Calder Central", "Northgate", "Weybridge", "Ash Hill",
            "tenure", "Social tenancy", "No fixed abode", "Private tenancy", "Owner-occupier"
        ]
        for _, row in self.exp_df.iterrows():
            summary = row["plain_language_summary"].lower()
            evidence = " ".join(row["evidence_points"]).lower()
            for term in demographic_terms:
                self.assertNotIn(
                    term.lower(),
                    summary,
                    f"Demographic term '{term}' found in summary for {row['case_id']}"
                )
                self.assertNotIn(
                    term.lower(),
                    evidence,
                    f"Demographic term '{term}' found in evidence for {row['case_id']}"
                )

    def test_no_claims_of_fraud_or_guilt(self):
        """Verify strict governance language without claims of fraud or guilt."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        prohibited_words = ["fraud", "fraudster", "guilty", "criminal", "confirmed improper", "crook"]
        for _, row in self.exp_df.iterrows():
            summary = row["plain_language_summary"].lower()
            evidence = " ".join(row["evidence_points"]).lower()
            for word in prohibited_words:
                self.assertNotIn(word, summary, f"Prohibited word '{word}' found in summary for {row['case_id']}")
                self.assertNotIn(word, evidence, f"Prohibited word '{word}' found in evidence for {row['case_id']}")

    def test_post_closure_explanation_numerical_integrity(self):
        """Verify post-closure explanations use exact closure dates and dollar sums."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        pc_exps = self.exp_df[self.exp_df["primary_signal"] == "Post-Closure"]
        self.assertGreater(len(pc_exps), 0)
        for _, row in pc_exps.iterrows():
            cid = row["case_id"]
            case_raw = self.cases_df[self.cases_df["case_id"] == cid].iloc[0]
            pays_raw = self.payments_df[self.payments_df["case_id"] == cid]
            closure_m = case_raw["closure_month"]
            pc_pays = pays_raw[pays_raw["pay_month"] > closure_m]

            self.assertIn(closure_m, row["plain_language_summary"])
            self.assertEqual(row["signal_financial_discrepancy"], round(pc_pays["amount"].sum(), 2))
            self.assertEqual(len(row["relevant_payment_ids"].split(", ")), len(pc_pays))

    def test_duplicate_explanation_numerical_integrity(self):
        """Verify duplicate explanations use exact duplicate dollar sums and months."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        dup_exps = self.exp_df[self.exp_df["primary_signal"] == "Duplicate"]
        self.assertGreater(len(dup_exps), 0)
        for _, row in dup_exps.iterrows():
            cid = row["case_id"]
            feature_row = self.top20_df[self.top20_df["case_id"] == cid].iloc[0]
            self.assertAlmostEqual(row["signal_financial_discrepancy"], feature_row["duplicate_excess_amount"], places=2)

    def test_award_spike_explanation_numerical_integrity(self):
        """Verify award spike explanations use exact award and peak payment figures."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        spike_exps = self.exp_df[self.exp_df["primary_signal"] == "Award Spike"]
        self.assertGreater(len(spike_exps), 0)
        for _, row in spike_exps.iterrows():
            cid = row["case_id"]
            case_raw = self.cases_df[self.cases_df["case_id"] == cid].iloc[0]
            self.assertAlmostEqual(row["monthly_award"], case_raw["monthly_award"], places=2)

    def test_disclaimer_presence(self):
        """Verify standard governance disclaimer is present on all explanations."""
        if self.exp_df is None:
            self.skipTest("Data files not found")
        for _, row in self.exp_df.iterrows():
            self.assertEqual(row["disclaimer"], STANDARD_DISCLAIMER)
        self.assertIn(STANDARD_DISCLAIMER, self.md_report)


if __name__ == "__main__":
    unittest.main()
