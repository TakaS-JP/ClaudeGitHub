"""Tests for ConstructionContract computed properties."""
import unittest
from datetime import date, datetime, timezone

from ledger.models.contract import ConstructionContract, ContractStatus


def _make(
    contract_amount: int = 10_000_000,
    change_amount: int = 0,
    advance: int = 0,
    interim: int = 0,
    completion: int = 0,
) -> ConstructionContract:
    return ConstructionContract(
        project_number="TEST-001",
        project_name="テスト工事",
        location="東京都",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 9, 30),
        contractor_name="テスト建設",
        contract_amount=contract_amount,
        change_amount=change_amount,
        advance_payment=advance,
        interim_payment=interim,
        completion_payment=completion,
    )


class TestComputedProperties(unittest.TestCase):
    def test_final_contract_amount_no_change(self):
        c = _make(contract_amount=10_000_000)
        self.assertEqual(c.final_contract_amount, 10_000_000)

    def test_final_contract_amount_positive_change(self):
        c = _make(contract_amount=10_000_000, change_amount=500_000)
        self.assertEqual(c.final_contract_amount, 10_500_000)

    def test_final_contract_amount_negative_change(self):
        c = _make(contract_amount=10_000_000, change_amount=-500_000)
        self.assertEqual(c.final_contract_amount, 9_500_000)

    def test_paid_amount_sums_all_payments(self):
        c = _make(advance=1_000_000, interim=2_000_000, completion=7_000_000)
        self.assertEqual(c.paid_amount, 10_000_000)

    def test_paid_amount_zero_when_no_payments(self):
        c = _make()
        self.assertEqual(c.paid_amount, 0)

    def test_remaining_amount_fully_paid(self):
        c = _make(contract_amount=10_000_000, completion=10_000_000)
        self.assertEqual(c.remaining_amount, 0)

    def test_remaining_amount_unpaid(self):
        c = _make(contract_amount=10_000_000, advance=3_000_000)
        self.assertEqual(c.remaining_amount, 7_000_000)

    def test_remaining_amount_with_change(self):
        c = _make(contract_amount=10_000_000, change_amount=500_000, completion=5_000_000)
        self.assertEqual(c.remaining_amount, 5_500_000)

    def test_default_status_is_planned(self):
        c = _make()
        self.assertEqual(c.status, ContractStatus.PLANNED)


if __name__ == "__main__":
    unittest.main()
