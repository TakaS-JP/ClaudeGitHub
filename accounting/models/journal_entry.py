"""仕訳データモデル.

マネーフォワードクラウド会計の仕訳CSVインポート形式に対応する
データクラスを定義する.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class RawTransaction:
    """取り込み元データ(クレカ明細・振込履歴)の生レコード.

    インポート元のExcel/CSVから読み込んだ1行分を表す中間表現.
    """

    transaction_date: date
    description: str
    amount: Decimal
    source: str  # "credit_card" / "bank_transfer"
    direction: str = "expense"  # "expense" or "income"
    counterparty: str = ""
    memo: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def is_income(self) -> bool:
        return self.direction == "income"


@dataclass
class JournalEntry:
    """マネーフォワードクラウド会計の仕訳1行.

    マネーフォワードの仕訳インポートCSVは複合仕訳に対応しており,
    1取引につき借方・貸方それぞれの勘定科目・補助科目・部門・金額・税区分を持つ.
    """

    transaction_no: int
    transaction_date: date

    debit_account: str
    debit_sub_account: str = ""
    debit_department: str = ""
    debit_amount: Decimal = Decimal("0")
    debit_tax_category: str = "対象外"

    credit_account: str = ""
    credit_sub_account: str = ""
    credit_department: str = ""
    credit_amount: Decimal = Decimal("0")
    credit_tax_category: str = "対象外"

    description: str = ""
    memo: str = ""
    tag: str = ""

    def to_csv_row(self) -> list[str]:
        """マネーフォワード仕訳CSVの1行(15項目)に変換する."""
        return [
            str(self.transaction_no),
            self.transaction_date.strftime("%Y/%m/%d"),
            self.debit_account,
            self.debit_sub_account,
            self.debit_department,
            str(int(self.debit_amount)),
            self.debit_tax_category,
            self.credit_account,
            self.credit_sub_account,
            self.credit_department,
            str(int(self.credit_amount)),
            self.credit_tax_category,
            self.description,
            self.memo,
            self.tag,
        ]


# マネーフォワードクラウド会計の仕訳インポートCSVヘッダ.
MONEYFORWARD_CSV_HEADERS = [
    "取引No",
    "取引日",
    "借方勘定科目",
    "借方補助科目",
    "借方部門",
    "借方金額",
    "借方税区分",
    "貸方勘定科目",
    "貸方補助科目",
    "貸方部門",
    "貸方金額",
    "貸方税区分",
    "摘要",
    "仕訳メモ",
    "タグ",
]
