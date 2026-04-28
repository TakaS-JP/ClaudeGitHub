"""RuleEngine の動作確認テスト."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting.classifiers.rule_engine import RuleEngine
from accounting.models.journal_entry import RawTransaction


RULES_PATH = Path(__file__).resolve().parents[2] / "accounting_config" / "rules.yaml"


@pytest.fixture()
def engine() -> RuleEngine:
    return RuleEngine(RULES_PATH)


def _txn(description: str, *, source: str, direction: str, payment_id: str = "") -> RawTransaction:
    return RawTransaction(
        transaction_date=date(2026, 4, 1),
        description=description,
        amount=Decimal("1000"),
        source=source,
        direction=direction,
        counterparty=description,
        raw={"payment_source_id": payment_id},
    )


def test_credit_card_amazon_classified_as_supplies(engine: RuleEngine):
    res = engine.classify(_txn("AMAZON.CO.JP", source="credit_card", direction="expense", payment_id="rakuten"))
    assert res.debit_account == "消耗品費"
    assert res.credit_account == "未払金"
    assert res.credit_sub_account == "楽天カード"


def test_credit_card_jr_classified_as_travel(engine: RuleEngine):
    res = engine.classify(_txn("JR東日本 モバイルSuica", source="credit_card", direction="expense", payment_id="rakuten"))
    assert res.debit_account == "旅費交通費"


def test_bank_transfer_ec_sales_routed_to_ec_department(engine: RuleEngine):
    res = engine.classify(_txn("振込 楽天市場 04月清算", source="bank_transfer", direction="income", payment_id="mufg"))
    assert res.credit_account == "売上高"
    assert res.credit_department == "EC事業部"
    assert res.debit_account == "普通預金"


def test_bank_transfer_btob_routed_to_wholesale(engine: RuleEngine):
    res = engine.classify(_txn("振込 株式会社ミドリ商事", source="bank_transfer", direction="income", payment_id="mufg"))
    assert res.credit_department == "卸売部門"


def test_unknown_expense_falls_back_to_default(engine: RuleEngine):
    res = engine.classify(_txn("UNKNOWN MERCHANT XYZ", source="credit_card", direction="expense", payment_id="rakuten"))
    assert res.debit_account == "雑費"
    assert res.matched_rule == "default-expense"


def test_default_payment_account_when_no_id(engine: RuleEngine):
    res = engine.classify(_txn("AMAZON.CO.JP", source="credit_card", direction="expense"))
    # payment_source_id 未指定時はフォールバックの "クレジットカード" 補助科目になる.
    assert res.credit_sub_account == "クレジットカード"
