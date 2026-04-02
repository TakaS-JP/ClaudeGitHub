"""
工事請負台帳システム — Construction Contract Ledger System
エントリーポイント

Usage:
    python ledger_main.py <command> [options]
    python ledger_main.py --help

Commands:
    add           新規工事を登録する
    list          工事一覧を表示する
    show          工事詳細を表示する
    update        基本情報・契約情報を更新する
    payment       支払い情報を更新する
    progress      進捗情報を更新する
    change-order  変更契約を登録する
    status        工事ステータスを変更する
    delete        工事を削除する
    summary       集計レポートを表示する
"""
import sys

from ledger.cli.commands import build_parser, dispatch_command
from ledger.config.settings import LedgerSettings
from ledger.services.contract_service import ContractService
from ledger.storage.ledger_store import LedgerStore
from ledger.utils.logger import setup_ledger_logger


def main() -> None:
    config = LedgerSettings()
    logger = setup_ledger_logger(config.log_level)

    store = LedgerStore(config.db_path)
    service = ContractService(store)

    parser = build_parser()
    args = parser.parse_args()

    if not getattr(args, "subcommand", None):
        parser.print_help()
        sys.exit(0)

    try:
        dispatch_command(args, service, config)
    except ValueError as exc:
        print(f"入力エラー: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n中断されました。", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
