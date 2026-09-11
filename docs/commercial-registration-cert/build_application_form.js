// 商業登記電子証明書「電子証明書発行申請書」ドラフト生成スクリプト
// 実行: NODE_PATH=<docxをインストールしたnode_modules> node build_application_form.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, HeadingLevel, ShadingType,
  Header, Footer, PageBreak, LevelFormat, VerticalAlign, PageNumber,
} = require("docx");

const FONT = { ascii: "ＭＳ 明朝", eastAsia: "ＭＳ 明朝", hAnsi: "ＭＳ 明朝" };
const GOTHIC = { ascii: "ＭＳ ゴシック", eastAsia: "ＭＳ ゴシック", hAnsi: "ＭＳ ゴシック" };
const TABLE_W = 9600;
const thin = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
const borders = { top: thin, bottom: thin, left: thin, right: thin };

const run = (text, opts = {}) => new TextRun({ text, font: FONT, size: 21, ...opts });
const p = (text, opts = {}) => new Paragraph({ children: [run(text, opts.run || {})], ...opts });
const blank = () => new Paragraph({ children: [run("")] });

function cell(children, width, opts = {}) {
  const kids = Array.isArray(children) ? children : [children];
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    ...opts,
    children: kids.map((c) => (typeof c === "string" ? p(c) : c)),
  });
}
const labelCell = (text, width) =>
  cell(p(text), width, { shading: { type: ShadingType.CLEAR, fill: "EDEDED", color: "auto" } });

function twoColTable(rows, w1 = 2800, w2 = TABLE_W - 2800) {
  return new Table({
    width: { size: TABLE_W, type: WidthType.DXA },
    columnWidths: [w1, w2],
    rows: rows.map(([label, value]) => new TableRow({
      children: [labelCell(label, w1), cell(value, w2)],
    })),
  });
}

function bullets(items, ref = "bul") {
  return items.map((t) => new Paragraph({
    numbering: { reference: ref, level: 0 },
    children: [run(t)],
  }));
}

const note = (text) => new Paragraph({
  children: [run(text, { size: 18 })],
  spacing: { before: 40, after: 40 },
});

const title = (text) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 200, after: 300 },
  children: [new TextRun({ text, font: GOTHIC, size: 36, bold: true })],
});

const h = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 240, after: 120 },
  children: [new TextRun({ text, font: GOTHIC, size: 24, bold: true })],
});

// ---------- ページ1: 申請書 ----------
const page1 = [
  title("電子証明書発行申請書"),
  p("（商業登記法第12条の2、商業登記規則第33条の2）", { alignment: AlignmentType.CENTER, run: { size: 18 } }),
  blank(),
  p("　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　令和　　年　　月　　日"),
  blank(),
  p("　　　　　　　　　　　　　　　法務局　　　　　　　　　支局・出張所　御中"),
  p("（本店又は主たる事務所を管轄する登記所）", { run: { size: 18 } }),
  blank(),
  p("　下記のとおり、商業登記に基づく電子証明書の発行を申請します。"),
  blank(),
  twoColTable([
    ["(1) 商号又は名称", [p("　"), p("　")]],
    ["(2) 商号又は名称の\nローマ字表記（任意）".replace("\n", ""), p("　")],
    ["(3) 本店又は主たる事務所", [p("　"), p("　")]],
    ["(4) 被証明者の氏名", p("　")],
    ["(5) 被証明者の氏名のローマ字表記（任意）", p("　")],
    ["(6) 被証明者の資格", p("　　　　　　　　　　　（例：代表取締役、代表社員、理事長）")],
    ["(7) 証明期間", [
      p("☐ １か月"),
      p("☐ ３か月　☐ ６か月　☐ ９か月　☐ 12か月　☐ 15か月"),
      p("☐ 18か月　☐ 21か月　☐ 24か月　☐ 27か月"),
    ]],
    ["(8) 手数料", [
      p("金　　　　　　　　　円　（収入印紙又は登記印紙を右欄に貼付）"),
    ]],
    ["(9) 証明書発行申請ファイル", [
      p("☐ CD　☐ DVD　☐ USBメモリ　に格納して添付"),
      p("（フォルダを作らず、当該申請用のファイル１件のみを直接格納）", { run: { size: 18 } }),
    ]],
  ]),
  blank(),
  new Table({
    width: { size: TABLE_W, type: WidthType.DXA },
    columnWidths: [2800, 4400, 2400],
    rows: [
      new TableRow({ children: [
        labelCell("申請人", 2800),
        cell([p("本店：　"), p("商号：　"), p("資格・氏名：　")], 4400),
        cell([p("登記所届出印", { alignment: AlignmentType.CENTER, run: { size: 18 } }), p("　"), p("　"), p("　"), p("印", { alignment: AlignmentType.CENTER })], 2400),
      ]}),
      new TableRow({ children: [
        labelCell("代理人\n（代理人が提出する場合のみ）".replace("\n", ""), 2800),
        cell([p("住所：　"), p("氏名：　"), p("電話：　")], 4400),
        cell([p("　"), p("　"), p("　"), p("印", { alignment: AlignmentType.CENTER })], 2400),
      ]}),
      new TableRow({ children: [
        labelCell("収入印紙貼付欄", 2800),
        cell([p("　"), p("　"), p("　"), p("　（消印しないこと）", { run: { size: 18 } })], 6800, { columnSpan: 2 }),
      ]}),
    ],
  }),
  blank(),
  note("※ 申請人欄の印は、管轄登記所に届け出た印鑑（会社実印）を押印してください。"),
  note("※ 代理人が提出する場合は、代理人欄を記載のうえ、別紙の委任状を添付してください。"),
  note("※ (1)(3)(4)(6) は登記事項証明書の記載どおり（全角）に記載してください。"),
];

