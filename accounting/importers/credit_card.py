"""クレジットカード明細(Excel)のインポータ.

マネーフォワードクラウド会計でクレカと同期している場合,
明細自体は自動取得されるが「仕訳の自動振替」までは行われないことが多い.
本モジュールはユーザが用意したExcel明細(クレカ会社のCSVをExcelで整形した
もの, または社内で集計した明細)を読み込み, RawTransactionに変換する.

期待される列(ヘッダ名は config/columns で柔軟にマッピング可能):
- 利用日 (date)
- 利用店名 / ご利用先 (description)
- 利用金額 (amount)
- メモ (memo, 任意)
- カード名 / カード会社 (payment_source_id, 任意, 複数枚運用時)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional

import openpyxl

from accounting.models.journal_entry import RawTransaction


# 列ヘッダの揺らぎを吸収するための候補名.
DEFAULT_COLUMN_ALIASES = {
    "date": ["利用日", "ご利用日", "日付", "取引日"],
    "description": ["利用店名", "ご利用先", "ご利用店名", "店名", "摘要"],
    "amount": ["利用金額", "金額", "ご利用金額"],
    "memo": ["メモ", "備考"],
    "payment_source_id": ["カード名", "カード会社", "カード"],
}


@dataclass
class CreditCardExcelImporter:
    """Excelクレカ明細を読み込み, RawTransactionリストを返す."""

    column_aliases: dict[str, list[str]] | None = None
    sheet_name: Optional[str] = None

    def load(self, path: Path | str) -> list[RawTransaction]:
        path = Path(path)
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb[self.sheet_name] if self.sheet_name else wb.active

        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []

        header = [str(c).strip() if c is not None else "" for c in rows[0]]
        col_idx = self._resolve_columns(header)

        transactions: list[RawTransaction] = []
        for row in rows[1:]:
            if row is None or all(c is None or c == "" for c in row):
                continue
            txn = self._row_to_transaction(row, col_idx)
            if txn is not None:
                transactions.append(txn)
        return transactions

    def _resolve_columns(self, header: list[str]) -> dict[str, int]:
        """ヘッダ名と列インデックスのマッピングを構築."""
        aliases = self.column_aliases or DEFAULT_COLUMN_ALIASES
        idx: dict[str, int] = {}
        for key, candidates in aliases.items():
            for cand in candidates:
                if cand in header:
                    idx[key] = header.index(cand)
                    break
        for required in ("date", "description", "amount"):
            if required not in idx:
                raise ValueError(
                    f"必須列 '{required}' がExcelヘッダに見つかりませんでした. "
                    f"ヘッダ: {header}"
                )
        return idx

    def _row_to_transaction(
        self, row: tuple, col_idx: dict[str, int]
    ) -> Optional[RawTransaction]:
        try:
            txn_date = _parse_date(row[col_idx["date"]])
        except (ValueError, TypeError):
            return None

        description = str(row[col_idx["description"]] or "").strip()
        amount = _parse_amount(row[col_idx["amount"]])
        if amount is None or amount == 0:
            return None

        memo = ""
        if "memo" in col_idx and row[col_idx["memo"]] is not None:
            memo = str(row[col_idx["memo"]]).strip()

        payment_source_id = ""
        if (
            "payment_source_id" in col_idx
            and row[col_idx["payment_source_id"]] is not None
        ):
            payment_source_id = str(row[col_idx["payment_source_id"]]).strip()

        # クレカ明細は支出が一般的だが, 返金はマイナス金額として income に振り替える.
        direction = "income" if amount < 0 else "expense"
        amount_abs = abs(amount)

        return RawTransaction(
            transaction_date=txn_date,
            description=description,
            amount=amount_abs,
            source="credit_card",
            direction=direction,
            counterparty=description,
            memo=memo,
            raw={"payment_source_id": payment_source_id},
        )


def _parse_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d", "%Y年%m月%d日"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    raise ValueError(f"日付として解釈できません: {value!r}")


def _parse_amount(value) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    s = str(value).replace(",", "").replace("¥", "").replace("円", "").strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None
