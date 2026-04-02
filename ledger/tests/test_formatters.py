"""Smoke tests for output formatters."""
import unittest
from datetime import date

from ledger.cli.formatters import (
    format_amount,
    format_contract_detail,
    format_contract_table,
    format_progress_bar,
    format_summary_report,
)
from ledger.models.contract import ConstructionContract, ContractStatus


def _contract() -> ConstructionContract:
    return ConstructionContract(
        project_number="2024-001",
        project_name="市役所外壁改修工事",
        location="東京都千代田区",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 9, 30),
        contractor_name="株式会社山田建設",
        contract_amount=15_000_000,
        advance_payment=3_000_000,
    )


class TestFormatAmount(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(format_amount(1_500_000), "¥1,500,000")

    def test_zero(self):
        self.assertEqual(format_amount(0), "¥0")

    def test_custom_symbol(self):
        self.assertEqual(format_amount(1_000, "$"), "$1,000")


class TestFormatProgressBar(unittest.TestCase):
    def test_50_percent(self):
        result = format_progress_bar(50.0)
        self.assertIn("50.0%", result)
        self.assertIn("[", result)
        self.assertIn("]", result)

    def test_0_percent(self):
        result = format_progress_bar(0.0)
        self.assertIn("0.0%", result)

    def test_100_percent(self):
        result = format_progress_bar(100.0)
        self.assertIn("100.0%", result)


class TestFormatContractTable(unittest.TestCase):
    def test_empty_list(self):
        result = format_contract_table([])
        self.assertIn("登録された工事はありません", result)

    def test_single_contract(self):
        c = _contract()
        result = format_contract_table([c])
        self.assertIn("2024-001", result)
        self.assertIn("山田建設", result)

    def test_does_not_crash_on_long_name(self):
        c = _contract()
        c.project_name = "a" * 50
        result = format_contract_table([c])
        self.assertIsInstance(result, str)


class TestFormatContractDetail(unittest.TestCase):
    def test_contains_key_fields(self):
        c = _contract()
        result = format_contract_detail(c)
        self.assertIn("2024-001", result)
        self.assertIn("市役所外壁改修工事", result)
        self.assertIn("¥15,000,000", result)
        self.assertIn("¥3,000,000", result)

    def test_computed_remaining(self):
        c = _contract()
        result = format_contract_detail(c)
        self.assertIn("¥12,000,000", result)


class TestFormatSummaryReport(unittest.TestCase):
    def test_empty_stats(self):
        stats = {
            "count": 0,
            "total_contract": 0,
            "total_final_contract": 0,
            "total_paid": 0,
            "total_remaining": 0,
            "by_status": {},
        }
        result = format_summary_report([], stats)
        self.assertIn("0件", result)

    def test_with_data(self):
        c = _contract()
        stats = {
            "count": 1,
            "total_contract": 15_000_000,
            "total_final_contract": 15_000_000,
            "total_paid": 3_000_000,
            "total_remaining": 12_000_000,
            "by_status": {"planned": 1},
        }
        result = format_summary_report([c], stats)
        self.assertIn("¥15,000,000", result)


if __name__ == "__main__":
    unittest.main()
