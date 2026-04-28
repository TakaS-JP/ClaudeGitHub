"""マネーフォワードクラウド会計の仕訳インポートCSV書き出し.

マネーフォワード公式仕様 (仕訳帳インポート) に従い, 15項目のCSVを生成する.
- 文字コード: UTF-8 (BOM付き). マネーフォワードはBOM付きUTF-8を推奨.
- 改行: CRLF.
- 区切り: カンマ.
- ヘッダ行を含める.

部門別売上を可視化するため, 各仕訳に「貸方部門」を必ず設定する.
売上以外の費用にも部門指定が必要な場合は ClassificationResult 経由で設定可能.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from accounting.classifiers.rule_engine import ClassificationResult, RuleEngine
from accounting.models.journal_entry import (
    JournalEntry,
    MONEYFORWARD_CSV_HEADERS,
    RawTransaction,
)


class MoneyForwardCSVExporter:
    """RawTransaction群を仕訳CSVに変換して書き出す."""

    def __init__(self, rule_engine: RuleEngine, start_no: int = 1):
        self._engine = rule_engine
        self._start_no = start_no

    def build_entries(
        self, transactions: Iterable[RawTransaction]
    ) -> list[JournalEntry]:
        """RawTransactionをルールエンジンで分類しJournalEntry化する."""
        entries: list[JournalEntry] = []
        no = self._start_no
        for txn in transactions:
            result = self._engine.classify(txn)
            entries.append(self._to_entry(no, txn, result))
            no += 1
        return entries

    def write(
        self,
        path: Path | str,
        transactions: Iterable[RawTransaction],
    ) -> int:
        """仕訳CSVを書き出し, 書き込んだ行数を返す."""
        entries = self.build_entries(transactions)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # マネーフォワードはBOM付きUTF-8を推奨 (Excelでの文字化け防止).
        with open(path, "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh, lineterminator="\r\n")
            writer.writerow(MONEYFORWARD_CSV_HEADERS)
            for entry in entries:
                writer.writerow(entry.to_csv_row())
        return len(entries)

    def _to_entry(
        self,
        no: int,
        txn: RawTransaction,
        result: ClassificationResult,
    ) -> JournalEntry:
        memo = f"[{txn.source}] rule={result.matched_rule}"
        if txn.memo:
            memo = f"{memo} | {txn.memo}"

        return JournalEntry(
            transaction_no=no,
            transaction_date=txn.transaction_date,
            debit_account=result.debit_account,
            debit_sub_account=result.debit_sub_account,
            debit_department=result.debit_department,
            debit_amount=txn.amount,
            debit_tax_category=result.debit_tax_category,
            credit_account=result.credit_account,
            credit_sub_account=result.credit_sub_account,
            credit_department=result.credit_department,
            credit_amount=txn.amount,
            credit_tax_category=result.credit_tax_category,
            description=txn.description[:100],
            memo=memo,
            tag="",
        )
