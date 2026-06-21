#!/usr/bin/env python3
"""第108回 香港国際大会 旅程表 PDF 生成スクリプト"""
from fpdf import FPDF

FONT = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
NAVY = (28, 58, 110)
LIGHT = (224, 231, 245)
GREY = (240, 240, 240)
RED = (200, 60, 60)
GREEN = (30, 130, 70)


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("jp", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "第108回 香港国際大会 旅程表 / ライオンズクラブ国際協会 333-E地区", align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("jp", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, f"- {self.page_no()} -", align="C")


pdf = PDF(orientation="P", unit="mm", format="A4")
pdf.add_font("jp", "", FONT)
pdf.set_auto_page_break(True, margin=15)
pdf.add_page()
EPW = pdf.epw  # effective page width


def h1(txt):
    pdf.set_font("jp", "", 18)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(0, 9, txt, align="C")
    pdf.ln(1)


def sub(txt):
    pdf.set_font("jp", "", 11)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(0, 6, txt, align="C")
    pdf.ln(3)


def h2(txt):
    pdf.ln(2)
    pdf.set_font("jp", "", 13)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "  " + txt, new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(1.5)


def note(txt, color=NAVY):
    pdf.set_font("jp", "", 9)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, 5, txt)
    pdf.ln(0.5)


def table(headers, rows, widths):
    # scale widths to EPW
    scale = EPW / sum(widths)
    widths = [w * scale for w in widths]
    line_h = 5.0
    # header row
    pdf.set_font("jp", "", 9)
    pdf.set_fill_color(*LIGHT)
    pdf.set_text_color(*NAVY)
    pdf.set_draw_color(180, 180, 180)
    for w, htxt in zip(widths, headers):
        pdf.cell(w, 7, htxt, border=1, align="C", fill=True)
    pdf.ln(7)
    # body
    pdf.set_font("jp", "", 8.5)
    pdf.set_text_color(40, 40, 40)
    fill = False
    for row in rows:
        # compute needed height per cell using multi_cell measurement
        heights = []
        for w, cell in zip(widths, row):
            txt = cell[0] if isinstance(cell, tuple) else cell
            lines = pdf.multi_cell(w, line_h, txt, dry_run=True, output="LINES")
            heights.append(max(1, len(lines)) * line_h)
        rh = max(heights)
        # page break check
        if pdf.get_y() + rh > pdf.page_break_trigger:
            pdf.add_page()
            pdf.set_font("jp", "", 9)
            pdf.set_fill_color(*LIGHT)
            pdf.set_text_color(*NAVY)
            for w, htxt in zip(widths, headers):
                pdf.cell(w, 7, htxt, border=1, align="C", fill=True)
            pdf.ln(7)
            pdf.set_font("jp", "", 8.5)
        x0, y0 = pdf.get_x(), pdf.get_y()
        for w, cell in zip(widths, row):
            if isinstance(cell, tuple):
                txt, col = cell
            else:
                txt, col = cell, (40, 40, 40)
            x, y = pdf.get_x(), pdf.get_y()
            pdf.set_fill_color(*(GREY if fill else (255, 255, 255)))
            pdf.rect(x, y, w, rh, style="F")
            pdf.set_text_color(*col)
            pdf.multi_cell(w, line_h, txt, border=1, align="L",
                           new_x="RIGHT", new_y="TOP", max_line_height=line_h)
            pdf.set_xy(x + w, y)
        pdf.set_xy(x0, y0 + rh)
        fill = not fill
    pdf.ln(2)


# ---------- Title ----------
h1("第108回 香港国際大会 旅程表")
sub("ライオンズクラブ国際協会 333-E地区  /  鈴木 光成 ガバナーエレクト")
sub("会期：2026年7月3日（金）〜7月7日（火）  渡航：7月3日〜7月8日（水）\n会場：アジアワールド・エキスポ（AsiaWorld-Expo）／香港")

