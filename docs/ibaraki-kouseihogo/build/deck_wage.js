// 茨城県更生保護協会 職員給与規程（案）検討 説明資料（PowerPoint）生成
// 仕様を一度定義し、pptxgenjs（本番）と HTML（確認用プレビュー）の両方に描画する。
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const path = require("path");
const LOGO = { k: fs.readFileSync(path.join(__dirname, "logo_k.png")).toString("base64"), w: fs.readFileSync(path.join(__dirname, "logo_w.png")).toString("base64") };

const OUT = process.argv[2] || "deck.pptx";
const HTML = process.argv[3] || "deck_preview.html";

// ---------- パレット（更生保護のシンボル「ひまわり」の黄を差し色に、深緑を基調） ----------
const C = {
  green: "1F4E3D", green2: "2E6B55", tint: "E9F1EC", tint2: "F4F8F5",
  yellow: "F2B705", text: "222222", muted: "666666", white: "FFFFFF", line: "CBD5CF", red: "B23A3A", grey: "9AA5A0",
};
const FONT = "游ゴシック";

// ---------- 仕様記録 ----------
const slides = [];
function slide(opts = {}) {
  const s = { bg: opts.bg || C.white, els: [], notes: "" };
  slides.push(s);
  const api = {
    text(t, o) { s.els.push({ k: "text", t, ...o }); return api; },
    rect(o) { s.els.push({ k: "rect", ...o }); return api; },
    circle(o) { s.els.push({ k: "circle", ...o }); return api; },
    line(o) { s.els.push({ k: "line", ...o }); return api; },
    table(rows, o) { s.els.push({ k: "table", rows, ...o }); return api; },
    chart(type, data, o) { s.els.push({ k: "chart", type, data, ...o }); return api; },
    image(o) { s.els.push({ k: "image", ...o }); return api; },
    notes(t) { s.notes = t; return api; },
  };
  return api;
}
const yen = (n) => n.toLocaleString("ja-JP");

// ---------- 共通部品 ----------
function header(s, title, sub) {
  s.image({ src: "k", x: 8.98, y: 0.22, w: 0.5, h: 0.59 });
  s.text(title, { x: 0.5, y: 0.3, w: 8.4, h: 0.6, size: 24, bold: true, color: C.green });
  if (sub) s.text(sub, { x: 0.5, y: 0.85, w: 9, h: 0.35, size: 12, color: C.muted });
}
function footer(s, n, src) {
  if (src) s.text("出典：" + src, { x: 0.5, y: 5.2, w: 8.4, h: 0.3, size: 8, color: C.muted });
  s.text(String(n), { x: 9.1, y: 5.2, w: 0.4, h: 0.3, size: 9, color: C.muted, align: "right" });
}
function card(s, x, y, w, h, o = {}) {
  s.rect({ x, y, w, h, fill: o.fill || C.tint2, radius: 0.12, line: o.line || null });
}
function numBadge(s, x, y, n, o = {}) {
  s.circle({ x, y, w: 0.42, h: 0.42, fill: o.fill || C.yellow });
  s.text(String(n), { x, y, w: 0.42, h: 0.42, size: 14, bold: true, color: C.green, align: "center", valign: "middle", margin: 0 });
}

// ---------- データ（出典：令和8年度理事会資料 財産目録 令和8年3月31日現在） ----------
const base = 175000000, bondTotal = 119750000, depTotal = 55250000;
const bondCoupon = 1365500, depInt = 153850;
const NEWJGB = 0.022, DEP = 0.003;
const opt = (shift) => { const jgb = bondTotal + shift, dep = depTotal - shift; const inc = bondCoupon + shift * NEWJGB + dep * DEP; return { jgb, dep, shift, inc, ratio: jgb / base }; };
const options = [["A", "現状維持", opt(0)], ["B", "案の下限 70%", opt(2750000)], ["C", "80%", opt(20250000)], ["D", "満期分を順次振替 約84%", opt(26830000)], ["E", "案の上限 90%", opt(37750000)], ["F", "100%国債（栃木型）", opt(55250000)]];
const pct = (x) => (x * 100).toFixed(1) + "%";

// ===== 職員給与規程（案）検討 スライド内容（deck.js の共通部と結合して使う） =====
const HOURS_M = 120;
const scenW = [["S1", "規程案のまま", 130000], ["S2", "最低賃金1,136円準拠", 136400], ["S3", "時給1,200円相当", 144000], ["S4", "時給1,300円相当", 156000]];
const calcW = (b) => ({ hourly: b / HOURS_M, annual: b * 12 + 120000 + b * 2 });

