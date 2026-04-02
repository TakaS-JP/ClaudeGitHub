"""Data models for the Construction Contract Ledger (工事請負台帳) system."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional


class ContractStatus(str, Enum):
    """工事ステータス"""
    PLANNED = "planned"          # 計画中
    ACTIVE = "active"            # 進行中
    INSPECTION = "inspection"    # 検査中
    COMPLETED = "completed"      # 完成
    CANCELLED = "cancelled"      # 中止


@dataclass
class ConstructionContract:
    """
    工事請負台帳の1件分のレコード。
    基本情報・契約情報・支払情報・進捗管理を統合したフラットな集約データ。
    """

    # ── 基本情報 ──────────────────────────────────────────────
    project_number: str           # 工事番号（主キー）
    project_name: str             # 工事名
    location: str                 # 工事場所
    start_date: date              # 工期開始日
    end_date: date                # 工期終了日

    # ── 契約情報 ──────────────────────────────────────────────
    contractor_name: str          # 請負業者名
    contract_amount: int          # 契約金額（円）

    change_amount: int = 0        # 変更金額（変更契約の累計差額）

    # ── 支払情報 ──────────────────────────────────────────────
    advance_payment: int = 0      # 前払金
    interim_payment: int = 0      # 中間払い
    completion_payment: int = 0   # 完成払い

    # ── 進捗管理 ──────────────────────────────────────────────
    progress_percent: float = 0.0              # 工事進捗率（0.0〜100.0）
    inspection_date: Optional[date] = None     # 検査日
    completion_date: Optional[date] = None     # 完成日
    notes: str = ""                             # 備考

    # ── システム管理 ──────────────────────────────────────────
    status: ContractStatus = ContractStatus.PLANNED
    created_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    # ── 計算項目（非保存） ────────────────────────────────────

    @property
    def final_contract_amount(self) -> int:
        """最終契約金額 = 契約金額 + 変更金額"""
        return self.contract_amount + self.change_amount

    @property
    def paid_amount(self) -> int:
        """支払済み金額 = 前払金 + 中間払い + 完成払い"""
        return self.advance_payment + self.interim_payment + self.completion_payment

    @property
    def remaining_amount(self) -> int:
        """未払い残高 = 最終契約金額 - 支払済み金額"""
        return self.final_contract_amount - self.paid_amount
