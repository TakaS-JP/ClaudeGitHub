"""銀行振込履歴(CSV)のインポータ.

インターネットバンキングからダウンロードしたCSVを汎用的に読み込み,
RawTransactionへ変換する. 多くの銀行は以下の列を持つ:
- 取引日 / 日付
- 摘要 / お取引内容
- お支払金額 / 出金 (引き落とし)
- お預り金額 / 入金 (振込入金)
- 取引メモ
- 残高 (本ツールでは未使用)

入出金が別カラムに分かれている形式と1カラムにまとまっている形式の両方に対応.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from accounting.models.journal_entry import RawTransaction


DEFAULT_COLUMN_ALIASES = {
    "date": ["取引日", "日付", "年月日", "計算日"],
    "description": ["摘要", "お取引内容", "内容", "取引内容"],
    "withdraw": ["お支払金額", "出金", "出金金額", "お支払額"],
    "deposit": ["お預り金額", "入金", "入金金額", "お預入額"],
    "amount": ["金額", "取引金額"],
    "memo": ["取引メモ", "メモ", "備考"],
}


@dataclass
class BankTransferCSVImporter:
    """銀行のCSV履歴をRawTransactionに変換."""

    account_id: str = ""  # 複数口座運用時に支払元を識別するキー
    column_aliases: dict[str, list[str]] | None = None
    encoding: str = "utf-8-sig"

    def load(self, path: Path | str) -> list[RawTransaction]:
        path = Path(path)
        encodings_to_try = [self.encoding, "cp932", "shift_jis", "utf-8"]

        last_err: Optional[Exception] = None
        for enc in encodings_to_try:
            try:
                with open(path, "r", encoding=enc, newline="") as fh:
                    reader = csv.reader(fh)
                    rows = list(reader)
                break
            except UnicodeDecodeError as e:
                last_err = e
        else:
            raise last_err  # type: ignore[misc]

        if not rows:
            return []

        header = [c.strip() for c in rows[0]]
        col_idx = self._resolve_columns(header)

        transactions: list[RawTransaction] = []
        for row in rows[1:]:
            if not row or all(c.strip() == "" for c in row):
                continue
            txn = self._row_to_transaction(row, col_idx)
            if txn is not None:
                transactions.append(txn)
        return transactions

    def _resolve_columns(self, header: list[str]) -> dict[str, int]:
        aliases = self.column_aliases or DEFAULT_COLUMN_ALIASES
        idx: dict[str, int] = {}
        for key, candidates in aliases.items():
            for cand in candidates:
                if cand in header:
                    idx[key] = header.index(cand)
                    break

        if "date" not in idx:
            raise ValueError(f"日付列が見つかりません. ヘッダ: {header}")
        if "description" not in idx:
            raise ValueError(f"摘要列が見つかりません. ヘッダ: {header}")
        # 入出金は (withdraw + deposit) または (amount) のどちらかが必須.
        if not (("withdraw" in idx and "deposit" in idx) or "amount" in idx):
            raise ValueError(
                f"入出金額の列が見つかりません. ヘッダ: {header}"
            )
        return idx

    def _row_to_transaction(
        self, row: list[str], col_idx: dict[str, int]
    ) -> Optional[RawTransaction]:
        try:
            txn_date = _parse_date(row[col_idx["date"]])
        except (ValueError, TypeError, IndexError):
            return None

        description = row[col_idx["description"]].strip() if col_idx["description"] < len(row) else ""

        memo = ""
        if "memo" in col_idx and col_idx["memo"] < len(row):
            memo = row[col_idx["memo"]].strip()

        amount: Optional[Decimal] = None
        direction = "expense"

        if "withdraw" in col_idx and "deposit" in col_idx:
            withdraw = _parse_amount(row[col_idx["withdraw"]] if col_idx["withdraw"] < len(row) else "")
            deposit = _parse_amount(row[col_idx["deposit"]] if col_idx["deposit"] < len(row) else "")
            if deposit and deposit > 0:
                amount = deposit
                direction = "income"
            elif withdraw and withdraw > 0:
                amount = withdraw
                direction = "expense"
        elif "amount" in col_idx:
            v = _parse_amount(row[col_idx["amount"]])
            if v is None:
                return None
            if v > 0:
                amount = v
                direction = "income"
            else:
                amount = abs(v)
                direction = "expense"

        if amount is None or amount == 0:
            return None

        return RawTransaction(
            transaction_date=txn_date,
            description=description,
            amount=amount,
            source="bank_transfer",
            direction=direction,
            counterparty=description,
            memo=memo,
            raw={"payment_source_id": self.account_id},
        )


def _parse_date(value: str) -> date:
    s = (value or "").strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d", "%Y%m%d", "%Y年%m月%d日"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"日付として解釈できません: {value!r}")


def _parse_amount(value: str) -> Optional[Decimal]:
    if value is None:
        return None
    s = str(value).replace(",", "").replace("¥", "").replace("円", "").strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None
