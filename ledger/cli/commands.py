"""CLI subcommand definitions and dispatcher for the Construction Contract Ledger."""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date

from ledger.cli.formatters import (
    format_contract_detail,
    format_contract_table,
    format_summary_report,
)
from ledger.config.settings import LedgerSettings
from ledger.models.contract import ContractStatus
from ledger.services.contract_service import ContractService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ledger_main.py",
        description="工事請負台帳システム — Construction Contract Ledger",
    )
    sub = parser.add_subparsers(dest="subcommand", metavar="<command>")

    # ── add ──────────────────────────────────────────────────────────────────
    p_add = sub.add_parser("add", help="新規工事を登録する")
    p_add.add_argument("--number", required=True, metavar="工事番号", dest="project_number")
    p_add.add_argument("--name", required=True, metavar="工事名", dest="project_name")
    p_add.add_argument("--location", required=True, metavar="工事場所")
    p_add.add_argument("--start", required=True, metavar="YYYY-MM-DD", dest="start_date")
    p_add.add_argument("--end", required=True, metavar="YYYY-MM-DD", dest="end_date")
    p_add.add_argument("--contractor", required=True, metavar="請負業者名", dest="contractor_name")
    p_add.add_argument("--amount", required=True, type=int, metavar="契約金額", dest="contract_amount")

    # ── list ─────────────────────────────────────────────────────────────────
    p_list = sub.add_parser("list", help="工事一覧を表示する")
    p_list.add_argument("--status", metavar="ステータス", help="planned/active/inspection/completed/cancelled")
    p_list.add_argument("--contractor", metavar="請負業者名（部分一致）")
    p_list.add_argument("--year", type=int, metavar="年度")

    # ── show ─────────────────────────────────────────────────────────────────
    p_show = sub.add_parser("show", help="工事詳細を表示する")
    p_show.add_argument("project_number", metavar="工事番号")

    # ── update ───────────────────────────────────────────────────────────────
    p_upd = sub.add_parser("update", help="基本情報・契約情報を更新する")
    p_upd.add_argument("project_number", metavar="工事番号")
    p_upd.add_argument("--name", metavar="工事名", dest="project_name")
    p_upd.add_argument("--location", metavar="工事場所")
    p_upd.add_argument("--start", metavar="YYYY-MM-DD", dest="start_date")
    p_upd.add_argument("--end", metavar="YYYY-MM-DD", dest="end_date")
    p_upd.add_argument("--contractor", metavar="請負業者名", dest="contractor_name")
    p_upd.add_argument("--amount", type=int, metavar="契約金額", dest="contract_amount")

    # ── payment ──────────────────────────────────────────────────────────────
    p_pay = sub.add_parser("payment", help="支払い情報を更新する")
    p_pay.add_argument("project_number", metavar="工事番号")
    p_pay.add_argument("--advance", type=int, metavar="前払金")
    p_pay.add_argument("--interim", type=int, metavar="中間払い")
    p_pay.add_argument("--completion", type=int, metavar="完成払い")

    # ── progress ─────────────────────────────────────────────────────────────
    p_prog = sub.add_parser("progress", help="進捗情報を更新する")
    p_prog.add_argument("project_number", metavar="工事番号")
    p_prog.add_argument("--percent", type=float, metavar="進捗率(0-100)")
    p_prog.add_argument("--inspection-date", metavar="YYYY-MM-DD", dest="inspection_date")
    p_prog.add_argument("--completion-date", metavar="YYYY-MM-DD", dest="completion_date")
    p_prog.add_argument("--notes", metavar="備考")

    # ── change-order ─────────────────────────────────────────────────────────
    p_co = sub.add_parser("change-order", help="変更契約を登録する（増減額）")
    p_co.add_argument("project_number", metavar="工事番号")
    p_co.add_argument("--delta", required=True, type=int, metavar="変更金額（±円）")

    # ── status ───────────────────────────────────────────────────────────────
    p_st = sub.add_parser("status", help="工事ステータスを変更する")
    p_st.add_argument("project_number", metavar="工事番号")
    p_st.add_argument(
        "--set",
        required=True,
        choices=[s.value for s in ContractStatus],
        metavar="ステータス",
        dest="new_status",
    )

    # ── delete ───────────────────────────────────────────────────────────────
    p_del = sub.add_parser("delete", help="工事を削除する")
    p_del.add_argument("project_number", metavar="工事番号")
    p_del.add_argument("--confirm", action="store_true", help="削除を確認する")

    # ── summary ──────────────────────────────────────────────────────────────
    p_sum = sub.add_parser("summary", help="集計レポートを表示する")
    p_sum.add_argument("--status", metavar="ステータス")
    p_sum.add_argument("--year", type=int, metavar="年度")
    p_sum.add_argument("--contractor", metavar="請負業者名（部分一致）")

    return parser


