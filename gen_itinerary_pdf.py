#!/usr/bin/env python3
"""香港国際大会スケジュール PDF 生成（いつものフォーマット／1ページ）"""
from fpdf import FPDF

FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
BLACK = (0, 0, 0)
HEAD_FILL = (220, 220, 220)

# 各日付ブロック: (日付, [(時間, 予定), ...])
DAYS = [
    ("2026/7/3（金）", [
        ("18:45", "NH811 成田発"),
        ("22:35", "香港着"),
        ("", "ホテル着"),
    ]),
    ("2026/7/4（土）", [
        ("06:15", "代議員朝食会 送迎バス発（インターコンチネンタル グランドスタンフォード香港 前）"),
        ("07:00", "日本ライオンズ代議員会・朝食会  リーガルエアポートホテル"),
        ("09:00", "開会式"),
        ("18:30", "MD333「議長・ガバナーを囲む晩餐会」"),
        ("", "好彩海鮮酒家（帝国中心 2F）"),
    ]),
    ("2026/7/5（日）", [
        ("09:00", "二日目総会"),
        ("09:00", "代議員投票"),
        ("18:30", "333-E地区「ガバナーを囲む夕食会」"),
        ("", "Regal Kowloon Hotel（リーガルカオルーン）"),
    ]),
    ("2026/7/6（月）", [
        ("12:30", "メルビン・ジョーンズ・フェロー昼食会"),
        ("15:00", "閉会式（鈴木光成ガバナー就任）"),
        ("18:30", "333-E地区「鈴木光成ガバナーを励ます夕べ」"),
        ("", "会場未定"),
    ]),
    ("2026/7/7（火）", [
        ("19:00", "国際役員との集い"),
    ]),
    ("2026/7/8（水）", [
        ("09:30", "NH812 香港発"),
        ("15:10", "成田着"),
    ]),
]

HOTEL = [
    "New World Millennium Hong Kong Hotel",
    "72 Mody Road, Tsim Sha Tsui East, Kowloon, Hong Kong",
]

pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.add_font("jp", "", FONT)
pdf.set_auto_page_break(False)
pdf.set_margins(18, 16, 18)
pdf.add_page()
EPW = pdf.epw

# ---- タイトル ----
pdf.set_font("jp", "", 17)
pdf.set_text_color(*BLACK)
pdf.cell(0, 11, "香港国際大会スケジュール", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(2)

# ---- 表 ----
W_DATE, W_TIME = 34, 18
W_PLAN = EPW - W_DATE - W_TIME
LH = 6.0

pdf.set_draw_color(0, 0, 0)
pdf.set_line_width(0.3)

# ヘッダ行
pdf.set_font("jp", "", 11)
pdf.set_fill_color(*HEAD_FILL)
pdf.cell(W_DATE, 9, "日付", border=1, align="C", fill=True)
pdf.cell(W_TIME, 9, "時間", border=1, align="C", fill=True)
pdf.cell(W_PLAN, 9, "予定", border=1, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

pdf.set_font("jp", "", 10)
for date, rows in DAYS:
    # 各予定行の高さ（予定セルの折返しを計測）
    line_heights = []
    for tm, plan in rows:
        n = len(pdf.multi_cell(W_PLAN - 3, LH, plan, dry_run=True, output="LINES"))
        line_heights.append(max(1, n) * LH)
    block_h = sum(line_heights)

    x0 = pdf.l_margin
    y0 = pdf.get_y()

    # 日付セル（ブロック全体を縦結合）
    pdf.rect(x0, y0, W_DATE, block_h)
    pdf.set_xy(x0, y0 + (block_h - LH) / 2)
    pdf.cell(W_DATE, LH, date, align="C")

    # 時間・予定セル
    y = y0
    for (tm, plan), rh in zip(rows, line_heights):
        pdf.set_xy(x0 + W_DATE, y)
        pdf.cell(W_TIME, rh, tm, border="LR", align="C")
        pdf.set_xy(x0 + W_DATE + W_TIME, y)
        pdf.multi_cell(W_PLAN, LH, plan, border="R", align="L",
                       max_line_height=LH, new_x="LMARGIN", new_y="TOP")
        y += rh
    # ブロック下罫線
    pdf.line(x0 + W_DATE, y0 + block_h, x0 + EPW, y0 + block_h)
    pdf.set_xy(x0, y0 + block_h)

pdf.ln(8)

# ---- 滞在ホテル ----
pdf.set_font("jp", "", 11)
pdf.cell(28, 7, "滞在ホテル", align="L")
pdf.set_font("jp", "", 10)
pdf.multi_cell(EPW - 28, 6, "\n".join(HOTEL))

out = "/home/user/ClaudeGitHub/第108回香港国際大会_旅程表.pdf"
pdf.output(out)
print("written:", out)
