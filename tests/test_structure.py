"""Sanity test to verify project structure and data loader imports."""
import unittest
from pathlib import Path
from src.data.loader import load_cases, load_payments, NEEDS_FIGURES
from src.governance.guardrails import PROHIBITED_AUTOMATED_ACTIONS, get_governance_statement


class TestProjectStructure(unittest.TestCase):
    def test_needs_figures(self):
        self.assertEqual(len(NEEDS_FIGURES), 6)
        self.assertEqual(NEEDS_FIGURES[1], 1240)
        self.assertEqual(NEEDS_FIGURES[6], 2990)

    def test_governance_statement(self):
        statement = get_governance_statement()
        self.assertIn("PROHIBITED ACTIONS", statement)
        self.assertIn("HUMAN-IN-THE-LOOP INVESTIGATION WORKFLOW", statement)
        self.assertEqual(len(PROHIBITED_AUTOMATED_ACTIONS), 11)

    def test_data_loader_presence(self):
        cases_path = Path("data/cases.csv")
        payments_path = Path("data/payments.csv")
        if cases_path.exists() and payments_path.exists():
            cases = load_cases(cases_path)
            payments = load_payments(payments_path)
            self.assertEqual(len(cases), 4200)
            self.assertEqual(len(payments), 24756)


if __name__ == "__main__":
    unittest.main()


