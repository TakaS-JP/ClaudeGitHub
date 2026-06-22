#!/usr/bin/env python3
"""香港国際大会スケジュール HTML 生成（Box保存・印刷用／PDFと同デザイン）"""
import html

EXPO = "AsiaWorld-Expo（香港国際空港／ランタオ島）"
DAYS = [
    ("7/3", "金", [
        ("18:45", "NH811 成田発", False, ""),
        ("22:35", "香港着 ／ ホテルチェックイン", False, ""),
    ]),
    ("7/4", "土", [
        ("06:15", "代議員朝食会 送迎バス発（インターコンチネンタル グランドスタンフォード香港 前）", False,
         "70 Mody Road, Tsim Sha Tsui East, Kowloon（尖沙咀東 麼地道70號）"),
        ("07:00", "日本ライオンズ代議員会・朝食会  リーガルエアポートホテル", False,
         "9 Cheong Tat Road, Chek Lap Kok, Lantau（大嶼山赤鱲角 暢達路9號）"),
        ("09:00", "開会式", False, EXPO),
        ("18:30", "MD333「議長・ガバナーを囲む晩餐会」  好彩海鮮酒家（帝国中心 2F）", True,
         "68 Mody Road, Tsim Sha Tsui East, Kowloon（尖沙咀東 麼地道68號 帝国中心2F） TEL +852-2311-4567"),
    ]),
    ("7/5", "日", [
        ("09:00", "二日目総会 ／ 代議員投票", False, EXPO),
        ("18:30", "333-E地区「ガバナーを囲む夕食会」  Regal Kowloon Hotel", True,
         "71 Mody Road, Tsim Sha Tsui, Kowloon（尖沙咀 麼地道71號） TEL +852-2722-1818"),
    ]),
    ("7/6", "月", [
        ("12:30", "メルビン・ジョーンズ・フェロー昼食会", False, EXPO),
        ("15:00", "閉会式（鈴木光成ガバナー就任）", True, EXPO),
        ("18:30", "333-E地区「鈴木光成ガバナーを励ます夕べ」  会場未定", True, "会場が決定次第、追って記載"),
    ]),
    ("7/7", "火", [
        ("19:00", "国際役員との集い", False, EXPO),
    ]),
    ("7/8", "水", [
        ("09:30", "NH812 香港発", False, ""),
        ("15:10", "成田着", False, ""),
    ]),
]
HOTEL_NAME = "New World Millennium Hong Kong Hotel"
HOTEL_ADDR = "72 Mody Road, Tsim Sha Tsui East, Kowloon, Hong Kong"


def esc(s):
    return html.escape(s)


rows_html = []
for md, wd, rows in DAYS:
    cells = []
    for i, (tm, plan, key, addr) in enumerate(rows):
        cls = "ev key" if key else "ev"
        addr_html = f'<div class="addr">{esc(addr)}</div>' if addr else ""
        first = ' first' if i == 0 else ''
        cells.append(
            f'<tr class="{cls}{first}">'
            + (f'<td class="date" rowspan="{len(rows)}"><div class="d">{esc(md)}</div>'
               f'<div class="w">（{esc(wd)}）</div></td>' if i == 0 else '')
            + f'<td class="time">{esc(tm)}</td>'
            + f'<td class="plan"><div class="p">{esc(plan)}</div>{addr_html}</td>'
            + '</tr>'
        )
    rows_html.append("".join(cells))
body_rows = "\n".join(rows_html)

