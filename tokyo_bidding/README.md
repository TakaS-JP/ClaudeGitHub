# 東京都入札案件 ダウンローダ

東京都のオープンデータカタログ (CKAN API) から入札・調達関連のデータセットを取得し、
統合された一覧表 (CSV / Markdown) を生成するスクリプトです。

## データ取得元

| 優先 | 名称 | URL |
|------|------|-----|
| 1 | 東京都オープンデータカタログ (CKAN API) | https://catalog.data.metro.tokyo.lg.jp/ |
| 2 | 東京都電子調達システム 入札情報サービス | https://www.e-tokyo.lg.jp/choutatu_ppij/ppij/pub |
| 3 | 政府電子調達ポータル 落札実績オープンデータ | https://www.p-portal.go.jp/pps-web-biz/UAB02/OAB0201 |

## 使い方

```bash
# デフォルト (キーワード: 入札/落札/契約/調達、最大100件)
python tokyo_bidding/download.py

# キーワードと件数を指定
python tokyo_bidding/download.py --keyword 入札 --keyword 工事 --limit 50

# 本体CSVのDLはせずメタ情報のみ取得 (高速)
python tokyo_bidding/download.py --no-download
```

依存ライブラリは Python 標準ライブラリのみ。`pip install` 不要です。

## 出力

```
output/
├── tokyo_bidding_YYYYMMDD.csv    # 統合一覧 (UTF-8 BOM 付き、Excel 互換)
├── tokyo_bidding_YYYYMMDD.md     # 一覧 Markdown 表 (先頭 200 件)
└── raw/<dataset_id>/<resource>   # 元データ (CSV/XLSX)
```

CSV の列:

| 列名 | 内容 |
|------|------|
| source | データ取得元 (`ckan` 等) |
| dataset_id | データセット ID |
| dataset_title | データセット名 |
| organization | 発注機関 / 所管局 |
| case_name | 件名 / 案件名 |
| case_no | 案件番号 |
| category | 業種・区分 |
| bid_open_date | 開札日 |
| award_date | 契約日 / 落札日 |
| award_amount | 契約金額 / 落札金額 |
| awarded_supplier | 契約相手方 |
| resource_url | 元CSV/XLSXの URL |
| resource_format | フォーマット |
| updated | データセット最終更新日時 |

## 注意

- このリポジトリのリモート実行環境では `catalog.data.metro.tokyo.lg.jp` 等への
  アウトバウンドが制限されているため、本スクリプトは **ローカル環境** で実行する想定です。
- 各データセットによって列名が異なるため、列マッピングは `_COL_MAP` で
  代表的な日本語ヘッダを集約しています。新しい列名が出てきた場合は追記してください。
