"""ルールベースの仕訳判定エンジン.

YAMLで定義したキーワードルールに従い, 取引摘要・取引先名から
勘定科目・補助科目・部門・税区分を判定する.

ルール優先順位:
1. ファイル先頭で定義されたルールが上位
2. キーワードは部分一致 (大小文字無視, 全角半角無視)
3. マッチしない場合は default ルールが適用される
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from accounting.models.journal_entry import RawTransaction


@dataclass
class ClassificationResult:
    """ルール判定結果.

    debit/credit の勘定科目とそれぞれの部門・税区分を保持する.
    """

    debit_account: str
    debit_sub_account: str = ""
    debit_department: str = ""
    debit_tax_category: str = "対象外"

    credit_account: str = ""
    credit_sub_account: str = ""
    credit_department: str = ""
    credit_tax_category: str = "対象外"

    matched_rule: str = "default"


def _normalize(text: str) -> str:
    """全角→半角, 小文字化, 空白除去でキーワード比較を安定化."""
    if text is None:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    return text


class RuleEngine:
    """YAML定義に従い RawTransaction を分類する."""

    def __init__(self, rules_path: Path | str):
        rules_path = Path(rules_path)
        with open(rules_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        self._expense_rules: list[dict] = data.get("expense_rules", [])
        self._income_rules: list[dict] = data.get("income_rules", [])
        self._defaults: dict = data.get("defaults", {})
        self._payment_accounts: dict = data.get("payment_accounts", {})

    def payment_account_for(self, source: str, source_id: str = "") -> dict:
        """支払元(クレカ・銀行口座)に対応する勘定科目情報を返す.

        例: クレジットカード→未払金/補助科目"楽天カード", 銀行→普通預金/補助科目"○○銀行".
        """
        key = f"{source}:{source_id}" if source_id else source
        if key in self._payment_accounts:
            return self._payment_accounts[key]
        if source in self._payment_accounts:
            return self._payment_accounts[source]
        # source未定義時のフォールバック
        if source == "credit_card":
            return {"account": "未払金", "sub_account": "クレジットカード"}
        return {"account": "普通預金", "sub_account": ""}

    def classify(self, txn: RawTransaction) -> ClassificationResult:
        """取引を分類して仕訳の借方・貸方情報を返す.

        - 支出の場合: 借方=費用科目, 貸方=支払元(クレカ未払金 or 普通預金).
        - 入金の場合: 借方=普通預金など, 貸方=売上高(部門付).
        """
        haystack = _normalize(f"{txn.description} {txn.counterparty} {txn.memo}")

        rules = self._income_rules if txn.is_income else self._expense_rules

        for rule in rules:
            keywords = rule.get("keywords", [])
            for kw in keywords:
                if _normalize(kw) and _normalize(kw) in haystack:
                    return self._build_result(rule, txn)

        # default
        if txn.is_income:
            d = self._defaults.get("income", {})
            return self._build_result(
                {
                    "name": "default-income",
                    "credit_account": d.get("credit_account", "売上高"),
                    "credit_department": d.get("credit_department", ""),
                    "credit_tax_category": d.get("credit_tax_category", "課税売上 10%"),
                },
                txn,
            )
        d = self._defaults.get("expense", {})
        return self._build_result(
            {
                "name": "default-expense",
                "debit_account": d.get("debit_account", "雑費"),
                "debit_tax_category": d.get("debit_tax_category", "課税仕入 10%"),
            },
            txn,
        )

    def _build_result(self, rule: dict, txn: RawTransaction) -> ClassificationResult:
        """ルール定義から ClassificationResult を組み立てる.

        支出ルールは debit_* を, 入金ルールは credit_* を主に持つ.
        対向科目(支払元)は payment_accounts から自動的に補完する.
        """
        payment = self.payment_account_for(
            txn.source, txn.raw.get("payment_source_id", "")
        )

        if txn.is_income:
            return ClassificationResult(
                debit_account=rule.get("debit_account", payment["account"]),
                debit_sub_account=rule.get("debit_sub_account", payment.get("sub_account", "")),
                debit_department=rule.get("debit_department", ""),
                debit_tax_category=rule.get("debit_tax_category", "対象外"),
                credit_account=rule.get("credit_account", "売上高"),
                credit_sub_account=rule.get("credit_sub_account", ""),
                credit_department=rule.get("credit_department", ""),
                credit_tax_category=rule.get("credit_tax_category", "課税売上 10%"),
                matched_rule=rule.get("name", "income"),
            )

        return ClassificationResult(
            debit_account=rule.get("debit_account", "雑費"),
            debit_sub_account=rule.get("debit_sub_account", ""),
            debit_department=rule.get("debit_department", ""),
            debit_tax_category=rule.get("debit_tax_category", "課税仕入 10%"),
            credit_account=rule.get("credit_account", payment["account"]),
            credit_sub_account=rule.get("credit_sub_account", payment.get("sub_account", "")),
            credit_department=rule.get("credit_department", ""),
            credit_tax_category=rule.get("credit_tax_category", "対象外"),
            matched_rule=rule.get("name", "expense"),
        )