let n = 0;
// 1 表紙
{
  const s = slide({ bg: C.green }); n++;
  s.circle({ x: 7.6, y: -0.9, w: 3.4, h: 3.4, fill: C.green2 });
  s.circle({ x: 8.35, y: -0.15, w: 1.9, h: 1.9, fill: C.yellow });
  s.image({ src: "w", x: 0.6, y: 0.45, w: 0.8, h: 0.94 });
  s.text("更生保護法人 茨城県更生保護協会", { x: 0.6, y: 1.5, w: 8, h: 0.5, size: 18, color: "CFE3D8" });
  s.text("職員給与規程（案）等の検討", { x: 0.6, y: 2.0, w: 8.5, h: 0.8, size: 38, bold: true, color: C.white });
  s.text("説明資料（案）", { x: 0.6, y: 2.75, w: 8.5, h: 0.7, size: 30, bold: true, color: C.yellow });
  s.text("検討会　令和8年（2026年）9月17日（木）又は18日（金） 11:30〜　於：景山", { x: 0.6, y: 3.75, w: 8.5, h: 0.4, size: 14, color: C.white });
  s.text("※開催日および本件が同日の議題に含まれるかは要確認", { x: 0.6, y: 4.1, w: 8.5, h: 0.3, size: 10, color: "CFE3D8" });
  s.text("作成：理事 鈴木 孝昌　2026年9月12日（9月14日改訂：理事会 2027年1月予定）", { x: 0.6, y: 4.7, w: 8.5, h: 0.35, size: 12, color: "CFE3D8" });
  s.notes("職員給与規程（案）を理事会に付議する前に、最低賃金への適合、時間外単価の算式、就業規則との整合、退職金の引当を確認していただきたい。");
}
// 2 本日のゴール
{
  const s = slide(); n++;
  header(s, "本日のゴール", "決めていただきたいことは3点です");
  const items = [
    ["基準時給の決定", "基本給表を2026年10月18日（予定）改定後の茨城県最低賃金1,136円以上に引き上げる。推奨は時給1,200円相当（週30時間で月額144,000円）"],
    ["就業規則の同時改正", "有給休暇の日数（法定は勤続6年6か月以上で年20日）、通勤手当、期末手当の用語、退職手当の算定基礎を給与規程と合わせて改める"],
    ["退職手当と引当金", "退職手当の見込額（208万〜308万円）と引当金（165万円）の差への対応を決める。基本は引当繰入の増額"],
  ];
  items.forEach((it, i) => {
    const x = 0.5 + i * 3.1;
    card(s, x, 1.45, 2.9, 3.4);
    numBadge(s, x + 0.25, 1.7, i + 1);
    s.text(it[0], { x: x + 0.8, y: 1.68, w: 2.0, h: 0.45, size: 16, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(it[1], { x: x + 0.25, y: 2.35, w: 2.4, h: 2.3, size: 12, color: C.text, valign: "top" });
  });
  footer(s, n);
  s.notes("3点のうち、最低賃金への対応は10月18日までに必要で、時間的に最優先。");
}
// 3 結論
{
  const s = slide(); n++;
  header(s, "結論：6つの提案", "法令に適合させたうえで理事会へ");
  const props = [
    ["基本給表を引上げ", "案の週30時間130,000円は時給1,083円。10月改定後の1,136円を下回るため136,400円以上に"],
    ["推奨は時給1,200円", "月額144,000円。年間人件費は案比＋約20万円。次回以降の最低賃金改定にも耐える"],
    ["時間外単価を法定算式に", "案は年間休日を考慮せず単価が約8%低い。「基本給÷月平均所定労働時間」に改める"],
    ["有給休暇を法定日数に", "現行「年10日」は勤続1年6か月以上で法定未満。勤続16年の事務局長は20日"],
    ["退職金の引当を見直し", "見込額が引当金を43万〜83万円上回る。年間繰入150,000円→25万〜30万円を基本に検討"],
    ["実態確認のうえ付議", "現行支給額、社会保険の適用、職員の同意を確認。必要なら社労士に規程案を確認"],
  ];
  props.forEach((pr, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.5 + col * 3.1, y = 1.4 + row * 1.85;
    card(s, x, y, 2.9, 1.65);
    numBadge(s, x + 0.2, y + 0.2, i + 1);
    s.text(pr[0], { x: x + 0.72, y: y + 0.17, w: 2.1, h: 0.48, size: 14, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(pr[1], { x: x + 0.2, y: y + 0.75, w: 2.55, h: 0.85, size: 10, color: C.text, valign: "top" });
  });
  footer(s, n);
  s.notes("1〜3が給与規程案そのものの修正、4〜6が就業規則・引当・手続きの課題。");
}
// 4 経緯
{
  const s = slide(); n++;
  header(s, "経緯：給与規程の明文化は今回が初めて", "平成25年案は「内容を検討のうえ再提出」の議長裁定");
  const steps = [
    ["平成25年5月8日", "理事会", "就業規則・給与細則・退職慰労金支給細則（案）を当日動議で上程。定年年齢、他法人との給与比較、職員数の弾力化の意見が出て再提出に"],
    ["平成26年7月", "理事会", "大野理事立案の就業規則（全17条）を承認。施行は平成26年6月1日。給与の金額は定めず"],
    ["令和8年7月23日", "検討会", "事務局から平成25年案と議事録のコピーを理事に送付"],
    ["令和8年8月22日", "規程案", "「職員給与規程」（施行日空欄、作成者記載なし）をBoxに保存"],
  ];
  s.line({ x: 0.9, y: 2.0, w: 8.2, h: 0, color: C.line, width: 3 });
  steps.forEach((st, i) => {
    const x = 0.5 + i * 2.3;
    s.circle({ x: x + 0.85, y: 1.76, w: 0.5, h: 0.5, fill: i === 3 ? C.yellow : C.green });
    s.text(String(i + 1), { x: x + 0.85, y: 1.76, w: 0.5, h: 0.5, size: 12, bold: true, color: i === 3 ? C.green : C.white, align: "center", valign: "middle", margin: 0 });
    s.text(st[0], { x, y: 1.3, w: 2.2, h: 0.4, size: 12, bold: true, color: C.green, align: "center", margin: 0 });
    card(s, x, 2.45, 2.2, 2.5);
    s.text(st[1], { x: x + 0.15, y: 2.55, w: 1.9, h: 0.35, size: 12, bold: true, color: C.green, margin: 0 });
    s.text(st[2], { x: x + 0.15, y: 2.95, w: 1.95, h: 1.95, size: 9.5, color: C.text, valign: "top", margin: 0 });
  });
  footer(s, n, "理事会議事録（平成25年5月8日）、事務局「書類送付ご案内」（令和8年7月23日）、Box「0.鈴木孝昌／(更生保護協会)」20260822_更生保護法人茨城県更生保護協会職員給与規程.pdf");
  s.notes("平成25年の理事会で出た「他法人との給与比較」の宿題は、今回もデータが得られていない。");
}
// 5 現行と案の比較
{
  const s = slide(); n++;
  header(s, "現行就業規則と給与規程（案）の比較", "案は金額を初めて明文化。就業規則側にも改正が必要な条項がある");
  const rows = [["項目", "現行就業規則（平成26年6月1日施行）", "給与規程（案）", "整合"],
    ["基本給", "基本給及び諸手当（金額の定めなし）", "週30時間 130,000円、週20〜30時間 88,000〜127,600円、週10〜20時間 44,000〜83,600円、非常勤 時給1,100円", "△ 最低賃金"],
    ["役職手当", "諸手当を付加できる", "事務局長 10,000円、主事 5,000円", "○"],
    ["通勤手当", "実費", "公共交通 実費（上限20,000円）、自家用車 15円/km（上限20,000円）、自転車 2,000円", "△ 上限の新設"],
    ["時間外", "定めなし", "125%（深夜150%）。単価＝基本給×12÷（2週の勤務時間×26）", "△ 算式"],
    ["賞与", "期末手当を6月・12月に支給できる", "年2回、各基本給1月分以内", "△ 用語"],
    ["昇給", "定めなし", "年1回2月決定、4月支給分から", "○"],
    ["支給日", "毎月16日", "毎月16日", "○"],
    ["有給休暇", "年間10日", "（規定なし）", "× 法定未満"],
    ["退職手当", "退職時の月額給与×勤務年数", "（規定なし）", "△ 引当との差"]];
  s.table(rows, { x: 0.5, y: 1.3, w: 9.0, colW: [1.1, 2.6, 4.2, 1.1], size: 8.5, align: ["l", "l", "l", "c"] });
  footer(s, n, "現行就業規則、職員給与規程（案）（Box「0.鈴木孝昌／(更生保護協会)」20260822_更生保護法人茨城県更生保護協会職員給与規程.pdf）");
  s.notes("○は整合、△は修正が必要、×は法令に反する部分。");
}
// 6 最低賃金
{
  const s = slide(); n++;
  header(s, "最低賃金との比較：10月改定後は全区分が下回る", "茨城県 1,074円（2025年10月12日〜）→ 1,136円（2026年10月18日予定、答申8月24日）");
  s.chart("bar", [{ name: "時給換算", labels: ["A 週30h\n130,000円", "B 週20h\n88,000円", "C 週10h\n44,000円", "非常勤\n時給", "最低賃金\n現行", "最低賃金\n改定後"], values: [1083, 1100, 1100, 1100, 1074, 1136] }],
    { x: 0.4, y: 1.3, w: 5.6, h: 3.8, colors: [C.green2, C.green2, C.green2, C.green2, C.grey, C.red], showValue: true, fmt: "#,##0\"円\"", barDir: "col", valAxisMax: 1250 });
  card(s, 6.3, 1.35, 3.2, 3.7, { fill: C.tint });
  s.text("読み取り", { x: 6.5, y: 1.45, w: 2.8, h: 0.4, size: 13, bold: true, color: C.green, margin: 0 });
  s.text([
    "案は概ね時給1,100円で設計。現行1,074円は満たすが、改定後1,136円を全区分で下回る",
    "週30時間で1,136円を満たす月額は136,400円以上（1,136円×120時間）",
    "月平均所定労働時間120時間は、1日6時間×年間所定労働日数240日÷12で算定（日数は要確認）",
    "最低賃金の比較では通勤手当・賞与・時間外割増は除外、役職手当は含む",
  ], { x: 6.5, y: 1.9, w: 2.85, h: 3.1, size: 9.5, color: C.text, bullets: true, valign: "top" });
  footer(s, n, "茨城県・つくば市公表資料（1,074円）、茨城地方最低賃金審議会答申の報道（1,136円、二次情報。茨城労働局の告示で要確認）");
  s.notes("改定後の1,136円は答申段階の二次情報。告示で確定したら差し替える。発効日以降は改定額を下回る賃金は無効で差額支払いが必要。");
}
// 7 時間外単価と有給
{
  const s = slide(); n++;
  header(s, "時間外手当の単価算式と年次有給休暇", "いずれも労働基準法の定めに合わせる必要がある");
  card(s, 0.5, 1.35, 4.4, 3.7);
  s.text("時間外手当の1時間当たり単価（案第9条2項）", { x: 0.7, y: 1.45, w: 4.1, h: 0.4, size: 12, bold: true, color: C.green, margin: 0 });
  s.chart("bar", [{ name: "単価", labels: ["案の算式\n（÷1,560時間）", "法定算式\n（÷120時間×12）"], values: [1000, 1083] }],
    { x: 0.6, y: 1.9, w: 2.3, h: 2.9, colors: [C.grey, C.green], showValue: true, fmt: "#,##0\"円\"", barDir: "col", valAxisMax: 1300 });
  s.text([
    "案：基本給×12÷（2週間の勤務時間×26）＝130,000×12÷1,560＝1,000円",
    "労基法施行規則第19条：月給÷月平均所定労働時間＝130,000÷120＝1,083円",
    "案の算式は年間休日を考慮せず、単価が約8%低い",
    "→「基本給月額÷月平均所定労働時間」に改める",
  ], { x: 3.0, y: 1.9, w: 1.85, h: 3.0, size: 9, color: C.text, bullets: true, valign: "top" });
  card(s, 5.1, 1.35, 4.4, 3.7);
  s.text("年次有給休暇（現行就業規則第6条）", { x: 5.3, y: 1.45, w: 4.1, h: 0.4, size: 12, bold: true, color: C.green, margin: 0 });
  const rows = [["勤続", "法定（週30h以上）", "現行規則"], ["6か月", "10日", "10日"], ["1年6か月", "11日", "10日"], ["2年6か月", "12日", "10日"], ["3年6か月", "14日", "10日"], ["4年6か月", "16日", "10日"], ["5年6か月", "18日", "10日"], ["6年6か月以上", "20日", "10日"]];
  s.table(rows, { x: 5.3, y: 1.9, w: 4.0, colW: [1.4, 1.5, 1.1], size: 9, hilite: 7, align: ["l", "c", "c"] });
  s.text("法定を下回る部分は無効（労基法第13条）。勤続16年の事務局長には年20日の付与が必要", { x: 5.3, y: 4.35, w: 4.0, h: 0.6, size: 9.5, color: C.red, bold: true, margin: 0 });
  footer(s, n, "労働基準法第37条・第39条、労働基準法施行規則第19条（厚生労働省「確かめよう労働条件」ほか、二次情報）");
  s.notes("時間外単価は案の算式が法定より低くなる点、有給は現行規則が法定未満である点を説明する。");
}
// 8 水準試算
{
  const s = slide(); n++;
  header(s, "基本給水準の試算（週30時間勤務）", "推奨はS3：時給1,200円相当、月額144,000円");
  const rows = [["案", "内容", "月額基本給", "時給換算", "年間人件費", "案比"]];
  scenW.forEach(([k, name, b]) => { const c = calcW(b), base = calcW(130000).annual; rows.push([k, name, yen(b) + "円", yen(Math.round(c.hourly)) + "円", yen(c.annual) + "円", (c.annual - base >= 0 ? "+" : "") + yen(c.annual - base) + "円"]); });
  s.table(rows, { x: 0.5, y: 1.35, w: 5.6, colW: [0.45, 1.65, 0.95, 0.75, 0.95, 0.85], size: 9, hilite: 3, align: ["c", "l", "r", "r", "r", "r"] });
  s.chart("bar", [{ name: "年間人件費", labels: scenW.map((x) => x[0]), values: scenW.map((x) => Math.round(calcW(x[2]).annual / 10000)) }],
    { x: 6.3, y: 1.3, w: 3.3, h: 2.6, colors: [C.grey, C.green2, C.yellow, C.green2], showValue: true, fmt: "0\"万円\"", barDir: "col", valAxisMax: 260 });
  card(s, 0.5, 3.3, 5.6, 1.75, { fill: C.tint });
  s.text([
    "年間人件費＝基本給×12＋役職手当120,000円＋賞与（基本給2か月、案の上限）。社会保険料・退職引当・福利厚生は含まない",
    "参考：令和7年度 給料手当決算 1,850,000円（一般会計支出の8.5%）",
    "S2は改定後の最低賃金の下限で、次回改定（例年10月）で再び下回る可能性が高い",
    "基本給表は「時給×月平均所定労働時間」で毎年度見直す方式にすると追随が容易",
  ], { x: 0.7, y: 3.38, w: 5.3, h: 1.65, size: 9, color: C.text, bullets: true, valign: "top" });
  footer(s, n, "令和7年度一般会計収支決算報告、職員給与規程（案）");
  s.notes("S3でも年間20万円弱の増加。B・C区分と非常勤も同じ基準時給で再計算する。");
}
// 9 退職金
{
  const s = slide(); n++;
  header(s, "退職手当の見込みと引当金の差", "現行就業規則第15条：退職時の月額給与×勤務年数");
  s.chart("bar", [
    { name: "退職手当 見込み（基本給のみ）", labels: ["2026年（勤続16年）", "2030年（勤続20年）"], values: [208, 260] },
    { name: "退職手当 見込み（役職手当込・S3）", labels: ["2026年（勤続16年）", "2030年（勤続20年）"], values: [246, 308] },
    { name: "引当金残高", labels: ["2026年（勤続16年）", "2030年（勤続20年）"], values: [165, 225] },
  ], { x: 0.4, y: 1.3, w: 5.6, h: 3.8, colors: [C.green2, C.green, C.yellow], showValue: true, fmt: "0\"万円\"", barDir: "col", valAxisMax: 350, legendPos: "b" });
  card(s, 6.3, 1.35, 3.2, 3.7, { fill: C.tint });
  s.text("対応案", { x: 6.5, y: 1.45, w: 2.8, h: 0.4, size: 13, bold: true, color: C.green, margin: 0 });
  s.text([
    "(a) 引当金の年間繰入を150,000円から25万〜30万円に引き上げる【基本】",
    "(b) 平成25年案のように「引当金の範囲内で理事会が決定」する方式に改める",
    "(c) 算定基礎を基本給に限定し、「月額給与」の範囲を明記する",
    "見込額は引当金を43万〜83万円上回る。職員の既得の期待に関わるため(a)を基本に",
  ], { x: 6.5, y: 1.9, w: 2.85, h: 3.1, size: 9.5, color: C.text, bullets: true, valign: "top" });
  footer(s, n, "財産目録（退職給与積立 1,650,000円、令和8年3月31日）、令和7年度決算（引当繰入150,000円）、役職員名簿（就任 平成22年9月26日）");
  s.notes("引当金は年15万円の積立で2030年に225万円。見込額との差を埋めるには繰入増額が最も単純。");
}
// 10 その他の確認事項
{
  const s = slide(); n++;
  header(s, "そのほか確認が必要な事項", "事務局・社会保険労務士で確認のうえ理事会へ");
  const items = [
    ["社会保険の適用", "法人は健康保険・厚生年金の強制適用。週30時間勤務は原則被保険者（70歳以上は厚生年金対象外）。令和7年度福利厚生費36,141円からは事業主負担（年約25万円規模）が見えない。適用状況と職員の年齢を確認"],
    ["現行の支給実額", "給料手当1,850,000円の内訳（基本給・手当・期末手当）は理事会資料に記載なし。案の金額が現行を下回る場合は不利益変更（労働契約法第9条・第10条）となり職員の同意が必要"],
    ["通勤手当の非課税限度額", "自家用車は片道距離に応じ月額4,200〜66,400円が非課税（2026年4月改正）。案の「1kmにつき15円」は期間の単位が不明。「片道×2×出勤日数×15円」等に明確化"],
    ["手当の要否", "平成25年案にあった扶養手当・資格手当・慶弔金は今回の案にない。設けるかを決定"],
    ["年間所定労働日数", "本資料は240日と仮定（2026年の平日261日−祝日17日−年末年始の平日4日）。保護観察所の閉庁日を含め事務局で確定"],
    ["規程案の誤記", "第11条が2つ（賞与・改訂）、「別紙」「別表」の混在、第3条2項の句読点、第8条(1)の文言、附則の施行日空欄"],
  ];
  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.65, y = 1.3 + row * 1.25;
    card(s, x, y, 4.4, 1.12);
    s.circle({ x: x + 0.15, y: y + 0.15, w: 0.32, h: 0.32, fill: C.yellow });
    s.text(String(i + 1), { x: x + 0.15, y: y + 0.15, w: 0.32, h: 0.32, size: 11, bold: true, color: C.green, align: "center", valign: "middle", margin: 0 });
    s.text(it[0], { x: x + 0.6, y: y + 0.1, w: 3.6, h: 0.38, size: 11, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(it[1], { x: x + 0.6, y: y + 0.47, w: 3.7, h: 0.63, size: 8, color: C.text, valign: "top", margin: 0 });
  });
  footer(s, n, "社会保険加入要件・通勤手当非課税限度額はいずれも二次情報（一次情報：日本年金機構、国税庁）");
  s.notes("社会保険は職員の年齢によって扱いが変わるため、断定せず確認事項として扱う。");
}
// 11 修正提案
{
  const s = slide(); n++;
  header(s, "給与規程（案）・就業規則の修正提案", "案9件、就業規則4件");
  const rows = [["条項", "現行の記載", "修正案"],
    ["案 別表 基本給", "A 130,000円ほか（時給約1,080〜1,100円）", "基準時給1,136円以上（推奨1,200円）×月平均所定労働時間。毎年度見直し"],
    ["案 第9条2項", "基本給×12÷（2週間の勤務時間×26）", "基本給月額÷月平均所定労働時間（年間所定労働時間÷12）"],
    ["案 第11条（2か所）", "賞与と規程の改訂が同じ条番号", "改訂を第12条に繰り下げ"],
    ["案 第4条／第7条", "「別紙」と「別表」が混在", "「別表」に統一"],
    ["案 第3条2項", "「ただし。役職手当については」", "「ただし、役職手当については」"],
    ["案 第8条(1)", "「定期券で算出された金額のいずれか低い実費」", "「定期券の額又は実費のいずれか低い額」"],
    ["案 第8条(2)", "通勤距離1kmにつき15円（期間の単位が不明）", "片道距離×2×出勤日数×15円（月額）。非課税限度額の範囲内"],
    ["案 第2条3項", "「就業規則第7条第1項に基づき付加給付」", "付加できる手当の種類を列挙"],
    ["案 附則", "施行日が空欄", "2027年1月の理事会承認日（最低賃金対応部分は2026年10月18日に遡及）"],
    ["就業規則 第6条", "年次有給休暇 年間10日", "労基法第39条の付与日数表（6年6か月以上20日）"],
    ["就業規則 第9条", "通勤手当は実費", "給与規程第8条による"],
    ["就業規則 第11条", "期末手当", "「賞与」に用語統一"],
    ["就業規則 第15条", "退職時の月額給与×勤務年数", "「月額給与」の範囲を明記し、引当金との関係を規定"]];
  s.table(rows, { x: 0.5, y: 1.3, w: 9.0, colW: [1.7, 3.3, 4.0], size: 8.5, align: ["l", "l", "l"] });
  footer(s, n, "職員給与規程（案）、現行職員就業規則");
  s.notes("誤記は理事会付議前に原案者と事務局で修正する。");
}
// 12 スケジュール
{
  const s = slide(); n++;
  header(s, "手続きとスケジュール（案）", "理事会は2027年1月。最低賃金の発効（10月18日）が先に来るため暫定措置が必要");
  const steps = [
    ["9月17/18日", "検討会", "基準時給、退職金の扱い、就業規則の同時改正の方針を決定"],
    ["9〜10月", "実態確認", "支給実額、社会保険、所定労働日数。職員へ説明・同意"],
    ["10月18日", "最低賃金発効", "理事長決定で暫定的に1,136円以上を支給（就業規則第7条2項）。差額は遡及"],
    ["11〜12月", "改正案確定", "社労士の確認、理事会資料の作成"],
    ["2027年1月", "理事会", "給与規程・就業規則改正を承認。暫定措置を追認"],
    ["2027年2月", "昇給決定", "給与規程第6条の初回昇給、4月支給分から"],
  ];
  steps.forEach((st, i) => {
    const x = 0.5 + i * 1.5;
    s.rect({ x, y: 1.5, w: 1.4, h: 0.95, fill: i === 0 ? C.yellow : (i === 2 ? C.red : C.green), radius: 0.08 });
    s.text(st[0], { x, y: 1.52, w: 1.4, h: 0.4, size: 10, bold: true, color: i === 0 ? C.green : "F2F2F2", align: "center", margin: 0 });
    s.text(st[1], { x, y: 1.9, w: 1.4, h: 0.5, size: 12, bold: true, color: i === 0 ? C.green : C.white, align: "center", margin: 0 });
    s.text(st[2], { x, y: 2.55, w: 1.4, h: 1.4, size: 9, color: C.text, align: "left", valign: "top" });
  });
  card(s, 0.5, 4.05, 9.0, 0.95, { fill: C.tint });
  s.text([
    "職員10人未満のため就業規則の労基署への届出義務はないが、給与規程は就業規則の一部であり、現行を下回る変更には職員の同意が必要（労働契約法第9条・第10条）",
    "現行就業規則第17条・給与規程案第11条により、改正は理事会の議決事項",
  ], { x: 0.7, y: 4.12, w: 8.6, h: 0.85, size: 9.5, color: C.text, bullets: true, valign: "top" });
  footer(s, n);
  s.notes("理事会は2027年1月で最低賃金の発効より後。発効日以降は規程の有無にかかわらず改定額での支払いが必要なので、理事長決定で暫定的に引き上げ、1月の理事会で追認する。");
}
// 13 決めていただきたいこと
{
  const s = slide(); n++;
  header(s, "本日、決めていただきたいこと", "7項目");
  const q = [
    "基本給表の基準時給を1,136円（S2）とするか、1,200円（S3）またはそれ以上とするか",
    "基本給表を「時給×月平均所定労働時間」で毎年度見直す方式に改めるか",
    "時間外手当の単価算式を法定算式に改めることの承認",
    "就業規則（有給休暇、通勤手当、期末手当の用語、退職手当の算定基礎）を同時に改正するか",
    "退職手当と引当金の差への対応（繰入増額／理事会決定方式／算定基礎の限定）",
    "扶養手当・資格手当・慶弔金（平成25年案にあり）を設けるか",
    "社会保険労務士への確認依頼の要否と、理事会付議の時期",
  ];
  q.forEach((t, i) => {
    const col = i < 4 ? 0 : 1, row = i < 4 ? i : i - 4;
    const x = 0.5 + col * 4.65, y = 1.35 + row * 0.92;
    s.rect({ x, y, w: 4.4, h: 0.8, fill: C.white, radius: 0.08, line: C.line });
    s.rect({ x: x + 0.15, y: y + 0.22, w: 0.36, h: 0.36, fill: C.white, line: C.green, radius: 0.04 });
    s.text(String(i + 1) + ". " + t, { x: x + 0.62, y: y + 0.05, w: 3.7, h: 0.7, size: 10.5, color: C.text, valign: "middle", margin: 0 });
  });
  footer(s, n);
  s.notes("決定事項は事務局で議事録に残す。");
}
// 14 留意事項
{
  const s = slide(); n++;
  header(s, "留意事項：本資料作成時点で確認できていないこと", "推測で埋めていない項目");
  const items = [
    ["規程案の作成者・位置づけ", "作成者・作成日の記載がなく、9月の検討会の議題に含まれるかも未確認。理事会は2027年1月予定（日付未確認）"],
    ["現行の支給実額", "給料手当1,850,000円の内訳（基本給・手当・期末手当）は理事会資料に記載なし"],
    ["社会保険の適用と職員の年齢", "健康保険・厚生年金の加入状況。年齢により厚生年金の対象外となる"],
    ["最低賃金1,136円は二次情報", "審議会答申の報道に基づく。茨城労働局の告示で金額・発効日を確認。労基法等の条文も一次情報サイトに接続できず"],
    ["年間所定労働日数", "240日と仮定。保護観察所の閉庁日を含め事務局で確定"],
    ["退職手当の解釈と他県水準", "「月額給与」に役職手当を含むか、過去の支給実績。他県協会の職員給与は入手できていない"],
  ];
  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.65, y = 1.35 + row * 1.22;
    card(s, x, y, 4.4, 1.08);
    s.circle({ x: x + 0.15, y: y + 0.15, w: 0.32, h: 0.32, fill: C.red });
    s.text("!", { x: x + 0.15, y: y + 0.15, w: 0.32, h: 0.32, size: 12, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.text(it[0], { x: x + 0.6, y: y + 0.1, w: 3.6, h: 0.4, size: 11.5, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(it[1], { x: x + 0.6, y: y + 0.48, w: 3.65, h: 0.58, size: 9, color: C.text, valign: "top", margin: 0 });
  });
  footer(s, n);
  s.notes("特に最低賃金の改定額は告示で確定次第差し替える。");
}
// 15 出典
{
  const s = slide(); n++;
  header(s, "出典一覧", "");
  const rows = [["資料", "日付", "所在"],
    ["職員給与規程（案）・現行職員就業規則", "案：作成日記載なし（Box保存 2026年8月22日）／規則：平成26年6月1日施行", "Box「0.鈴木孝昌／(更生保護協会)」20260822_更生保護法人茨城県更生保護協会職員給与規程.pdf"],
    ["事務局「書類送付ご案内」、平成25年就業規則（案）・給与細則（案）・退職慰労金支給細則（案）", "令和8年7月23日", "Box「0.鈴木孝昌／(更生保護協会)」20260723_書類送付ご案内.pdf"],
    ["理事会議事録（第4号議案 就業規則（案））", "平成25年5月8日", "Box「0.鈴木孝昌／(更生保護協会)」20130508_理事会議事録（就業規則案・基本財産変更）.pdf"],
    ["令和8年度理事会資料（令和7年度決算、財産目録、役職員名簿）", "令和8年5月13日", "Box「0.鈴木孝昌／(更生保護協会)」202605_更生保護法人茨城県更生保護協会.pdf"],
    ["茨城県最低賃金 1,074円", "2025年10月12日発効", "茨城県、つくば市、小美玉市の公表資料（二次情報）"],
    ["茨城県最低賃金 1,136円答申、発効予定2026年10月18日", "答申 2026年8月24日", "ゼロプラス、STRIDE、ろうどうDB（二次情報）。一次情報：茨城労働局"],
    ["年次有給休暇の付与日数（労基法第39条）", "―", "厚生労働省「確かめよう労働条件」、連合 労働相談Q&A"],
    ["社会保険の加入要件", "―", "弥生、社労士ナビ、連合（二次情報）。一次情報：日本年金機構"],
    ["通勤手当の非課税限度額（2026年4月改正）", "2026年4月1日施行", "OBC、電通総研、ラクラス（二次情報）。一次情報：国税庁"]];
  s.table(rows, { x: 0.5, y: 1.1, w: 9.0, colW: [3.4, 2.2, 3.4], size: 8, align: ["l", "l", "l"] });
  footer(s, n);
  s.notes("");
}

// ================= pptxgenjs 描画 =================
function toPptx() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "鈴木孝昌"; pres.title = "茨城県更生保護協会 職員給与規程（案）等の検討 説明資料（案）";
  const alignMap = { l: "left", r: "right", c: "center" };
  slides.forEach((sp) => {
    const sl = pres.addSlide();
    sl.background = { color: sp.bg };
    sp.els.forEach((e) => {
      if (e.k === "rect") {
        sl.addShape(e.radius ? pres.ShapeType.roundRect : pres.ShapeType.rect, { x: e.x, y: e.y, w: e.w, h: e.h, fill: { color: e.fill }, line: e.line ? { color: e.line, width: 0.75 } : { color: e.fill, width: 0 }, rectRadius: e.radius || 0 });
      } else if (e.k === "circle") {
        sl.addShape(pres.ShapeType.ellipse, { x: e.x, y: e.y, w: e.w, h: e.h, fill: { color: e.fill }, line: { color: e.fill, width: 0 } });
      } else if (e.k === "line") {
        sl.addShape(pres.ShapeType.line, { x: e.x, y: e.y, w: e.w, h: e.h, line: { color: e.color, width: e.width || 1 } });
      } else if (e.k === "image") {
        sl.addImage({ data: "image/png;base64," + LOGO[e.src], x: e.x, y: e.y, w: e.w, h: e.h });
      } else if (e.k === "text") {
        const common = { x: e.x, y: e.y, w: e.w, h: e.h, fontFace: FONT, fontSize: e.size || 12, color: e.color || C.text, bold: !!e.bold, align: e.align || "left", valign: e.valign || "top", isTextBox: true, margin: e.margin === 0 ? 0 : 0.05, fit: "shrink" };
        if (Array.isArray(e.t)) {
          const items = e.t.map((t, i) => ({ text: t, options: { bullet: e.numbered ? { type: "number" } : e.bullets ? true : false, breakLine: i < e.t.length - 1, paraSpaceAfter: 4 } }));
          sl.addText(items, common);
        } else sl.addText(e.t, common);
      } else if (e.k === "table") {
        const rows = e.rows.map((r, ri) => r.map((c, ci) => ({ text: String(c), options: {
          fontFace: FONT, fontSize: e.size || 10, bold: ri === 0 || ri === e.hilite, color: ri === 0 ? C.white : C.text,
          fill: { color: ri === 0 ? C.green : (ri === e.hilite ? "FBEFC4" : (ri % 2 === 0 ? C.tint2 : C.white)) },
          align: ri === 0 ? "center" : (alignMap[(e.align || [])[ci]] || "left"), valign: "middle", margin: 0.03,
        } })));
        sl.addTable(rows, { x: e.x, y: e.y, w: e.w, colW: e.colW, border: { type: "solid", color: C.line, pt: 0.5 }, rowH: 0.26 });
      } else if (e.k === "chart") {
        const base = { x: e.x, y: e.y, w: e.w, h: e.h, chartColors: e.colors, showLegend: !!e.legendPos, legendPos: e.legendPos || "b", legendFontFace: FONT, legendFontSize: 10,
          catAxisLabelFontFace: FONT, catAxisLabelFontSize: 9, catAxisLabelColor: C.muted, valAxisLabelFontFace: FONT, valAxisLabelFontSize: 9, valAxisLabelColor: C.muted,
          dataLabelFontFace: FONT, dataLabelFontSize: 9, dataLabelColor: C.text, valGridLine: { color: "E3E8E5", size: 0.5 }, catGridLine: { style: "none" } };
        if (e.type === "doughnut") {
          sl.addChart(pres.ChartType.doughnut, e.data, { ...base, holeSize: e.holeSize || 55, showPercent: true, showValue: false, showLabel: false, showLegend: true, legendPos: "b", dataLabelFontSize: 12, dataLabelColor: C.white, dataLabelFormatCode: "0.0%" });
        } else {
          sl.addChart(pres.ChartType.bar, e.data, { ...base, barDir: e.barDir || "col", barGrouping: e.stacked ? "stacked" : "clustered", showValue: !!e.showValue,
            dataLabelPosition: e.stacked ? "ctr" : "outEnd", dataLabelFormatCode: e.fmt || "0", valAxisMinVal: 0, valAxisMaxVal: e.valAxisMax, valAxisLabelFormatCode: e.fmt && !e.stacked ? e.fmt : "#,##0",
            showValAxisTitle: !!e.valTitle, valAxisTitle: e.valTitle, valAxisTitleFontFace: FONT, valAxisTitleFontSize: 9, valAxisTitleColor: C.muted, barGapWidthPct: 60 });
        }
      }
    });
    if (sp.notes) sl.addNotes(sp.notes);
  });
  return pres.writeFile({ fileName: OUT });
}

// ================= HTML プレビュー描画（確認用。96px = 1インチ） =================
function toHtml() {
  const px = (v) => (v * 96).toFixed(1) + "px";
  const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  let html = `<!doctype html><html lang="ja"><meta charset="utf-8"><style>
  body{background:#ddd;font-family:"IPAPGothic","IPAGothic",sans-serif;margin:0;padding:0}
  .s{position:relative;width:960px;height:540px;margin:0 auto 0;overflow:hidden;background:#fff}
  .e{position:absolute;box-sizing:border-box;overflow:hidden}
  .t{padding:4.8px;line-height:1.35;white-space:pre-wrap;word-break:break-all}
  .t.m0{padding:0}
  .t.mid{display:flex;flex-direction:column;justify-content:center}
  .t.bot{display:flex;flex-direction:column;justify-content:flex-end}
  ul,ol{margin:0;padding-left:1.2em} li{margin-bottom:4px}
  table{border-collapse:collapse;width:100%;table-layout:fixed} td{border:1px solid #CBD5CF;padding:1px 3px;line-height:1.25;overflow:hidden}
  .chart{border:1px dashed #9AA5A0;display:flex;align-items:flex-end;gap:6px;padding:20px 24px 28px;background:#fafafa}
  .bar{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;font-size:9px;height:100%}
  .bar div{width:60%}
  </style><body>`;
  slides.forEach((sp, i) => {
    html += `<div class="s" id="s${i}" style="background:#${sp.bg}">`;
    sp.els.forEach((e) => {
      const pos = `left:${px(e.x)};top:${px(e.y)};width:${px(e.w)};height:${px(e.h)};`;
      if (e.k === "rect") html += `<div class="e" style="${pos}background:#${e.fill};border-radius:${px(e.radius || 0)};${e.line ? "border:1px solid #" + e.line : ""}"></div>`;
      else if (e.k === "circle") html += `<div class="e" style="${pos}background:#${e.fill};border-radius:50%"></div>`;
      else if (e.k === "line") html += `<div class="e" style="${pos}border-top:${e.width || 1}px solid #${e.color}"></div>`;
      else if (e.k === "image") html += `<img class="e" src="data:image/png;base64,${LOGO[e.src]}" style="${pos}">`;
      else if (e.k === "text") {
        const st = `${pos}font-size:${((e.size || 12) * 96 / 72).toFixed(1)}px;color:#${e.color || C.text};font-weight:${e.bold ? 700 : 400};text-align:${e.align || "left"};`;
        const cls = "e t" + (e.margin === 0 ? " m0" : "") + (e.valign === "middle" ? " mid" : e.valign === "bottom" ? " bot" : "");
        let inner = Array.isArray(e.t) ? `<${e.numbered ? "ol" : "ul"}>${e.t.map((x) => `<li>${esc(x)}</li>`).join("")}</${e.numbered ? "ol" : "ul"}>` : esc(e.t);
        html += `<div class="${cls}" style="${st}">${inner}</div>`;
      } else if (e.k === "table") {
        const fs = ((e.size || 10) * 96 / 72).toFixed(1);
        html += `<div class="e" style="${pos.replace(/height:[^;]+;/, "")}"><table style="font-size:${fs}px"><colgroup>${e.colW.map((w) => `<col style="width:${px(w)}">`).join("")}</colgroup>`;
        e.rows.forEach((r, ri) => { html += `<tr style="height:${px(0.26)};background:${ri === 0 ? "#" + C.green : ri === e.hilite ? "#FBEFC4" : ri % 2 === 0 ? "#" + C.tint2 : "#fff"};color:${ri === 0 ? "#fff" : "#222"};font-weight:${ri === 0 || ri === e.hilite ? 700 : 400}">${r.map((c, ci) => `<td style="text-align:${ri === 0 ? "center" : ({ l: "left", r: "right", c: "center" })[(e.align || [])[ci]] || "left"}">${esc(c)}</td>`).join("")}</tr>`; });
        html += `</table></div>`;
      } else if (e.k === "chart") {
        if (e.type === "doughnut") {
          const v = e.data[0].values, tot = v.reduce((a, b) => a + b, 0), p1 = v[0] / tot * 100;
          html += `<div class="e" style="${pos}display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px dashed #9AA5A0"><div style="width:220px;height:220px;border-radius:50%;background:conic-gradient(#${e.colors[0]} 0 ${p1}%,#${e.colors[1]} ${p1}% 100%);position:relative"><div style="position:absolute;inset:50px;border-radius:50%;background:#fff"></div></div><div style="font-size:11px;margin-top:8px">${e.data[0].labels.map((l, j) => `<span style="color:#${e.colors[j]}">■</span> ${esc(l)} ${(v[j] / tot * 100).toFixed(1)}%`).join("　")}</div></div>`;
        } else {
          const max = e.valAxisMax || Math.max(...e.data.flatMap((d) => d.values)) * 1.1;
          const labels = e.data[0].labels;
          html += `<div class="e chart" style="${pos}">` + labels.map((l, j) => {
            const stack = e.data.map((d, di) => `<div style="height:${(d.values[j] / max * 100).toFixed(1)}%;background:#${(e.colors[e.stacked ? di : j] || e.colors[0])}"></div>`).join("");
            const val = e.data.map((d) => d.values[j]).reduce((a, b) => a + b, 0);
            return `<div class="bar"><span>${e.showValue ? val : ""}</span>${stack}<span style="height:26px;text-align:center;font-size:8.5px">${esc(l)}</span></div>`;
          }).join("") + `</div>`;
        }
      }
    });
    html += `<div style="position:absolute;left:4px;top:4px;font-size:10px;color:#999">slide ${i + 1}</div></div>`;
  });
  fs.writeFileSync(HTML, html + "</body></html>");
}

toHtml();
toPptx().then(() => console.log("written", OUT, "slides:", slides.length));
