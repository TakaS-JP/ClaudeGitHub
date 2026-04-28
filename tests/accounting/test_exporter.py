"""MoneyForwardCSVExporter の出力フォーマットテスト."""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from accounting.classifiers.rule_engine import RuleEngine
from accounting.exporters.moneyforward import MoneyForwardCSVExporter
from accounting.models.journal_entry import (
    MONEYFORWARD_CSV_HEADERS,
    RawTransaction,
)


RULES_PATH = Path(__file__).resolve().parents[2] / "accounting_config" / "rules.yaml"


def _engine() -> RuleEngine:
    return RuleEngine(RULES_PATH)


def test_csv_has_correct_headers_and_department(tmp_path: Path):
    txns = [
        RawTransaction(
            transaction_date=date(2026, 4, 3),
            description="振込 楽天市場 04月清算",
            amount=Decimal("1240000"),
            source="bank_transfer",
            direction="income",
            counterparty="楽天市場",
            raw={"payment_source_id": "mufg"},
        ),
        RawTransaction(
            transaction_date=date(2026, 4, 1),
            description="AMAZON.CO.JP",
            amount=Decimal("4980"),
            source="credit_card",
            direction="expense",
            counterparty="AMAZON",
            raw={"payment_source_id": "rakuten"},
        ),
    ]

    out = tmp_path / "out.csv"
    exporter = MoneyForwardCSVExporter(_engine())
    n = exporter.write(out, txns)
    assert n == 2

    with open(out, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)

    assert rows[0] == MONEYFORWARD_CSV_HEADERS

    # 売上行は貸方部門に EC事業部 がセットされている.
    sale_row = rows[1]
    headers = MONEYFORWARD_CSV_HEADERS
    sale = dict(zip(headers, sale_row))
    assert sale["貸方勘定科目"] == "売上高"
    assert sale["貸方部門"] == "EC事業部"
    assert sale["借方勘定科目"] == "普通預金"
    assert sale["借方補助科目"] == "三菱UFJ銀行"
    assert sale["貸方金額"] == "1240000"

    # クレカ行は借方=消耗品費, 貸方=未払金/楽天カード.
    expense = dict(zip(headers, rows[2]))
    assert expense["借方勘定科目"] == "消耗品費"
    assert expense["貸方勘定科目"] == "未払金"
    assert expense["貸方補助科目"] == "楽天カード"
