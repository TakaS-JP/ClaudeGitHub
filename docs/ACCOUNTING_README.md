# セイキョウ 経理自動化システム

マネーフォワードクラウド会計向けに **クレジットカード明細(Excel)** と
**銀行振込履歴(CSV)** を取り込み, ルールに従って自動仕訳を行い,
**部門別売上**を可視化できる仕訳インポートCSVを生成するツールです.

---

## 解決する業務課題

| 課題 | 本ツールでの解決 |
|------|------------------|
| マネーフォワードはクレカと同期しているが, **仕訳の自動振り分けが追いつかない** | エクセル明細を取り込み, ルールに従って勘定科目・補助科目を自動付与した仕訳CSVを生成 |
| インターネットバンキングからCSVダウンロードしても, **仕訳は手作業** | 銀行CSVを直接読み込み, 取引摘要から自動仕訳化 |
| **部門別売上**(EC, 卸売, 店舗A/B, コンサル...) が見えない | 入金ルールで `貸方部門` を自動付与, MoneyForwardの部門別レポートに反映 |
| カード/口座が複数あり**支払元が混在** | `--card` `--account` で支払元を識別, 補助科目で分けて記帳 |
| 摘要から判断できない取引が混じる | 未マッチは「雑費」(支出) / 「本社・売上高」(入金) にフォールバック → 後で目視レビュー可能 |

---

## アーキテクチャ

```
┌─────────────────┐    ┌────────────────┐    ┌──────────────────────┐
│ クレカ明細 (Excel)│──▶│ Importer       │──▶│ RawTransaction[]      │
└─────────────────┘    │ - credit_card  │   └──────────────────────┘
┌─────────────────┐    │ - bank_transfer│             │
│ 銀行履歴 (CSV)   │──▶│                │             ▼
└─────────────────┘    └────────────────┘    ┌──────────────────────┐
                                              │ RuleEngine            │
                       accounting_config/     │ (rules.yaml)          │
                       rules.yaml ──────────▶│ 勘定科目/補助/部門/税区分│
                                              └──────────┬───────────┘
                                                         ▼
                                              ┌──────────────────────┐
                                              │ MoneyForwardCSVExporter│
                                              │ → 仕訳インポートCSV    │
                                              └──────────────────────┘
                                                         │
                                                         ▼
                                              MoneyForwardクラウド会計
                                              [仕訳のインポート] にUP
```

---

## セットアップ

```bash
pip install -r requirements_accounting.txt
```

依存関係: `openpyxl` (Excel読込), `PyYAML` (ルール定義), `pytest` (テスト).

---

## ディレクトリ構成

```
accounting/
├── models/journal_entry.py      # JournalEntry / RawTransaction データクラス
├── importers/
│   ├── credit_card.py           # クレカExcel取り込み
│   └── bank_transfer.py         # 銀行CSV取り込み
├── classifiers/rule_engine.py   # YAMLルールベース仕訳判定
├── exporters/moneyforward.py    # 仕訳CSV書き出し (BOM付UTF-8/CRLF)
├── utils/logger.py
└── cli.py                       # CLIエントリポイント

accounting_config/
└── rules.yaml                   # 仕訳ルール定義 (★ここを編集して運用)

samples/
├── bank_transfer_sample.csv
└── generate_credit_card_sample.py

tests/accounting/
├── test_rule_engine.py
├── test_credit_card.py
├── test_bank_transfer.py
└── test_exporter.py

docs/
└── ACCOUNTING_README.md         # 本ファイル
```

---

## 使い方

### 1. ルールファイルを準備

`accounting_config/rules.yaml` を自社事情に合わせて編集します.
編集ポイントは大きく3つ:

1. **`payment_accounts`** – クレカ・銀行口座の補助科目
2. **`expense_rules`** – 経費の勘定科目判定 (摘要キーワード→科目)
3. **`income_rules`** – 売上の部門振り分け (キーワード→部門)

### 2. クレジットカードExcel明細を仕訳CSVに変換

```bash
python -m accounting.cli credit-card \
    --input  data/202604_rakuten_card.xlsx \
    --output out/202604_credit_journal.csv \
    --rules  accounting_config/rules.yaml \
    --card   rakuten \
    --start-no 1
```

期待されるExcelの列(揺らぎ吸収済):
- 利用日 / ご利用日 / 日付 / 取引日
- 利用店名 / ご利用先 / 摘要
- 利用金額 / 金額
- (任意) メモ / 備考
- (任意) カード名 / カード会社

> ヒント: マイナス金額は **返金** として `direction=income` に振り替わります.

### 3. 銀行振込履歴CSVを仕訳CSVに変換

```bash
python -m accounting.cli bank \
    --input  data/202604_mufg.csv \
    --output out/202604_bank_journal.csv \
    --rules  accounting_config/rules.yaml \
    --account mufg \
    --start-no 1001
```

期待されるCSVの列:
- 取引日 / 日付
- 摘要 / お取引内容
- お支払金額 + お預り金額 (二列方式) もしくは 金額 (一列方式)
- (任意) 取引メモ

文字コードは UTF-8 / CP932 / Shift_JIS を自動判定します.