def dispatch_command(
    args: argparse.Namespace,
    service: ContractService,
    config: LedgerSettings,
) -> None:
    sym = config.currency_symbol

    if args.subcommand == "add":
        contract = service.create_contract(
            project_number=args.project_number,
            project_name=args.project_name,
            location=args.location,
            start_date=_parse_date(args.start_date, "工期開始日"),
            end_date=_parse_date(args.end_date, "工期終了日"),
            contractor_name=args.contractor_name,
            contract_amount=args.contract_amount,
        )
        print(f"登録完了: {contract.project_number} — {contract.project_name}")
        print(format_contract_detail(contract, sym))

    elif args.subcommand == "list":
        contracts = service._store.search(
            status=args.status,
            contractor=getattr(args, "contractor", None),
            year=args.year,
        )
        print(format_contract_table(contracts, sym))

    elif args.subcommand == "show":
        contract = service._store.get(args.project_number)
        if contract is None:
            _abort(f"工事番号が見つかりません: {args.project_number}")
        print(format_contract_detail(contract, sym))

    elif args.subcommand == "update":
        kwargs: dict = {}
        for field in ("project_name", "location", "contractor_name", "contract_amount"):
            val = getattr(args, field, None)
            if val is not None:
                kwargs[field] = val
        for field, label in (("start_date", "工期開始日"), ("end_date", "工期終了日")):
            raw = getattr(args, field, None)
            if raw is not None:
                kwargs[field] = _parse_date(raw, label)
        if not kwargs:
            _abort("更新する項目を指定してください（--name, --location, etc.）")
        contract = service.update_fields(args.project_number, **kwargs)
        print(f"更新完了: {contract.project_number}")
        print(format_contract_detail(contract, sym))

    elif args.subcommand == "payment":
        contract = service.record_payment(
            args.project_number,
            advance=args.advance,
            interim=args.interim,
            completion=args.completion,
        )
        print(f"支払更新完了: {contract.project_number}")
        print(format_contract_detail(contract, sym))

    elif args.subcommand == "progress":
        contract = service.update_progress(
            args.project_number,
            percent=args.percent,
            inspection_date=_parse_date(args.inspection_date, "検査日") if args.inspection_date else None,
            completion_date=_parse_date(args.completion_date, "完成日") if args.completion_date else None,
            notes=args.notes,
        )
        print(f"進捗更新完了: {contract.project_number} — {contract.progress_percent:.1f}%")
        print(format_contract_detail(contract, sym))

    elif args.subcommand == "change-order":
        contract = service.apply_change_order(args.project_number, args.delta)
        print(f"変更契約登録完了: {contract.project_number}")
        print(format_contract_detail(contract, sym))

    elif args.subcommand == "status":
        contract = service.update_status(
            args.project_number,
            ContractStatus(args.new_status),
        )
        print(f"ステータス更新完了: {contract.project_number} → {contract.status.value}")

    elif args.subcommand == "delete":
        if not args.confirm:
            _abort("削除するには --confirm フラグを指定してください")
        deleted = service._store.delete(args.project_number)
        if deleted:
            print(f"削除完了: {args.project_number}")
        else:
            _abort(f"工事番号が見つかりません: {args.project_number}")

    elif args.subcommand == "summary":
        contracts = service._store.search(
            status=args.status,
            contractor=getattr(args, "contractor", None),
            year=args.year,
        )
        stats = service.get_summary_stats(contracts)
        print(format_summary_report(contracts, stats, sym))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{label}の形式が不正です（YYYY-MM-DD）: {value}")


def _abort(message: str) -> None:
    print(f"エラー: {message}", file=sys.stderr)
    sys.exit(1)