# ---------- 航空便 ----------
h2("航空便（ANA）")
table(["区分", "日付", "便名", "区間", "出発", "到着"],
      [["往路", "7/3(金)", "NH811", "成田(NRT)→香港(HKG)", "18:45", "22:35"],
       ["復路", "7/8(水)", "NH812", "香港(HKG)→成田(NRT)", "9:30", "15:10"]],
      [12, 16, 16, 50, 16, 16])

# ---------- 宿泊 ----------
h2("宿泊ホテル")
table(["項目", "内容"],
      [["ホテル名", "New World Millennium Hong Kong Hotel（by Rosewood Hotel Group）"],
       ["住所", "72 Mody Road, Tsim Sha Tsui East, Kowloon（九龍 尖沙咀東 麼地道72號）"],
       ["宿泊期間", "2026年7月3日(金)〜7月8日(水) ※7/3深夜チェックイン"],
       ["受付番号", "HN6Q48WN（ホテル確認番号は Pending／後日通知）"]],
      [22, 110])
note("立地メモ：麼地道(Mody Road)沿い。晩餐会会場(帝国中心=68號)・夕食会会場(リーガルカオルーン=71號)と同じ通り・徒歩圏。", NAVY)

# ---------- 全体スケジュール ----------
h2("全体スケジュール（一覧）")
table(["日付", "主な公式行事", "333複合地区／333-E地区 関連行事（出席）"],
      [["7/3(金)", "香港着(22:35)、登録、展示ホール", "—"],
       ["7/4(土)", "開会総会、ビジネス・セッション", "代議員会・朝食会 ／ ○議長・ガバナーを囲む晩餐会"],
       ["7/5(日)", "二日目総会、選挙、各種セミナー", "○ガバナーを囲む夕食会（公式晩餐会は不参加）"],
       ["7/6(月)", "選挙、MJF昼食会、閉会総会(ガバナー就任)", "○鈴木ガバナーを励ます夕べ"],
       ["7/7(火)", "国際役員との集い", "—"],
       ["7/8(水)", "帰国（成田15:10着）", "—"]],
      [16, 58, 70])

# ---------- 7/3 ----------
h2("7月3日（金）")
table(["時刻", "行事", "会場"],
      [["8:00〜17:00", "登録", "アジアワールド・エキスポ"],
       ["10:00〜17:00", "展示ホール", "アジアワールド・エキスポ"],
       ["18:45", "NH811 成田(NRT)発", "成田空港"],
       ["22:35", "香港(HKG)着→入国・ホテルへ・チェックイン", "→ New World Millennium Hong Kong Hotel"]],
      [22, 62, 60])

# ---------- 7/4 ----------
h2("7月4日（土）")
table(["時刻", "行事", "会場／備考"],
      [["6:15", ("★チャーターバス① 出発（333-E指定便）", RED), "インターコンチネンタル グランドスタンフォード香港 前"],
       ["6:55", "代議員朝食会会場 着", "リーガルエアポートホテル"],
       ["7:00〜8:00", "日本ライオンズ代議員会・朝食会（コアタイム）", "リーガルエアポート 1F グランドボールルームI〜III／10,000円＋バス4,000〜5,000円"],
       ["8:15→8:20", "バス① 朝食会場発 → EXPO着", "リーガルエアポート → アジアワールド・エキスポ"],
       ["9:00〜12:30", "開会総会", "アジアワールド・エキスポ"],
       ["10:00〜17:00", "展示ホール", "アジアワールド・エキスポ"],
       ["16:00〜17:30", "ビジネス・セッション（国際理事候補者の紹介）", "アジアワールド・エキスポ"],
       ["18:30〜20:00", ("インターナショナル・ショー → 不参加", RED), "アジアワールド・エキスポ"],
       ["18:30〜20:30", ("○議長・ガバナーを囲む晩餐会（受付18:00〜）", GREEN), "帝国中心 2F「好彩海鮮酒家」麼地道68號／21,000円・中華10品"]],
      [22, 60, 62])

