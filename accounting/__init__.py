"""セイキョウ経理自動化システム.

マネーフォワードクラウド会計向けの仕訳CSV自動生成ツール.

主な機能:
- クレジットカード明細(Excel)を取り込み, 仕訳CSVに変換
- 銀行振込履歴(CSV)を取り込み, 仕訳CSVに変換
- ルールに基づき勘定科目・部門を自動判定
- 売上を部門別に振り分け, MoneyForwardの部門別レポートに反映
"""

from accounting.models.journal_entry import JournalEntry
from accounting.classifiers.rule_engine import RuleEngine

__all__ = ["JournalEntry", "RuleEngine"]
__version__ = "0.1.0"
