"""銀行振込CSV取り込みテスト."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from accounting.importers.bank_transfer import BankTransferCSVImporter


SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "bank_transfer_sample.csv"


def test_load_bank_transfer_sample_separates_income_and_expense():
    importer = BankTransferCSVImporter(account_id="mufg")
    txns = importer.load(SAMPLE)
    # 12行のサンプル全てが取り込まれる想定.
    assert len(txns) == 12

    incomes = [t for t in txns if t.is_income]
    expenses = [t for t in txns if not t.is_income]
    assert len(incomes) >= 5
    assert len(expenses) >= 5

    # 楽天市場の入金が正しく金額で読まれる.
    rakuten = next(t for t in txns if "楽天市場" in t.description)
    assert rakuten.is_income
    assert rakuten.amount == Decimal("1240000")
    assert rakuten.transaction_date == date(2026, 4, 3)


def test_account_id_is_propagated_for_payment_source():
    importer = BankTransferCSVImporter(account_id="mufg")
    txns = importer.load(SAMPLE)
    assert all(t.raw.get("payment_source_id") == "mufg" for t in txns)
