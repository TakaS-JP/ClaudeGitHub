"""動作確認用のクレカ明細サンプルExcelを生成するスクリプト.

実行:
    python samples/generate_credit_card_sample.py

出力先: samples/credit_card_sample.xlsx
"""

from __future__ import annotations

from pathlib import Path

import openpyxl


SAMPLE_ROWS = [
    ["利用日", "利用店名", "利用金額", "メモ", "カード名"],
    ["2026/04/01", "AMAZON.CO.JP", 4980, "事務用品", "rakuten"],
    ["2026/04/02", "JR東日本 モバイルSuica", 8500, "営業交通費", "rakuten"],
    ["2026/04/03", "スターバックス 渋谷店", 1280, "打合せ", "rakuten"],
    ["2026/04/05", "GOOGLE ADS", 55000, "EC事業部 広告", "amex"],
    ["2026/04/06", "META PLATFORMS", 38000, "Facebook広告", "amex"],
    ["2026/04/08", "ヨドバシカメラ", 22800, "PCモニタ", "rakuten"],
    ["2026/04/10", "東京メトロ", 3600, "出張", "rakuten"],
    ["2026/04/12", "ASKUL", 7800, "コピー用紙", "rakuten"],
    ["2026/04/15", "AMAZON 返金", -1980, "返品", "rakuten"],
    ["2026/04/18", "ZOOM.US", 2178, "Web会議", "rakuten"],
    ["2026/04/20", "タクシー JPN TAXI", 4320, "深夜帰宅", "rakuten"],
    ["2026/04/22", "TARGET不明な店", 9800, "要確認", "rakuten"],
    ["2026/04/25", "楽天カード 年会費", 11000, "", "rakuten"],
]


def main() -> None:
    out = Path(__file__).parent / "credit_card_sample.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "credit_card"
    for row in SAMPLE_ROWS:
        ws.append(row)
    wb.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
