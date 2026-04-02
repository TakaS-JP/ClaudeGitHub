"""Output formatting helpers for the Construction Contract Ledger CLI."""
from __future__ import annotations

from datetime import date
from typing import Optional

from ledger.models.contract import ConstructionContract, ContractStatus

_STATUS_LABEL: dict[ContractStatus, str] = {
    ContractStatus.PLANNED: "計画中",
    ContractStatus.ACTIVE: "進行中",
    ContractStatus.INSPECTION: "検査中",
    ContractStatus.COMPLETED: "完成",
    ContractStatus.CANCELLED: "中止",
}


def format_amount(amount: int, symbol: str = "¥") -> str:
    """Format an integer as ¥1,500,000."""
    return f"{symbol}{amount:,}"


def format_date(d: Optional[date]) -> str:
    return d.isoformat() if d else "—"


def format_progress_bar(percent: float, width: int = 20) -> str:
    """Render an ASCII progress bar: [=========>          ] 45.0%"""
    filled = int(percent / 100 * width)
    if filled >= width:
        bar = "=" * width
    elif filled > 0:
        bar = "=" * (filled - 1) + ">" + " " * (width - filled)
    else:
        bar = " " * width
    return f"[{bar}] {percent:.1f}%"


def format_status(status: ContractStatus) -> str:
    return _STATUS_LABEL.get(status, status.value)


def format_contract_table(contracts: list[ConstructionContract], symbol: str = "¥") -> str:
    """Render contracts as a fixed-width ASCII table."""
    if not contracts:
        return "（登録された工事はありません）"

    header = (
        f"{'工事番号':<12} {'工事名':<20} {'請負業者':<16} "
        f"{'最終契約金額':>14} {'進捗':>8} {'ステータス':<8}"
    )
    separator = "-" * len(header)
    lines = [header, separator]

    for c in contracts:
        lines.append(
            f"{c.project_number:<12} {c.project_name[:20]:<20} "
            f"{c.contractor_name[:16]:<16} "
            f"{format_amount(c.final_contract_amount, symbol):>14} "
            f"{c.progress_percent:>6.1f}%  "
            f"{format_status(c.status):<8}"
        )

    lines.append(separator)
    lines.append(f"  合計: {len(contracts)}件")
    return "\n".join(lines)


def format_contract_detail(contract: ConstructionContract, symbol: str = "¥") -> str:
    """Render a full detail card for the show command."""
    c = contract
    lines = [
        "═" * 60,
        f"  工事請負台帳 詳細",
        "═" * 60,
        "",
        "【基本情報】",
        f"  工事番号    : {c.project_number}",
        f"  工事名      : {c.project_name}",
        f"  工事場所    : {c.location}",
        f"  工期        : {c.start_date} 〜 {c.end_date}",
        f"  ステータス  : {format_status(c.status)}",
        "",
        "【契約情報】",
        f"  請負業者名  : {c.contractor_name}",
        f"  契約金額    : {format_amount(c.contract_amount, symbol)}",
        f"  変更金額    : {'+' if c.change_amount >= 0 else ''}{format_amount(c.change_amount, symbol)}",
        f"  最終契約金額: {format_amount(c.final_contract_amount, symbol)}",
        "",
        "【支払情報】",
        f"  前払金      : {format_amount(c.advance_payment, symbol)}",
        f"  中間払い    : {format_amount(c.interim_payment, symbol)}",
        f"  完成払い    : {format_amount(c.completion_payment, symbol)}",
        f"  支払済み    : {format_amount(c.paid_amount, symbol)}",
        f"  未払い残高  : {format_amount(c.remaining_amount, symbol)}",
        "",
        "【進捗管理】",
        f"  進捗率      : {format_progress_bar(c.progress_percent)}",
        f"  検査日      : {format_date(c.inspection_date)}",
        f"  完成日      : {format_date(c.completion_date)}",
        f"  備考        : {c.notes or '—'}",
        "",
        "【システム情報】",
        f"  登録日時    : {c.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"  更新日時    : {c.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "═" * 60,
    ]
    return "\n".join(lines)


def format_summary_report(
    contracts: list[ConstructionContract],
    stats: dict,
    symbol: str = "¥",
) -> str:
    """Render an aggregated summary report."""
    status_lines = []
    for sv, count in stats.get("by_status", {}).items():
        label = _STATUS_LABEL.get(ContractStatus(sv), sv)
        status_lines.append(f"    {label:<8}: {count}件")

    lines = [
        "═" * 60,
        "  工事請負台帳 集計レポート",
        "═" * 60,
        "",
        f"  工事件数          : {stats['count']}件",
        "",
        "  【契約金額集計】",
        f"  契約金額合計      : {format_amount(stats['total_contract'], symbol)}",
        f"  最終契約金額合計  : {format_amount(stats['total_final_contract'], symbol)}",
        "",
        "  【支払集計】",
        f"  支払済み合計      : {format_amount(stats['total_paid'], symbol)}",
        f"  未払い残高合計    : {format_amount(stats['total_remaining'], symbol)}",
        "",
        "  【ステータス別件数】",
        *status_lines,
        "═" * 60,
    ]
    return "\n".join(lines)