# ---------- 7/5 ----------
h2("7月5日（日）")
table(["時刻", "行事", "会場／備考"],
      [["9:00〜17:00", "登録", "アジアワールド・エキスポ"],
       ["9:00〜12:00", "二日目総会", "アジアワールド・エキスポ"],
       ["9:00〜17:00", "選挙", "アジアワールド・エキスポ"],
       ["13:15〜17:00", "各種セミナー", "アジアワールド・エキスポ"],
       ["18:30〜20:30", ("○333-E地区「ガバナーを囲む夕食会」", GREEN), "リーガルカオルーンホテル 宴会場 麼地道71號／20,000円・中華10品"],
       ["20:00〜22:00", ("元国際会長等 晩餐会 → 不参加", RED), "アジアワールド・エキスポ"]],
      [22, 60, 62])

# ---------- 7/6 ----------
h2("7月6日（月）")
table(["時刻", "行事", "会場／備考"],
      [["9:00〜17:00", "登録", "アジアワールド・エキスポ"],
       ["9:00〜14:30", "選挙", "アジアワールド・エキスポ"],
       ["9:30〜11:45", "各種セミナー", "アジアワールド・エキスポ"],
       ["12:30〜14:30", "メルビン・ジョーンズ・フェロー(MJF)昼食会", "アジアワールド・エキスポ"],
       ["15:00〜17:30", ("★閉会総会（鈴木ガバナーエレクトがリボンを外し新ガバナー就任）", NAVY), "アジアワールド・エキスポ"],
       ["18:30〜(予定)", ("○333-E地区「鈴木光成ガバナーを励ます夕べ」", GREEN), "会場未定（決定次第連絡）／20,000円(予定)・鈴木ガバナーが主役"]],
      [22, 60, 62])

# ---------- 7/7 ----------
h2("7月7日（火）")
table(["時刻", "行事", "会場"],
      [["19:00〜21:00", "国際役員との集い", "アジアワールド・エキスポ"]],
      [22, 62, 60])

# ---------- 7/8 ----------
h2("7月8日（水）")
table(["時刻", "行事", "会場"],
      [["(午前)", "チェックアウト・空港へ移動", "ホテル → 香港国際空港"],
       ["9:30", "NH812 香港(HKG)発", "香港国際空港"],
       ["15:10", "成田(NRT)着", "成田空港"]],
      [22, 62, 60])

# ---------- 申込・登録料 ----------
h2("申込・登録料 まとめ")
table(["行事", "日程", "登録料／会費", "申込先"],
      [["代議員会・朝食会", "7/4 7:00", "10,000円(＋バス4,000〜5,000円)", "md333@nifty.com（名簿締切5/12）"],
       ["○議長・ガバナーを囲む晩餐会", "7/4 18:30", "21,000円", "lions@lc333-e.com（5/18締切）"],
       ["○ガバナーを囲む夕食会", "7/5 18:30", "20,000円", "—"],
       ["○鈴木ガバナーを励ます夕べ", "7/6 18:30", "20,000円(予定)", "mika-takakura@takakura-kk.co.jp"]],
      [50, 20, 44, 50])
note("振込先（晩餐会等）：常陽銀行 本店営業部（普）3671538 ／ ライオンズクラブ国際協会333-E地区 集金用 キャビネット会計 大窪聡史", NAVY)

# ---------- 注記 ----------
h2("メモ・注意事項")
for t in [
    "・7/3は香港着22:35のため、当日の登録(〜17:00)には間に合わず。登録は翌7/4朝。",
    "・7/4朝の代議員会・朝食会に出席のため、バス①(6:15発)の発着点へ。宿泊先から徒歩圏だが早朝のため6:00頃出発を推奨。",
    "・7/6「励ます夕べ」の会場は未定（決定次第、本旅程表を更新）。",
    "・ホテル予約名義は高倉(Takamasa)。鈴木様分の手配状況は要確認。",
]:
    note(t, (60, 60, 60))

pdf.ln(2)
note("作成日：2026年6月21日", (150, 150, 150))

out = "/home/user/ClaudeGitHub/第108回香港国際大会_旅程表.pdf"
pdf.output(out)
print("written:", out)
