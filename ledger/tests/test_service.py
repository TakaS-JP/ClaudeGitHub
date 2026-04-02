"""Tests for ContractService business logic and validation."""
import unittest
from datetime import date

from ledger.models.contract import ContractStatus
from ledger.services.contract_service import ContractService
from ledger.storage.ledger_store import LedgerStore


def _service() -> ContractService:
    return ContractService(LedgerStore(":memory:"))


def _create(svc: ContractService, number: str = "2024-001") -> object:
    return svc.create_contract(
        project_number=number,
        project_name="テスト工事",
        location="東京都",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 9, 30),
        contractor_name="テスト建設",
        contract_amount=10_000_000,
    )


class TestCreateContract(unittest.TestCase):
    def test_create_success(self):
        svc = _service()
        c = _create(svc)
        self.assertEqual(c.project_number, "2024-001")

    def test_start_after_end_raises(self):
        svc = _service()
        with self.assertRaises(ValueError):
            svc.create_contract(
                project_number="BAD",
                project_name="x",
                location="x",
                start_date=date(2024, 9, 30),
                end_date=date(2024, 4, 1),
                contractor_name="x",
                contract_amount=1_000_000,
            )

    def test_start_equal_end_raises(self):
        svc = _service()
        with self.assertRaises(ValueError):
            svc.create_contract(
                project_number="BAD2",
                project_name="x",
                location="x",
                start_date=date(2024, 4, 1),
                end_date=date(2024, 4, 1),
                contractor_name="x",
                contract_amount=1_000_000,
            )

    def test_negative_amount_raises(self):
        svc = _service()
        with self.assertRaises(ValueError):
            svc.create_contract(
                project_number="BAD3",
                project_name="x",
                location="x",
                start_date=date(2024, 4, 1),
                end_date=date(2024, 9, 30),
                contractor_name="x",
                contract_amount=-1,
            )


class TestChangeOrder(unittest.TestCase):
    def test_increase(self):
        svc = _service()
        _create(svc)
        c = svc.apply_change_order("2024-001", 500_000)
        self.assertEqual(c.final_contract_amount, 10_500_000)

    def test_decrease(self):
        svc = _service()
        _create(svc)
        c = svc.apply_change_order("2024-001", -500_000)
        self.assertEqual(c.final_contract_amount, 9_500_000)

    def test_too_large_decrease_raises(self):
        svc = _service()
        _create(svc)
        with self.assertRaises(ValueError):
            svc.apply_change_order("2024-001", -15_000_000)

    def test_unknown_project_raises(self):
        svc = _service()
        with self.assertRaises(ValueError):
            svc.apply_change_order("GHOST", 100)


class TestRecordPayment(unittest.TestCase):
    def test_payment_within_limit(self):
        svc = _service()
        _create(svc)
        c = svc.record_payment("2024-001", advance=3_000_000)
        self.assertEqual(c.paid_amount, 3_000_000)

    def test_overpayment_raises(self):
        svc = _service()
        _create(svc)
        with self.assertRaises(ValueError):
            svc.record_payment("2024-001", completion=20_000_000)

    def test_multiple_payment_fields(self):
        svc = _service()
        _create(svc)
        c = svc.record_payment("2024-001", advance=3_000_000, interim=3_000_000, completion=4_000_000)
        self.assertEqual(c.paid_amount, 10_000_000)
        self.assertEqual(c.remaining_amount, 0)


class TestUpdateProgress(unittest.TestCase):
    def test_progress_update(self):
        svc = _service()
        _create(svc)
        c = svc.update_progress("2024-001", percent=65.0)
        self.assertEqual(c.progress_percent, 65.0)

    def test_progress_100_auto_completes(self):
        svc = _service()
        _create(svc)
        c = svc.update_progress("2024-001", percent=100.0)
        self.assertEqual(c.status, ContractStatus.COMPLETED)

    def test_progress_above_100_raises(self):
        svc = _service()
        _create(svc)
        with self.assertRaises(ValueError):
            svc.update_progress("2024-001", percent=101.0)

    def test_progress_below_0_raises(self):
        svc = _service()
        _create(svc)
        with self.assertRaises(ValueError):
            svc.update_progress("2024-001", percent=-1.0)

    def test_notes_update(self):
        svc = _service()
        _create(svc)
        c = svc.update_progress("2024-001", notes="内装工事開始")
        self.assertEqual(c.notes, "内装工事開始")

    def test_inspection_date(self):
        svc = _service()
        _create(svc)
        c = svc.update_progress("2024-001", inspection_date=date(2024, 9, 1))
        self.assertEqual(c.inspection_date, date(2024, 9, 1))


class TestSummaryStats(unittest.TestCase):
    def test_empty_list(self):
        svc = _service()
        stats = svc.get_summary_stats([])
        self.assertEqual(stats["count"], 0)

    def test_total_contract(self):
        svc = _service()
        _create(svc, "2024-001")
        _create(svc, "2024-002")
        contracts = svc._store.list_all()
        stats = svc.get_summary_stats(contracts)
        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["total_contract"], 20_000_000)


if __name__ == "__main__":
    unittest.main()
