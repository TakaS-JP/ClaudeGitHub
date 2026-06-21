#!/usr/bin/env python3
"""香港国際大会スケジュール PDF 生成（スタイリッシュ版／1ページ）"""
from fpdf import FPDF

FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"

# ---- カラーパレット（ライオンズ：ネイビー × ゴールド）----
NAVY = (23, 42, 77)
NAVY2 = (38, 64, 115)
BLUE = (41, 98, 168)
GOLD = (192, 152, 62)
INK = (45, 49, 58)
SOFT = (108, 116, 130)
ROW_A = (255, 255, 255)
ROW_B = (244, 246, 251)
LINE = (214, 220, 232)

# 各日付ブロック: (日付, 曜日, [(時間, 予定, 強調?), ...])
DAYS = [
    ("7/3", "金", [
        ("18:45", "NH811 成田発", False),
        ("22:35", "香港着 ／ ホテルチェックイン", False),
    ]),
    ("7/4", "土", [
        ("06:15", "代議員朝食会 送迎バス発（インターコンチネンタル グランドスタンフォード香港 前）", False),
        ("07:00", "日本ライオンズ代議員会・朝食会  リーガルエアポートホテル", False),
        ("09:00", "開会式", False),
        ("18:30", "MD333「議長・ガバナーを囲む晩餐会」  好彩海鮮酒家（帝国中心 2F）", True),
    ]),
    ("7/5", "日", [
        ("09:00", "二日目総会 ／ 代議員投票", False),
        ("18:30", "333-E地区「ガバナーを囲む夕食会」  Regal Kowloon Hotel", True),
    ]),
    ("7/6", "月", [
        ("12:30", "メルビン・ジョーンズ・フェロー昼食会", False),
        ("15:00", "閉会式（鈴木光成ガバナー就任）", True),
        ("18:30", "333-E地区「鈴木光成ガバナーを励ます夕べ」  会場未定", True),
    ]),
    ("7/7", "火", [
        ("19:00", "国際役員との集い", False),
    ]),
    ("7/8", "水", [
        ("09:30", "NH812 香港発", False),
        ("15:10", "成田着", False),
    ]),
]

HOTEL_NAME = "New World Millennium Hong Kong Hotel"
HOTEL_ADDR = "72 Mody Road, Tsim Sha Tsui East, Kowloon, Hong Kong"

pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.add_font("jp", "", FONT)
pdf.set_auto_page_break(False)
LM, RM, TM = 16, 16, 14
pdf.set_margins(LM, TM, RM)
pdf.add_page()
EPW = pdf.epw
PW = pdf.w


def rrect(x, y, w, h, r, style="F"):
    pdf.rect(x, y, w, h, style=style, round_corners=True, corner_radius=r)


# ============ ヘッダーバナー ============
BANNER_H = 30
pdf.set_fill_color(*NAVY)
pdf.rect(0, 0, PW, BANNER_H, style="F")
# ゴールドのアクセントライン
pdf.set_fill_color(*GOLD)
pdf.rect(0, BANNER_H, PW, 1.4, style="F")

# 主タイトル
pdf.set_xy(LM, 7)
pdf.set_font("jp", "", 19)
pdf.set_text_color(255, 255, 255)
pdf.cell(0, 9, "香港国際大会スケジュール", align="L")
# 英字サブ
pdf.set_xy(LM, 18.5)
pdf.set_font("jp", "", 9)
pdf.set_text_color(206, 214, 230)
pdf.cell(0, 5, "108th Lions Clubs International Convention  /  Hong Kong", align="L")

# 右側：会期 & 主役
pdf.set_xy(PW - RM - 70, 9)
pdf.set_font("jp", "", 10)
pdf.set_text_color(*GOLD)
pdf.cell(70, 5.5, "2026.7.3（金）— 7.8（水）", align="R", new_x="LEFT", new_y="NEXT")
pdf.set_x(PW - RM - 70)
pdf.set_font("jp", "", 8.5)
pdf.set_text_color(206, 214, 230)
pdf.cell(70, 5, "ライオンズクラブ国際協会 333-E地区", align="R", new_x="LEFT", new_y="NEXT")
pdf.set_x(PW - RM - 70)
pdf.cell(70, 5, "鈴木 光成 ガバナーエレクト", align="R")

pdf.set_y(BANNER_H + 8)

# ============ テーブル ============
W_DATE, W_TIME = 30, 18
W_PLAN = EPW - W_DATE - W_TIME
GAP_X = LM + W_DATE + W_TIME  # plan列 開始X
LH = 5.8
PAD = 3.2

