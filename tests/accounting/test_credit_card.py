"""クレジットカードExcel取り込みテスト."""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting.importers.credit_card import CreditCardExcelImporter


SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "credit_card_sample.xlsx"
GENERATOR = Path(__file__).resolve().parents[2] / "samples" / "generate_credit_card_sample.py"


@pytest.fixture(scope="module", autouse=True)
def ensure_sample_excel():
    if not SAMPLE.exists():
        subprocess.run([sys.executable, str(GENERATOR)], check=True)
    yield


def test_load_credit_card_sample():
    importer = CreditCardExcelImporter()
    txns = importer.load(SAMPLE)
    # サンプルは13行 (ヘッダ除く).
    assert len(txns) == 13

    first = txns[0]
    assert first.transaction_date == date(2026, 4, 1)
    assert "AMAZON" in first.description.upper()
    assert first.amount == Decimal("4980")
    assert first.source == "credit_card"
    assert first.direction == "expense"
    assert first.raw["payment_source_id"] == "rakuten"


def test_negative_amount_treated_as_refund_income():
    importer = CreditCardExcelImporter()
    txns = importer.load(SAMPLE)
    refund = next(t for t in txns if "返金" in t.description)
    assert refund.is_income
    assert refund.amount == Decimal("1980")