### 4. マネーフォワードクラウド会計にインポート

1. ブラウザで MoneyForward にログイン
2. **[各種設定] → [仕訳のインポート]**
3. 「仕訳帳」形式を選択し, 生成された CSV をアップロード
4. プレビューで内容確認 → 取り込み確定

> CSVは **UTF-8 (BOM付き) / CRLF / 15列固定** で出力されます.

### 5. 部門別売上の集計サマリ

```bash
python -m accounting.cli summary --input out/202604_bank_journal.csv
```

```
=== 部門別売上 ===
  EC事業部              1,240,000 円
  卸売部門                605,000 円
  店舗A                   485,000 円
  コンサル事業部           165,000 円
  合計                  2,495,000 円

=== 勘定科目別 経費 ===
  給料手当                540,000 円
  地代家賃                330,000 円
  ...
```

---

## 仕訳ルールの書き方

`accounting_config/rules.yaml` の構造:

```yaml
payment_accounts:
  "credit_card:rakuten":            # source:payment_id をキーに使用
    account: 未払金
    sub_account: 楽天カード
  "bank_transfer:mufg":
    account: 普通預金
    sub_account: 三菱UFJ銀行

expense_rules:
  - name: 旅費交通費-JR/私鉄
    keywords: [JR東日本, 東京メトロ, 都営, タクシー]
    debit_account: 旅費交通費
    debit_tax_category: 課税仕入 10%

income_rules:
  - name: 売上-EC事業部
    keywords: [楽天市場, AMAZON 売上, BASE, SHOPIFY]
    credit_account: 売上高
    credit_sub_account: EC売上
    credit_department: EC事業部     # ★ ここで部門が決まる
    credit_tax_category: 課税売上 10%

defaults:
  expense:
    debit_account: 雑費
    debit_tax_category: 課税仕入 10%
  income:
    credit_account: 売上高
    credit_department: 本社
    credit_tax_category: 課税売上 10%
```

### キーワードマッチの仕組み

- マッチ対象は `description + counterparty + memo` の連結文字列
- 比較前に **NFKC正規化(全角→半角) → 小文字化 → 空白除去** が行われる
- `JR東日本` `jr東日本` `ＪＲ東日本` は同じものとして扱われる
- ルールは上から順に評価され, 最初にマッチしたものが採用される

### 部門別売上の運用

1. **MoneyForward側で部門マスタを登録** (例: EC事業部 / 卸売部門 / 店舗A / 店舗B / コンサル事業部 / 本社)
2. `rules.yaml` の `income_rules` でキーワードと部門を紐づける
3. 取り込み後, MoneyForwardの **[会計帳簿] → [部門別損益計算書]** で売上を確認

---

## テストの実行

```bash
# クレカサンプルExcelを生成 (初回のみ)
python samples/generate_credit_card_sample.py

# テスト実行
pytest tests/accounting -v
```

期待結果:
- `test_rule_engine.py`: 6件 PASS (ルール判定)
- `test_credit_card.py`: 2件 PASS (Excel取り込み)
- `test_bank_transfer.py`: 2件 PASS (CSV取り込み)
- `test_exporter.py`: 1件 PASS (CSV出力)

---

## 運用フロー(月次想定)

```
月初:
  1. クレカ会社の利用明細Excelをダウンロード/作成
  2. 銀行のインターネットバンキングから当月のCSVをダウンロード

仕訳生成:
  3. python -m accounting.cli credit-card --input ...  --output out/credit.csv
  4. python -m accounting.cli bank        --input ...  --output out/bank.csv
  5. python -m accounting.cli summary     --input out/bank.csv   ← 部門別売上を即確認

確認:
  6. 摘要列が「default-expense」「default-income」となっている行を目視確認
     → 必要に応じて rules.yaml にキーワードを追加して再生成

取り込み:
  7. MoneyForward → [仕訳のインポート] で out/*.csv をUP
  8. 部門別損益計算書で売上を確認
```

---

## よくあるカスタマイズ

| やりたいこと | 編集箇所 |
|------------|---------|
| 新しいカードを追加 | `payment_accounts:` に `"credit_card:<id>"` を追加, `--card <id>` で起動 |
| 部門を追加 (例: 新規事業部) | `income_rules` に `credit_department: 新規事業部` のルールを追加 |
| 摘要から判別不能な取引を要レビューに | `defaults.expense.debit_account` を `仮払金` に変更 |
| 経費にも部門を付けたい | `expense_rules` の各エントリに `debit_department:` を追加 |
| インボイス区分を細かく分けたい | `*_tax_category` を `課税売上 10%軽減` などMF側区分に合わせる |

---

## 制限事項

- 本ツールは **CSVを生成するだけ**です. MoneyForwardへの自動アップロード(API)は行いません.
- マネーフォワードの仕訳インポートCSV仕様(15列)は本ツール作成時点のものです. 仕様変更時は `models/journal_entry.py` の `MONEYFORWARD_CSV_HEADERS` を見直してください.
- 摘要キーワードに依存するため, **一度生成した仕訳は必ず人間がレビュー**してください. `summary` コマンドや MoneyForward上のプレビューで確認できます.