pdf.set_font("jp", "", 10)
alt = False
for day_idx, (md, wd, rows) in enumerate(DAYS):
    # 行高さを計測（予定セルの折返し）
    heights = []
    for tm, plan, key in rows:
        n = len(pdf.multi_cell(W_PLAN - PAD * 2, LH, plan, dry_run=True, output="LINES"))
        heights.append(max(1, n) * LH + 3.2)
    block_h = sum(heights)

    y0 = pdf.get_y()
    x = LM

    # 背景（交互）
    pdf.set_fill_color(*(ROW_B if alt else ROW_A))
    pdf.rect(x, y0, EPW, block_h, style="F")
    alt = not alt

    # 日付セル（ネイビー帯）
    pdf.set_fill_color(*NAVY2)
    pdf.rect(x, y0, W_DATE, block_h, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("jp", "", 15)
    pdf.set_xy(x, y0 + block_h / 2 - 6)
    pdf.cell(W_DATE, 7, md, align="C", new_x="LEFT", new_y="NEXT")
    pdf.set_x(x)
    pdf.set_font("jp", "", 9)
    pdf.set_text_color(*GOLD)
    pdf.cell(W_DATE, 5, f"（{wd}）", align="C")

    # 各予定行
    y = y0
    for (tm, plan, key), rh in zip(rows, heights):
        cy = y + rh / 2
        # 時間
        pdf.set_font("jp", "", 9.5)
        pdf.set_text_color(*(GOLD if key else BLUE))
        pdf.set_xy(x + W_DATE, cy - 2.6)
        pdf.cell(W_TIME, 5, tm, align="C")
        # 強調バー
        if key:
            pdf.set_fill_color(*GOLD)
            pdf.rect(GAP_X + 1.0, y + 2.0, 1.6, rh - 4.0, style="F")
        # 予定テキスト
        pdf.set_font("jp", "", 10)
        pdf.set_text_color(*(NAVY if key else INK))
        nlines = len(pdf.multi_cell(W_PLAN - PAD * 2, LH, plan, dry_run=True, output="LINES"))
        text_h = nlines * LH
        pdf.set_xy(GAP_X + PAD + 2.0, cy - text_h / 2)
        pdf.multi_cell(W_PLAN - PAD * 2 - 2.0, LH, plan, align="L",
                       max_line_height=LH, new_x="LMARGIN", new_y="TOP")
        # 行内の薄い区切り線（最終行以外）
        y += rh
        if (tm, plan, key) != rows[-1]:
            pdf.set_draw_color(*LINE)
            pdf.set_line_width(0.2)
            pdf.line(x + W_DATE + 2, y, x + EPW - 2, y)

    pdf.set_xy(x, y0 + block_h)

# テーブル外枠
table_top = BANNER_H + 8
table_bottom = pdf.get_y()
pdf.set_draw_color(*NAVY2)
pdf.set_line_width(0.4)
pdf.rect(LM, table_top, EPW, table_bottom - table_top)
pdf.line(LM + W_DATE, table_top, LM + W_DATE, table_bottom)
pdf.line(LM + W_DATE + W_TIME, table_top, LM + W_DATE + W_TIME, table_bottom)

# ============ 滞在ホテル カード ============
pdf.ln(7)
cy = pdf.get_y()
CARD_H = 18
pdf.set_fill_color(247, 249, 252)
rrect(LM, cy, EPW, CARD_H, 2.5, style="F")
pdf.set_draw_color(*LINE)
pdf.set_line_width(0.3)
rrect(LM, cy, EPW, CARD_H, 2.5, style="D")
# 左のゴールド帯
pdf.set_fill_color(*GOLD)
rrect(LM, cy, 2.2, CARD_H, 1.0, style="F")

pdf.set_xy(LM + 8, cy + 3.5)
pdf.set_font("jp", "", 9)
pdf.set_text_color(*SOFT)
pdf.cell(0, 4.5, "滞在ホテル / HOTEL", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(LM + 8)
pdf.set_font("jp", "", 11)
pdf.set_text_color(*NAVY)
pdf.cell(0, 5.5, HOTEL_NAME, new_x="LMARGIN", new_y="NEXT")
pdf.set_x(LM + 8)
pdf.set_font("jp", "", 8.5)
pdf.set_text_color(*SOFT)
pdf.cell(0, 4.5, HOTEL_ADDR)

# フッター
pdf.set_xy(LM, pdf.h - 12)
pdf.set_font("jp", "", 7.5)
pdf.set_text_color(170, 176, 188)
pdf.cell(EPW, 4, "作成日：2026年6月21日", align="R")

out = "/home/user/ClaudeGitHub/第108回香港国際大会_旅程表.pdf"
pdf.output(out)
print("written:", out)