// ---------- ページ2: 委任状 ----------
const page2 = [
  new Paragraph({ children: [new PageBreak()] }),
  title("委　任　状"),
  blank(),
  p("　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　令和　　年　　月　　日"),
  blank(),
  twoColTable([
    ["代理人　住所", p("　")],
    ["代理人　氏名", p("　")],
  ]),
  blank(),
  p("　私は、上記の者を代理人と定め、下記の権限を委任します。"),
  blank(),
  p("記", { alignment: AlignmentType.CENTER, run: { bold: true } }),
  blank(),
  ...bullets([
    "商業登記に基づく電子証明書（下記事項）の発行申請に関する一切の件",
    "電子証明書発行確認票の受領に関する一切の件",
    "上記に付随する一切の件",
  ], "num"),
  blank(),
  twoColTable([
    ["商号又は名称", p("　")],
    ["本店又は主たる事務所", p("　")],
    ["被証明者の氏名", p("　")],
    ["被証明者の資格", p("　")],
    ["証明期間", p("　　　　か月")],
  ]),
  blank(),
  blank(),
  p("　　　　　　　　　　　　　　委任者　本店　　"),
  p("　　　　　　　　　　　　　　　　　　商号　　"),
  p("　　　　　　　　　　　　　　　　　　資格・氏名　　　　　　　　　　　　　　　　　　　㊞（登記所届出印）"),
];

// ---------- ページ3: 記入要領・チェックリスト ----------
const feeRows = [
  ["証明期間", "手数料（令和7年4月1日以降）"],
  ["１か月", "500円"],
  ["３か月", "1,100円"],
  ["６か月", "2,000円"],
  ["12か月", "3,800円"],
  ["24か月", "7,400円"],
  ["27か月", "8,300円"],
  ["９・15・18・21か月", "法務省の手数料表で要確認（本書では未確認）"],
];
const feeTable = new Table({
  width: { size: 6000, type: WidthType.DXA },
  columnWidths: [2500, 3500],
  rows: feeRows.map(([a, b], i) => new TableRow({
    children: i === 0 ? [labelCell(a, 2500), labelCell(b, 3500)] : [cell(p(a), 2500), cell(p(b), 3500)],
  })),
});