DOC = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>香港国際大会スケジュール</title>
<style>
  :root {{
    --navy:#172a4d; --navy2:#264073; --blue:#2962a8;
    --gold:#c0983e; --ink:#2d313a; --soft:#6c7482;
    --rowb:#f4f6fb; --line:#d6dce8;
  }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:"Hiragino Kaku Gothic ProN","Yu Gothic","Meiryo","Noto Sans JP",sans-serif;
         margin:0; color:var(--ink); background:#fff; }}
  .sheet {{ max-width:900px; margin:0 auto; padding:0 0 30px; }}
  .banner {{ background:var(--navy); color:#fff; padding:18px 28px 14px;
             display:flex; justify-content:space-between; align-items:flex-end;
             border-bottom:3px solid var(--gold); }}
  .banner h1 {{ margin:0; font-size:25px; letter-spacing:1px; }}
  .banner .sub {{ margin-top:6px; font-size:12px; color:#ced6e6; letter-spacing:1px; }}
  .banner .meta {{ text-align:right; font-size:12px; color:#ced6e6; line-height:1.7; }}
  .banner .meta .term {{ color:var(--gold); font-size:13px; font-weight:bold; }}
  table {{ width:calc(100% - 56px); margin:24px 28px 0; border-collapse:collapse;
           border:1.5px solid var(--navy2); }}
  th {{ background:#dcdcdc; color:var(--navy); font-size:13px; padding:8px; border:1px solid var(--navy2); }}
  td {{ border-left:1px solid var(--line); border-right:1px solid var(--line); }}
  td.date {{ background:var(--navy2); color:#fff; text-align:center; vertical-align:middle;
             width:84px; border:1px solid var(--navy2); }}
  td.date .d {{ font-size:20px; font-weight:bold; }}
  td.date .w {{ font-size:11px; color:var(--gold); margin-top:2px; }}
  td.time {{ width:64px; text-align:center; color:var(--blue); font-size:13px;
             padding:9px 4px; white-space:nowrap; }}
  td.plan {{ padding:9px 12px; }}
  td.plan .p {{ font-size:14px; }}
  td.plan .addr {{ font-size:11px; color:var(--soft); margin-top:3px; }}
  tr.ev td {{ border-bottom:1px solid var(--line); }}
  tr.ev.first td {{ border-top:1px solid var(--navy2); }}
  tr:nth-child(odd):not(.key) td.plan, tr:nth-child(odd):not(.key) td.time {{ }}
  tr.key td.time {{ color:var(--gold); font-weight:bold; }}
  tr.key td.plan {{ background:#fbf7ec; border-left:3px solid var(--gold); }}
  tr.key td.plan .p {{ color:var(--navy); font-weight:bold; }}
  .hotel {{ margin:26px 28px 0; background:#f7f9fc; border:1px solid var(--line);
            border-left:5px solid var(--gold); border-radius:6px; padding:12px 18px; }}
  .hotel .lbl {{ font-size:11px; color:var(--soft); }}
  .hotel .name {{ font-size:15px; color:var(--navy); font-weight:bold; margin:3px 0; }}
  .hotel .ad {{ font-size:12px; color:var(--soft); }}
  .foot {{ text-align:right; margin:16px 28px 0; font-size:11px; color:#aab0bc; }}
  @media print {{ .banner {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
                 td.date, th, tr.key td.plan {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }} }}
</style>
</head>
<body>
<div class="sheet">
  <div class="banner">
    <div>
      <h1>香港国際大会スケジュール</h1>
      <div class="sub">108th Lions Clubs International Convention / Hong Kong</div>
    </div>
    <div class="meta">
      <div class="term">2026.7.3（金） — 7.8（水）</div>
      <div>ライオンズクラブ国際協会 333-E地区</div>
      <div>鈴木 光成 ガバナーエレクト</div>
    </div>
  </div>
  <table>
    <thead><tr><th>日付</th><th>時間</th><th>予定</th></tr></thead>
    <tbody>
{body_rows}
    </tbody>
  </table>
  <div class="hotel">
    <div class="lbl">滞在ホテル / HOTEL</div>
    <div class="name">{esc(HOTEL_NAME)}</div>
    <div class="ad">{esc(HOTEL_ADDR)}</div>
  </div>
  <div class="foot">作成日：2026年6月21日</div>
</div>
</body>
</html>
"""

out = "/home/user/ClaudeGitHub/第108回香港国際大会_旅程表.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(DOC)
print("written:", out, len(DOC), "bytes")
