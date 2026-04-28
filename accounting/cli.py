"""経理自動化CLI.

使い方:

    # クレジットカードExcel明細を仕訳CSVに変換
    python -m accounting.cli credit-card \
        --input samples/credit_card_sample.xlsx \
        --output out/credit_card_journal.csv \
        --rules accounting_config/rules.yaml \
        --card rakuten

    # 銀行振込CSVを仕訳CSVに変換
    python -m accounting.cli bank \
        --input samples/bank_transfer_sample.csv \
        --output out/bank_journal.csv \
        --rules accounting_config/rules.yaml \
        --account mufg

    # 取り込み結果のサマリ(部門別売上集計)を表示
    python -m accounting.cli summary \
        --input out/bank_journal.csv

生成された仕訳CSVはマネーフォワードクラウド会計の
[各種設定] → [仕訳のインポート] からアップロードしてください.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from accounting.classifiers.rule_engine import RuleEngine
from accounting.exporters.moneyforward import MoneyForwardCSVExporter
from accounting.importers.bank_transfer import BankTransferCSVImporter
from accounting.importers.credit_card import CreditCardExcelImporter
from accounting.utils.logger import get_logger

logger = get_logger("accounting.cli")


def _cmd_credit_card(args: argparse.Namespace) -> int:
    importer = CreditCardExcelImporter()
    transactions = importer.load(args.input)
    # カード識別子をRawTransactionに反映 (importer段階で未指定の場合).
    if args.card:
        for t in transactions:
            if not t.raw.get("payment_source_id"):
                t.raw["payment_source_id"] = args.card

    engine = RuleEngine(args.rules)
    exporter = MoneyForwardCSVExporter(engine, start_no=args.start_no)
    n = exporter.write(args.output, transactions)
    logger.info("クレカ明細 %d 件を %s に書き出しました.", n, args.output)
    return 0


def _cmd_bank(args: argparse.Namespace) -> int:
    importer = BankTransferCSVImporter(account_id=args.account)
    transactions = importer.load(args.input)

    engine = RuleEngine(args.rules)
    exporter = MoneyForwardCSVExporter(engine, start_no=args.start_no)
    n = exporter.write(args.output, transactions)
    logger.info("銀行振込履歴 %d 件を %s に書き出しました.", n, args.output)
    return 0


def _cmd_summary(args: argparse.Namespace) -> int:
    """生成済み仕訳CSVから部門別売上を集計表示する."""
    sales_by_dept: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    expense_by_account: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    with open(args.input, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            credit_account = row.get("貸方勘定科目", "")
            credit_dept = row.get("貸方部門", "") or "(未設定)"
            credit_amount = _to_decimal(row.get("貸方金額", "0"))
            debit_account = row.get("借方勘定科目", "")
            debit_amount = _to_decimal(row.get("借方金額", "0"))

            if credit_account == "売上高":
                sales_by_dept[credit_dept] += credit_amount
            else:
                expense_by_account[debit_account] += debit_amount

    print("=== 部門別売上 ===")
    if sales_by_dept:
        for dept, amt in sorted(sales_by_dept.items(), key=lambda x: -x[1]):
            print(f"  {dept:<20} {int(amt):>12,} 円")
        print(f"  {'合計':<20} {int(sum(sales_by_dept.values())):>12,} 円")
    else:
        print("  (売上仕訳なし)")

    print()
    print("=== 勘定科目別 経費 ===")
    if expense_by_account:
        for acc, amt in sorted(expense_by_account.items(), key=lambda x: -x[1]):
            print(f"  {acc:<20} {int(amt):>12,} 円")
    else:
        print("  (経費仕訳なし)")

    return 0


def _to_decimal(s: str) -> Decimal:
    s = (s or "0").replace(",", "").strip()
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="accounting",
        description="セイキョウ 経理自動化システム (マネーフォワード仕訳CSV生成)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_cc = sub.add_parser("credit-card", help="クレジットカードExcel明細を仕訳CSVに変換")
    p_cc.add_argument("--input", required=True, type=Path, help="クレカ明細Excelファイル")
    p_cc.add_argument("--output", required=True, type=Path, help="出力CSVパス")
    p_cc.add_argument("--rules", required=True, type=Path, help="ルールYAML")
    p_cc.add_argument("--card", default="", help="カード識別子 (rakuten / amex 等)")
    p_cc.add_argument("--start-no", type=int, default=1)
    p_cc.set_defaults(func=_cmd_credit_card)

    p_bank = sub.add_parser("bank", help="銀行振込CSVを仕訳CSVに変換")
    p_bank.add_argument("--input", required=True, type=Path)
    p_bank.add_argument("--output", required=True, type=Path)
    p_bank.add_argument("--rules", required=True, type=Path)
    p_bank.add_argument("--account", default="", help="口座識別子 (mufg / smbc 等)")
    p_bank.add_argument("--start-no", type=int, default=1)
    p_bank.set_defaults(func=_cmd_bank)

    p_sum = sub.add_parser("summary", help="生成済み仕訳CSVの集計を表示")
    p_sum.add_argument("--input", required=True, type=Path)
    p_sum.set_defaults(func=_cmd_summary)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