const page3 = [
  new Paragraph({ children: [new PageBreak()] }),
  title("記入要領・提出チェックリスト（社内用）"),
  h("１　この様式の位置づけ（重要）"),
  ...bullets([
    "法務省の案内では、電子証明書発行申請書は「商業登記電子認証ソフト」で鍵ペアファイル・証明書発行申請ファイル（SHINSEIファイル）と同時に「発行申請書・委任状ファイル」（PDF）として作成されます。正式提出には、原則としてソフトが出力したPDFを印刷して使用してください。",
    "法務局サイトには「電子証明書の発行申請書の様式」ページ（houmukyoku.moj.go.jp/homu/ELECTRON_13-1.html）があり、申請書様式・記載例のPDFが公開されています。本書はそのPDFを取得できない環境で作成した下書きであり、公式様式と項目順・レイアウトが異なる可能性があります。窓口提出前に公式様式と照合してください。",
    "本書の(1)〜(7)の項目名・番号は、法務省「証明書発行申請ファイルの作成に当たっての留意点」に記載の入力項目に合わせています。(2)(5)のローマ字表記は任意項目です。",
  ]),
  h("２　記入時の確認事項"),
  ...bullets([
    "(1) 商号・(3) 本店・(4) 代表者氏名・(6) 資格は、最新の登記事項証明書と一字一句一致させる（全角）。",
    "証明期間は１か月、又は３か月から27か月まで（３か月単位）。証明期間中に商号・本店・代表者の変更登記をすると失効するため、変更予定がある場合は短めを選ぶ。",
    "手数料は証明期間に応じた額の収入印紙（又は登記印紙）を貼付する。消印はしない。",
    "押印は管轄登記所に届け出た印鑑（会社実印）。認印は不可。",
    "証明書発行申請ファイルは、CD・DVD・USBメモリにフォルダを作らず１件のみ直接格納する。媒体は返却される。",
    "代理人（担当者）が窓口へ行く場合は、申請書の代理人欄を記載し、委任状（登記所届出印を押印）を添付する。",
    "旧証明書は有効期限切れのため、旧証明書によるオンライン申請はできない。書面申請とする。",
  ]),
  h("３　窓口持参物"),
  ...bullets([
    "電子証明書発行申請書（登記所届出印を押印、収入印紙貼付）",
    "証明書発行申請ファイルを格納した CD／DVD／USBメモリ",
    "委任状（代理人が提出する場合）",
    "登記所届出印（窓口で訂正を求められた場合に備えて）",
    "手数料相当の現金（収入印紙を法務局内の印紙売場で購入する場合）",
  ]),
  h("４　手数料表"),
  feeTable,
  note("出典：法務省「商業登記に基づく電子認証制度手数料改定（引下げ）のお知らせ」（令和7年4月1日改定）。9・15・18・21か月の額は本書作成時に確認できていません。"),
  h("５　交付後の流れ"),
  ...bullets([
    "窓口で「電子証明書発行確認票」が交付される。記載のシリアル番号を商業登記電子認証ソフトに入力し、電子証明書をダウンロードする。",
    "ダウンロードした電子証明書ファイルとパスワードは、社内の管理台帳に登録し、有効期限をカレンダーに登録する。",
  ]),
  h("６　出典（2026年9月11日確認）"),
  ...bullets([
    "法務省「ファイル形式（従来型）の商業登記電子証明書の取得方法」 https://www.moj.go.jp/MINJI/minji06_00028.html",
    "法務局「電子証明書の発行申請書の様式」 https://houmukyoku.moj.go.jp/homu/ELECTRON_13-1.html",
    "法務省「電子証明書の発行申請」 https://www.moj.go.jp/ONLINE/ELECTRON/13-1.html",
    "法務省「証明書発行申請ファイルの作成に当たっての留意点」 https://www.moj.go.jp/ONLINE/CERTIFICATION/GUIDE/guide03-01.html",
    "法務省「商業登記電子認証ソフト 操作手引書 第2.6版（令和7年4月）」 https://www.moj.go.jp/content/001436290.pdf",
    "法務省「商業登記に基づく電子認証制度手数料改定（引下げ）のお知らせ」 https://www.moj.go.jp/ONLINE/CERTIFICATION/fee00.html",
  ]),
];

const doc = new Document({
  creator: "総務",
  title: "電子証明書発行申請書（下書き）",
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
  },
  numbering: {
    config: [
      { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "・", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 480, hanging: 240 } } } }] },
      { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1．", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 480 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "【社内確認用ドラフト】正式提出は法務省ソフト出力の申請書又は法務局公式様式を使用", font: GOTHIC, size: 16, color: "808080" })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })],
      })] }),
    },
    children: [...page1, ...page2, ...page3],
  }],
});

const out = path.join(__dirname, "電子証明書発行申請書_下書き.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("written:", out); });
