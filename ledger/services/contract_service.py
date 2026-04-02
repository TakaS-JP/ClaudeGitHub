"""Business logic and validation for Construction Contract Ledger operations."""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Optional

from ledger.models.contract import ConstructionContract, ContractStatus
from ledger.storage.ledger_store import LedgerStore

logger = logging.getLogger("construction_ledger.service")


class ContractService:
    """
    Validates input, applies business rules, and delegates persistence to LedgerStore.
    All mutating operations update `updated_at` automatically.
    """

    def __init__(self, store: LedgerStore) -> None:
        self._store = store

    # ── 新規登録 ──────────────────────────────────────────────────────────────

    def create_contract(
        self,
        project_number: str,
        project_name: str,
        location: str,
        start_date: date,
        end_date: date,
        contractor_name: str,
        contract_amount: int,
    ) -> ConstructionContract:
        """新規工事を登録する。入力値を検証し永続化する。"""
        self._validate_dates(start_date, end_date)
        self._validate_amount(contract_amount, "契約金額")

        contract = ConstructionContract(
            project_number=project_number,
            project_name=project_name,
            location=location,
            start_date=start_date,
            end_date=end_date,
            contractor_name=contractor_name,
            contract_amount=contract_amount,
        )
        self._store.create(contract)
        logger.info("工事登録: %s (%s)", project_number, project_name)
        return contract

    # ── 変更契約 ──────────────────────────────────────────────────────────────

    def apply_change_order(self, project_number: str, delta: int) -> ConstructionContract:
        """変更金額を加算する（負値で減額）。最終契約金額が正であることを検証する。"""
        contract = self._require(project_number)
        new_final = contract.contract_amount + contract.change_amount + delta
        if new_final < 0:
            raise ValueError(
                f"変更後の最終契約金額が負になります: {new_final:,}円"
            )
        contract.change_amount += delta
        contract.updated_at = datetime.now(tz=timezone.utc)
        self._store.update(contract)
        logger.info(
            "変更契約: %s 変更金額=%+,d 最終契約金額=%,d",
            project_number, delta, contract.final_contract_amount,
        )
        return contract

    # ── 支払い更新 ────────────────────────────────────────────────────────────

    def record_payment(
        self,
        project_number: str,
        advance: Optional[int] = None,
        interim: Optional[int] = None,
        completion: Optional[int] = None,
    ) -> ConstructionContract:
        """支払い金額を更新する（指定された項目のみ上書き）。"""
        contract = self._require(project_number)

        if advance is not None:
            self._validate_amount(advance, "前払金")
            contract.advance_payment = advance
        if interim is not None:
            self._validate_amount(interim, "中間払い")
            contract.interim_payment = interim
        if completion is not None:
            self._validate_amount(completion, "完成払い")
            contract.completion_payment = completion

        if contract.paid_amount > contract.final_contract_amount:
            raise ValueError(
                f"支払済み金額({contract.paid_amount:,}円)が"
                f"最終契約金額({contract.final_contract_amount:,}円)を超えています"
            )

        contract.updated_at = datetime.now(tz=timezone.utc)
        self._store.update(contract)
        logger.info(
            "支払更新: %s 支払済み=%,d 残高=%,d",
            project_number, contract.paid_amount, contract.remaining_amount,
        )
        return contract

    # ── 進捗更新 ──────────────────────────────────────────────────────────────

    def update_progress(
        self,
        project_number: str,
        percent: Optional[float] = None,
        inspection_date: Optional[date] = None,
        completion_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> ConstructionContract:
        """進捗情報を更新する。進捗率100%で自動的にステータスをCOMPLETEDに変更する。"""
        contract = self._require(project_number)

        if percent is not None:
            if not (0.0 <= percent <= 100.0):
                raise ValueError(f"進捗率は0〜100の範囲で入力してください: {percent}")
            contract.progress_percent = percent
            if percent == 100.0 and contract.status not in (
                ContractStatus.COMPLETED, ContractStatus.CANCELLED
            ):
                contract.status = ContractStatus.COMPLETED
                logger.info("ステータス自動更新: %s → 完成", project_number)

        if inspection_date is not None:
            contract.inspection_date = inspection_date
        if completion_date is not None:
            contract.completion_date = completion_date
        if notes is not None:
            contract.notes = notes

        contract.updated_at = datetime.now(tz=timezone.utc)
        self._store.update(contract)
        logger.info("進捗更新: %s %.1f%%", project_number, contract.progress_percent)
        return contract

    # ── ステータス更新 ────────────────────────────────────────────────────────

    def update_status(self, project_number: str, status: ContractStatus) -> ConstructionContract:
        """工事ステータスを手動で変更する。"""
        contract = self._require(project_number)
        contract.status = status
        contract.updated_at = datetime.now(tz=timezone.utc)
        self._store.update(contract)
        logger.info("ステータス更新: %s → %s", project_number, status.value)
        return contract

    # ── フィールド更新 ────────────────────────────────────────────────────────

    def update_fields(self, project_number: str, **kwargs) -> ConstructionContract:
        """基本情報・契約情報の任意フィールドを更新する。"""
        contract = self._require(project_number)
        allowed = {
            "project_name", "location", "start_date", "end_date",
            "contractor_name", "contract_amount",
        }
        for key, value in kwargs.items():
            if key not in allowed:
                raise ValueError(f"更新できないフィールドです: {key}")
            if key == "contract_amount":
                self._validate_amount(value, "契約金額")
            setattr(contract, key, value)

        if hasattr(kwargs, "start_date") or hasattr(kwargs, "end_date"):
            self._validate_dates(contract.start_date, contract.end_date)

        contract.updated_at = datetime.now(tz=timezone.utc)
        self._store.update(contract)
        return contract

    # ── 集計 ──────────────────────────────────────────────────────────────────

    def get_summary_stats(self, contracts: list[ConstructionContract]) -> dict:
        """契約リストの集計統計を返す。"""
        if not contracts:
            return {
                "count": 0,
                "total_contract": 0,
                "total_final_contract": 0,
                "total_paid": 0,
                "total_remaining": 0,
                "by_status": {},
            }

        by_status: dict[str, int] = {}
        for c in contracts:
            by_status[c.status.value] = by_status.get(c.status.value, 0) + 1

        return {
            "count": len(contracts),
            "total_contract": sum(c.contract_amount for c in contracts),
            "total_final_contract": sum(c.final_contract_amount for c in contracts),
            "total_paid": sum(c.paid_amount for c in contracts),
            "total_remaining": sum(c.remaining_amount for c in contracts),
            "by_status": by_status,
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _require(self, project_number: str) -> ConstructionContract:
        contract = self._store.get(project_number)
        if contract is None:
            raise ValueError(f"工事番号が見つかりません: {project_number}")
        return contract

    @staticmethod
    def _validate_dates(start: date, end: date) -> None:
        if start >= end:
            raise ValueError(
                f"工期開始日({start})は工期終了日({end})より前でなければなりません"
            )

    @staticmethod
    def _validate_amount(amount: int, label: str) -> None:
        if amount < 0:
            raise ValueError(f"{label}は0以上の値を入力してください: {amount:,}円")
