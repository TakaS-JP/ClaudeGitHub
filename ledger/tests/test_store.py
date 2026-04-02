"""Tests for LedgerStore SQLite CRUD operations using in-memory DB."""
import sqlite3
import unittest
from datetime import date

from ledger.models.contract import ConstructionContract, ContractStatus
from ledger.storage.ledger_store import LedgerStore


def _store() -> LedgerStore:
    """Return a fresh in-memory store."""
    return LedgerStore(":memory:")


def _contract(number: str = "2024-001", status: ContractStatus = ContractStatus.PLANNED) -> ConstructionContract:
    return ConstructionContract(
        project_number=number,
        project_name="市役所外壁改修工事",
        location="東京都千代田区",
        start_date=date(2024, 4, 1),
        end_date=date(2024, 9, 30),
        contractor_name="株式会社山田建設",
        contract_amount=15_000_000,
        status=status,
    )


class TestLedgerStoreCRUD(unittest.TestCase):
    def test_create_and_get(self):
        store = _store()
        c = _contract()
        store.create(c)
        fetched = store.get("2024-001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.project_name, "市役所外壁改修工事")
        self.assertEqual(fetched.contract_amount, 15_000_000)

    def test_get_nonexistent_returns_none(self):
        store = _store()
        self.assertIsNone(store.get("NONEXISTENT"))

    def test_duplicate_project_number_raises(self):
        store = _store()
        store.create(_contract())
        with self.assertRaises(sqlite3.IntegrityError):
            store.create(_contract())

    def test_update_modifies_fields(self):
        store = _store()
        c = _contract()
        store.create(c)
        c.project_name = "更新後の工事名"
        c.contract_amount = 20_000_000
        result = store.update(c)
        self.assertTrue(result)
        fetched = store.get("2024-001")
        self.assertEqual(fetched.project_name, "更新後の工事名")
        self.assertEqual(fetched.contract_amount, 20_000_000)

    def test_update_nonexistent_returns_false(self):
        store = _store()
        c = _contract("GHOST")
        result = store.update(c)
        self.assertFalse(result)

    def test_delete_removes_record(self):
        store = _store()
        store.create(_contract())
        deleted = store.delete("2024-001")
        self.assertTrue(deleted)
        self.assertIsNone(store.get("2024-001"))

    def test_delete_nonexistent_returns_false(self):
        store = _store()
        self.assertFalse(store.delete("GHOST"))

    def test_list_all_ordered_by_number(self):
        store = _store()
        store.create(_contract("2024-003"))
        store.create(_contract("2024-001"))
        store.create(_contract("2024-002"))
        contracts = store.list_all()
        numbers = [c.project_number for c in contracts]
        self.assertEqual(numbers, ["2024-001", "2024-002", "2024-003"])

    def test_search_by_status(self):
        store = _store()
        store.create(_contract("2024-001", ContractStatus.ACTIVE))
        store.create(_contract("2024-002", ContractStatus.PLANNED))
        store.create(_contract("2024-003", ContractStatus.ACTIVE))
        results = store.search(status="active")
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r.status, ContractStatus.ACTIVE)

    def test_search_by_contractor_partial(self):
        store = _store()
        c = _contract()
        store.create(c)
        results = store.search(contractor="山田")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].project_number, "2024-001")

    def test_date_roundtrip(self):
        store = _store()
        store.create(_contract())
        fetched = store.get("2024-001")
        self.assertEqual(fetched.start_date, date(2024, 4, 1))
        self.assertEqual(fetched.end_date, date(2024, 9, 30))


if __name__ == "__main__":
    unittest.main()
