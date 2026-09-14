// 茨城県更生保護協会 基本財産運用検討会 説明資料（PowerPoint）生成
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

let n = 0;
// ===== 1. 表紙 =====
{
  const s = slide({ bg: C.green }); n++;
  s.circle({ x: 7.6, y: -0.9, w: 3.4, h: 3.4, fill: C.green2 });
  s.circle({ x: 8.35, y: -0.15, w: 1.9, h: 1.9, fill: C.yellow });
  s.image({ src: "w", x: 0.6, y: 0.45, w: 0.8, h: 0.94 });
  s.text("更生保護法人 茨城県更生保護協会", { x: 0.6, y: 1.5, w: 8, h: 0.5, size: 18, color: "CFE3D8" });
  s.text("基本財産運用 検討会", { x: 0.6, y: 2.0, w: 8.5, h: 0.8, size: 40, bold: true, color: C.white });
  s.text("説明資料（案）", { x: 0.6, y: 2.75, w: 8.5, h: 0.7, size: 30, bold: true, color: C.yellow });
  s.text("令和8年（2026年）9月17日（木）又は18日（金） 11:30〜　於：景山", { x: 0.6, y: 3.75, w: 8.5, h: 0.4, size: 14, color: C.white });
  s.text("※開催日は事務局メールの曜日表記と日付が一致しないため要確認", { x: 0.6, y: 4.1, w: 8.5, h: 0.3, size: 10, color: "CFE3D8" });
  s.text("作成：理事 鈴木 孝昌　2026年9月12日（9月14日改訂：理事会 2027年1月予定）", { x: 0.6, y: 4.7, w: 8.5, h: 0.35, size: 12, color: "CFE3D8" });
  s.notes("本日は、基本財産1億7,500万円の運用方針について、規程案の承認と配分目標の決定をお願いしたい。数値は令和8年3月31日現在の財産目録に基づく。");
}
// ===== 2. 本日のゴール =====
{
  const s = slide(); n++;
  header(s, "本日のゴール", "検討会で決めていただきたいことは3点です");
  const items = [
    ["規程案の承認", "梶副理事長作成の「資金運用基本方針（案）」「資金運用ガイドライン（案）」（2026年8月19日付）を誤記修正のうえ理事会に付議する"],
    ["配分目標の決定", "基本財産のうち国債等の比率を「約84%」（定期預金 約16%）とする。ガイドライン案の目安70〜90%の範囲内"],
    ["移行方法の決定", "2027年1月の理事会承認後、満期を迎える定期から順次国債へ振り替える。2027年3月末に80.3%、常陽2年定期600万円の振替で83.8%"],
  ];
  items.forEach((it, i) => {
    const x = 0.5 + i * 3.1;
    card(s, x, 1.45, 2.9, 3.4);
    numBadge(s, x + 0.25, 1.7, i + 1);
    s.text(it[0], { x: x + 0.8, y: 1.68, w: 2.0, h: 0.45, size: 16, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(it[1], { x: x + 0.25, y: 2.35, w: 2.4, h: 2.3, size: 12, color: C.text, valign: "top" });
  });
  footer(s, n);
  s.notes("決めていただきたいのは、規程案の承認、配分目標、移行方法の3点。細かい諮問事項は最後のスライドにまとめている。");
}
// ===== 3. 結論（提案の全体像） =====
{
  const s = slide(); n++;
  header(s, "結論：6つの提案", "安全性・流動性・収益性の順で、定期預金の一部を国債へ");
  const props = [
    ["規程案を承認", "基本方針（案）・ガイドライン（案）を誤記修正のうえ理事会へ"],
    ["国債等 約84%", "定期は約16%（2,842万円）を流動性・再投資余力として保持"],
    ["満期ごとに振替", "理事会承認後、満期到来分から順次国債へ（2027年3月末に80%、600万円の振替で約84%）"],
    ["償還年限を分散", "2030年に約6割が償還する集中を、2年・5年・10年で段階的に是正"],
    ["複数機関で比較", "野村證券・常陽銀行・県信・めぶき証券から条件提示、選定記録を保存"],
    ["手続きを確認", "理事会・評議員会の議決後、必要なら関東地方更生保護委員会へ定款変更認可申請"],
  ];
  props.forEach((pr, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.5 + col * 3.1, y = 1.4 + row * 1.85;
    card(s, x, y, 2.9, 1.65);
    numBadge(s, x + 0.2, y + 0.2, i + 1);
    s.text(pr[0], { x: x + 0.72, y: y + 0.17, w: 2.1, h: 0.48, size: 15, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(pr[1], { x: x + 0.2, y: y + 0.75, w: 2.55, h: 0.85, size: 10.5, color: C.text, valign: "top" });
  });
  footer(s, n);
  s.notes("提案の全体像。1と2と3が本日の決定事項、4〜6は実務の進め方。");
}
// ===== 4. 現状① 基本財産の構成 =====
{
  const s = slide(); n++;
  header(s, "現状①　基本財産 1億7,500万円の構成", "国債 68.4%／定期預金 31.6%（令和8年3月31日現在）");
  s.chart("doughnut", [{ name: "構成", labels: ["国債 1億1,975万円", "定期預金 5,525万円"], values: [119750000, 55250000] }],
    { x: 0.4, y: 1.3, w: 4.4, h: 3.8, colors: [C.green, C.yellow], showPercent: true, legendPos: "b", holeSize: 55 });
  const stats = [["175,000,000円", "基本財産 合計"], ["0.87%", "現在の平均利回り（国債1.14%、定期0.28%）"], ["834,889円", "令和7年度 財産収入（利息利金等）実績"], ["1,519,350円", "現行構成での年間利息見込み（税引前）"]];
  stats.forEach((st, i) => {
    const y = 1.35 + i * 0.95;
    card(s, 5.1, y, 4.4, 0.82);
    s.text(st[0], { x: 5.3, y: y + 0.05, w: 2.2, h: 0.72, size: 18, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(st[1], { x: 7.45, y: y + 0.05, w: 2.0, h: 0.72, size: 9.5, color: C.muted, valign: "middle", margin: 0 });
  });
  footer(s, n, "令和8年度理事会資料 財産目録・財産目録別紙（令和8年3月31日現在）、令和7年度一般会計収支決算報告");
  s.notes("基本財産は国債1億1,975万円と定期預金5,525万円。令和7年度に定期4,000万円を国債に振り替え済み。平均利回りは0.87%だが、定期部分は0.28%にとどまる。");
}
// ===== 5. 現状② 利率の差 =====
{
  const s = slide(); n++;
  header(s, "現状②　定期預金と国債の利率差", "2026年9月時点で、国債利回りは定期預金の約5〜10倍");
  s.chart("bar", [{ name: "利率", labels: ["定期預金（保有分平均）", "国債（保有分平均）", "新規 2年国債", "新規 5年国債", "新規 10年国債"], values: [0.28, 1.14, 1.82, 2.22, 2.98] }],
    { x: 0.4, y: 1.3, w: 5.6, h: 3.8, colors: [C.grey, C.green2, C.yellow, C.yellow, C.yellow], valAxisMax: 3.5, fmt: "0.00\"%\"", showValue: true, barDir: "col" });
  card(s, 6.3, 1.35, 3.2, 3.7, { fill: C.tint });
  s.text("読み取り", { x: 6.5, y: 1.45, w: 2.8, h: 0.4, size: 13, bold: true, color: C.green, margin: 0 });
  s.text([
    "保有中の定期5,525万円は年0.28%。年間利息は約15万円",
    "同額を5年国債（2.22%）に置くと年間約123万円",
    "日銀の政策金利は2026年6月に1.0%へ。定期の店頭金利（常陽銀行スーパー定期0.35〜0.50%）も上昇しているが、国債との差は大きい",
    "定期の中途解約利率は多くの銀行で「普通預金利率」が下限。常陽銀行の普通預金が0.3%なら、0.275%の定期を解約しても不利益はほぼない可能性（要確認）",
  ], { x: 6.5, y: 1.9, w: 2.85, h: 3.1, size: 9.5, color: C.text, bullets: true, valign: "top" });
  footer(s, n, "国債利回りは2026年9月10日時点（stock-marketdata.com、二次情報）。政策金利・預金金利も二次情報。会議前に財務省・日銀・各行の一次情報で再確認");
  s.notes("グラフの左2本が現在の保有分、右3本が新規に買った場合の利回り。金利数値は二次情報なので、当日までに一次情報で再確認する。");
}
// ===== 6. 現状③ 償還の集中 =====
{
  const s = slide(); n++;
  header(s, "現状③　償還・満期が2030年に集中", "基本財産の60%（1億548万円）が同じ年に償還を迎える");
  s.chart("bar", [
    { name: "国債 償還", labels: ["2026年", "2027年", "2028〜29年", "2030年"], values: [0, 2000, 0, 9975] },
    { name: "定期 満期", labels: ["2026年", "2027年", "2028〜29年", "2030年"], values: [600, 4352, 0, 573] },
  ], { x: 0.4, y: 1.3, w: 5.6, h: 3.8, colors: [C.green, C.yellow], stacked: true, showValue: false, barDir: "col", valTitle: "万円", legendPos: "b" });
  card(s, 6.3, 1.35, 3.2, 3.7, { fill: C.tint });
  s.text("課題", { x: 6.5, y: 1.45, w: 2.8, h: 0.4, size: 13, bold: true, color: C.green, margin: 0 });
  s.text([
    "2030年に国債9,975万円＋定期573万円が償還・満期",
    "その時点の金利水準に基本財産の6割が一度に左右される",
    "ガイドライン（案）第4条は「特定の年度・年限に満期が集中することを避ける」と規定",
    "2028〜2029年は償還がゼロで、再投資の機会もない",
    "→ 今後の購入分は2年・5年・10年に分散（スライド11）",
  ], { x: 6.5, y: 1.9, w: 2.85, h: 3.1, size: 10, color: C.text, bullets: true, valign: "top" });
  footer(s, n, "財産目録別紙（令和8年3月31日現在）。2027年の定期には自動継続後の満期（2027.5.22 2,119万円、2027.8.7 150万円）を含む");
  s.notes("令和7年度に購入した国債3本がいずれも2030年償還のため、集中が生じている。今後の購入で年限を分散する。");
}
// ===== 7. 制度上の確認と他県事例 =====
{
  const s = slide(); n++;
  header(s, "制度上の確認と他県の事例", "関東地方更生保護委員会「許容割合の定めはない」「100%国債の前例あり」");
  card(s, 0.5, 1.35, 4.6, 3.7, { fill: C.tint });
  s.text("関東地方更生保護委員会の回答（要旨）", { x: 0.7, y: 1.45, w: 4.2, h: 0.4, size: 12, bold: true, color: C.green, margin: 0 });
  s.text([
    "許容される割合はどこにも示されていない",
    "定期預金より国債の利率が良いというだけでなく、中途解約利率・解約手数料・違約金を加味しても切り替えのメリットが高いか判断が必要",
    "基本財産を100%国債に切り替えて定款変更許可申請をした法人もある",
    "申請の際は、変更理由欄に上記の比較を盛り込むこと",
  ], { x: 0.7, y: 1.9, w: 4.25, h: 3.05, size: 10.5, color: C.text, bullets: true, valign: "top" });
  s.text("他県協会の基本財産に占める国債比率", { x: 5.4, y: 1.4, w: 4.1, h: 0.4, size: 12, bold: true, color: C.green, margin: 0 });
  s.chart("bar", [{ name: "国債比率", labels: ["栃木県協会", "群馬県協会", "茨城県協会（現状）", "茨城県協会（提案）"], values: [100, 83.3, 68.4, 83.8] }],
    { x: 5.3, y: 1.8, w: 4.3, h: 3.2, colors: [C.grey, C.grey, C.green2, C.yellow], valAxisMax: 100, fmt: "0.0\"%\"", showValue: true, barDir: "bar" });
  footer(s, n, "関東地方更生保護委員会からの回答（2026年8月、事務局メール添付）。栃木・群馬は事務局が栃木県協会事務局長に聞き取り（群馬：国債1億円・定期2千万円）");
  s.notes("制度上の上限はない。栃木は100%国債、群馬は国債1億・定期2千万。茨城の提案84%は群馬とほぼ同水準。");
}
// ===== 8. 規程案の要点 =====
{
  const s = slide(); n++;
  header(s, "資金運用基本方針（案）・ガイドライン（案）の要点", "梶副理事長作成、2026年8月19日付");
  const pts = [
    ["優先順位", "安全性 → 流動性 → 収益性。物価上昇による実質価値の低下にも留意"],
    ["運用対象", "基本財産は国債・地方債・政府保証債・定期預金・理事会が安全と認めた商品"],
    ["配分の目安", "国債等 70〜90%、定期預金等 10〜30%。毎年度見直し"],
    ["満期管理", "年限を分散し、満期時に同一商品へ機械的に継続しない。原則満期保有"],
    ["禁止取引", "信用取引・デリバティブ・FX・暗号資産・個別株の短期売買など"],
    ["選定と報告", "複数の金融機関から条件提示を受け記録を保存。毎年度、理事会へ運用状況を報告"],
  ];
  pts.forEach((pt, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.65, y = 1.35 + row * 1.25;
    s.circle({ x, y: y + 0.12, w: 0.5, h: 0.5, fill: C.yellow });
    s.text(String(i + 1), { x, y: y + 0.12, w: 0.5, h: 0.5, size: 14, bold: true, color: C.green, align: "center", valign: "middle", margin: 0 });
    s.text(pt[0], { x: x + 0.65, y, w: 3.8, h: 0.4, size: 13, bold: true, color: C.green, margin: 0, valign: "middle" });
    s.text(pt[1], { x: x + 0.65, y: y + 0.42, w: 3.85, h: 0.75, size: 10.5, color: C.text, margin: 0, valign: "top" });
  });
  footer(s, n, "【更生保護協会】資金運用基本方針.docx／資金運用ガイドライン.docx（Box「資産運用委員会」フォルダ）。誤記の修正案は付録2");
  s.notes("規程案の骨子。配分の目安70〜90%が本日の配分目標の枠になる。誤記12件の修正案は付録2に一覧化した。");
}
// ===== 9. 配分案の比較 =====
{
  const s = slide(); n++;
  header(s, "配分案の比較（A〜F）", "推奨はD案：満期到来分を順次振り替え、国債等 約84%");
  const rows = [["案", "国債等比率", "国債等（万円）", "定期（万円）", "年間利息見込み", "現状との差"]];
  options.forEach(([k, name, o]) => rows.push([k + "　" + name, pct(o.ratio), yen(o.jgb / 10000), yen(o.dep / 10000), yen(Math.round(o.inc)) + "円", (o.inc - options[0][2].inc >= 0 ? "+" : "") + yen(Math.round(o.inc - options[0][2].inc)) + "円"]));
  s.table(rows, { x: 0.5, y: 1.35, w: 5.7, colW: [1.5, 0.75, 0.8, 0.7, 1.05, 0.9], size: 9, hilite: 4, align: ["l", "r", "r", "r", "r", "r"] });
  s.chart("bar", [{ name: "年間利息", labels: options.map((o) => o[0]), values: options.map((o) => Math.round(o[2].inc / 10000)) }],
    { x: 6.3, y: 1.3, w: 3.3, h: 3.0, colors: options.map((o) => (o[0] === "D" ? C.yellow : C.green2)), showValue: true, fmt: "0\"万円\"", barDir: "col", valAxisMax: 300 });
  s.text("試算前提：新規国債 2.2%、定期 0.3%、既存国債は現行クーポン。2027年償還の国債2,000万円（0.7%・0.1%）を2.2%で再投資すると、さらに年約36万円の増収。A・Fはガイドライン案の目安（70〜90%）の範囲外", { x: 0.5, y: 4.35, w: 9.0, h: 0.7, size: 9, color: C.muted });
  footer(s, n);
  s.notes("D案は年間利息が現状比で約51万円増。F案（100%国債）は最も増収だが定期がゼロになり、ガイドライン案の目安を超えるため改訂が必要。");
}
// ===== 10. 推奨案の移行スケジュール =====
{
  const s = slide(); n++;
  header(s, "推奨案（D）の進め方：理事会承認後、満期ごとに振り替え", "2027年1月の理事会後に開始。2027年3月末に80.3%、常陽2年定期の振替で83.8%");
  const steps = [
    ["2027年1月", "理事会で承認\n（12/24満期の600万円は自動継続）", "―"],
    ["2027.2〜3", "国債償還 2,000万円\n（0.7%・0.1%）を再投資", "―"],
    ["2027.2.19", "県信 1年定期\n573万円", "71.7%"],
    ["2027.3.23", "常陽 1年定期\n300万円", "73.4%"],
    ["2027.3.28", "常陽 1年定期\n1,210万円", "80.3%"],
    ["承認後〜2027.12", "常陽 2年定期 600万円\n中途解約または満期で振替", "83.8%"],
  ];
  s.line({ x: 0.8, y: 2.3, w: 8.4, h: 0, color: C.line, width: 3 });
  steps.forEach((st, i) => {
    const x = 0.5 + i * 1.52;
    s.circle({ x: x + 0.46, y: 2.06, w: 0.5, h: 0.5, fill: i === 5 ? C.yellow : C.green });
    s.text(String(i + 1), { x: x + 0.46, y: 2.06, w: 0.5, h: 0.5, size: 12, bold: true, color: i === 5 ? C.green : C.white, align: "center", valign: "middle", margin: 0 });
    s.text(st[0], { x, y: 1.5, w: 1.42, h: 0.4, size: 11, bold: true, color: C.green, align: "center", margin: 0 });
    card(s, x, 2.75, 1.42, 1.0);
    s.text(st[1], { x: x + 0.04, y: 2.78, w: 1.34, h: 0.95, size: 8.5, color: C.text, align: "center", valign: "middle", margin: 0 });
    s.text("国債比率 " + st[2], { x, y: 3.85, w: 1.42, h: 0.35, size: 9.5, bold: st[2] === "83.8%", color: st[2] === "83.8%" ? C.red : C.muted, align: "center", margin: 0 });
  });
  card(s, 0.5, 4.35, 9.0, 0.7, { fill: C.tint });
  s.text("効果：年間利息 約152万円 → 約204万円（+約51万円）。国債償還分の再投資でさらに +約36万円。残る定期2,842万円（県信2,119万円・常陽150万円・常陽5年573万円）は流動性として保持し、翌年度に見直し", { x: 0.7, y: 4.4, w: 8.6, h: 0.6, size: 10, color: C.text, valign: "middle", margin: 0 });
  footer(s, n, "財産目録別紙。600万円を承認直後に中途解約すれば2027年12月の満期を待つより約11万円増収（金利差約2.1%×約11か月）。解約利率は要確認");
  s.notes("理事会が2027年1月のため、12月24日満期の600万円は自動継続し、承認後に中途解約か満期待ちかを決める。2〜3月の満期3口で80%に到達する。");
}
// ===== 11. 償還年限の分散 =====
{
  const s = slide(); n++;
  header(s, "償還年限の分散（ラダー）案", "2026年12月〜2027年5月の購入分 4,683万円を2年・5年・10年に分ける");
  s.chart("bar", [{ name: "購入額", labels: ["2年（2028〜29年償還）", "5年（2031〜32年償還）", "10年（2036〜37年償還）"], values: [1000, 2000, 1683] }],
    { x: 0.4, y: 1.3, w: 5.0, h: 3.7, colors: [C.green2, C.green, C.yellow], showValue: true, fmt: "0\"万円\"", barDir: "col", valAxisMax: 2500 });
  const rows = [["年限", "購入額", "利回り目安"], ["2年", "1,000万円", "1.82%"], ["5年", "2,000万円", "2.22%"], ["10年", "1,683万円", "2.98%"], ["計", "4,683万円", "加重平均 約2.41%"]];
  s.table(rows, { x: 5.7, y: 1.35, w: 3.8, colW: [0.8, 1.3, 1.7], size: 10, hilite: 4, align: ["c", "r", "c"] });
  card(s, 5.7, 3.1, 3.8, 1.95, { fill: C.tint });
  s.text("ルールの提案", { x: 5.9, y: 3.18, w: 3.4, h: 0.35, size: 12, bold: true, color: C.green, margin: 0 });
  s.text([
    "同一年に償還を迎える額は基本財産の25%以下（ガイドライン第4条に追記）",
    "2030年償還分9,975万円は、償還時に2031年以降へ分散して再投資",
    "10年債は原則満期保有のため、途中の評価損は元本保全に影響しない",
  ], { x: 5.9, y: 3.55, w: 3.45, h: 1.45, size: 9.5, color: C.text, bullets: true, valign: "top" });
  footer(s, n, "利回りは2026年9月10日時点（二次情報）。検討会資料（7月23日）の証券会社仮計算（7月21日、4銘柄・額面4,000万円）では2年1.4%〜10年2.7%、平均1.975%");
  s.notes("購入分を2年・5年・10年に分ければ、2028年以降ほぼ毎年償還が来て、金利変動への追随と流動性の両方が確保できる。");
}
// ===== 12. 金融機関の選定 =====
{
  const s = slide(); n++;
  header(s, "金融機関の選定手順（ガイドライン第8条）", "同一条件で条件提示を依頼し、比較表を選定記録として保存");
  const banks = [
    ["野村證券 水戸支店", "国債 8,450万円を保護預り", "既発債の提示価格、新窓販国債、保護預り料"],
    ["常陽銀行 本店", "国債 3,525万円・定期 2,833万円", "新窓販国債の取扱い、中途解約利率、店頭金利"],
    ["茨城県信用組合 本店", "定期 2,692万円", "国債の取扱い有無、中途解約利率。扱えない場合の預け替え"],
    ["めぶき証券", "投資信託 1,000万円（通常財産）", "国債の提示価格、保護預り料、投信の評価額報告"],
  ];
  banks.forEach((b, i) => {
    const y = 1.35 + i * 0.92;
    card(s, 0.5, y, 5.6, 0.8);
    s.text(b[0], { x: 0.65, y: y + 0.05, w: 1.7, h: 0.7, size: 11, bold: true, color: C.green, valign: "middle", margin: 0 });
    s.text(b[1], { x: 2.4, y: y + 0.05, w: 1.5, h: 0.7, size: 9, color: C.muted, valign: "middle", margin: 0 });
    s.text(b[2], { x: 3.95, y: y + 0.05, w: 2.1, h: 0.7, size: 9, color: C.text, valign: "middle", margin: 0 });
  });
  card(s, 6.4, 1.35, 3.1, 3.66, { fill: C.tint });
  s.text("評価項目（7項目）", { x: 6.6, y: 1.45, w: 2.8, h: 0.35, size: 12, bold: true, color: C.green, margin: 0 });
  s.text(["利回り・価格", "信用力", "手数料", "保護預り費用", "事務処理体制", "情報提供・アフターサービス", "更生保護活動への理解・協力（寄附、社明運動、研修講師派遣、協力雇用主など）"], { x: 6.6, y: 1.85, w: 2.75, h: 2.7, size: 10, color: C.text, numbered: true, valign: "top" });
  s.text("※ 協力内容のみをもって選定しない（ガイドライン第8条(3)）", { x: 6.6, y: 4.65, w: 2.8, h: 0.3, size: 8.5, color: C.muted, margin: 0 });
  footer(s, n, "財産目録（令和8年3月31日現在）、資金運用ガイドライン（案）第8条");
  s.notes("現在取引のある4社に同じ条件で提示を依頼する。他県では役員の関係先や長年の取引先を選ぶ例が多いが、本協会はガイドラインどおり比較と記録を残す。");
}
// ===== 13. スケジュール =====
{
  const s = slide(); n++;
  header(s, "手続きとスケジュール（案）", "検討会 → 条件提示 → 理事会 → 認可申請（必要な場合） → 振替開始");
  const steps = [
    ["9月17/18日", "検討会", "配分目標・移行方法・分散ルール・提示先を決定"],
    ["9〜12月", "条件提示", "4社へ依頼、比較表を作成。定款・認可要否の確認"],
    ["12月24日", "定期満期", "常陽2年定期600万円は理事会前のため自動継続"],
    ["2027年1月", "理事会", "規程と配分変更を承認（定款により評議員会も）"],
    ["承認後", "認可申請", "定款変更に当たる場合、関東地方更生保護委員会へ"],
    ["2〜3月", "振替開始", "満期到来分から順次国債へ"],
    ["2027年5月", "理事会報告", "運用状況を報告、翌年度の配分見直し"],
  ];
  steps.forEach((st, i) => {
    const x = 0.5 + i * 1.29;
    s.rect({ x, y: 1.5, w: 1.22, h: 0.95, fill: i === 0 ? C.yellow : (i === 3 ? C.green2 : C.green), radius: 0.08 });
    s.text(st[0], { x, y: 1.52, w: 1.22, h: 0.4, size: 9.5, bold: true, color: i === 0 ? C.green : "CFE3D8", align: "center", margin: 0 });
    s.text(st[1], { x, y: 1.9, w: 1.22, h: 0.5, size: 12, bold: true, color: i === 0 ? C.green : C.white, align: "center", margin: 0 });
    s.text(st[2], { x, y: 2.55, w: 1.22, h: 1.2, size: 8.5, color: C.text, align: "left", valign: "top" });
  });
  card(s, 0.5, 3.9, 9.0, 1.1, { fill: C.tint });
  s.text([
    "更生保護事業法：定款の変更は法務大臣の認可（地方更生保護委員会へ委任）を受けなければ効力を生じない。協会定款に基本財産の内訳が記載されているかを確認し、申請の要否を決める",
    "令和8年2月18日に水戸保護観察所の立入検査あり。規程整備と選定記録の保存は検査対応の観点からも有益",
  ], { x: 0.7, y: 3.98, w: 8.6, h: 1.0, size: 9.5, color: C.text, bullets: true, valign: "top" });
  footer(s, n, "更生保護事業法（平成7年法律第86号）、関東地方更生保護委員会回答、令和7年度事業報告");
  s.notes("理事会は2027年1月。12月24日に満期を迎える常陽2年定期600万円は理事会前のため自動継続し、承認後に扱いを決める。振替の本格開始は2027年2月から。");
}
// ===== 14. 本日決めていただきたいこと =====
{
  const s = slide(); n++;
  header(s, "本日、決めていただきたいこと", "7項目");
  const q = [
    "規程案を、付録2の誤記修正のうえ理事会に付議してよいか",
    "配分目標を「国債等 約84%」（D案）とするか、C・E・F案とするか",
    "移行は満期到来分の順次振替とするか、中途解約利率の確認を条件に前倒しを認めるか",
    "「同一年の償還額は25%以下」の分散ルールを採用するか。年限配分（2年・5年・10年）はこれでよいか",
    "条件提示を依頼する金融機関の範囲（4社）と担当者",
    "理事会付議の時期と、定款変更認可申請の要否を確認する担当者",
    "通常財産の投資信託（6月末評価額1,277万円）の位置づけと、リスク資産割合の上限",
  ];
  q.forEach((t, i) => {
    const col = i < 4 ? 0 : 1, row = i < 4 ? i : i - 4;
    const x = 0.5 + col * 4.65, y = 1.35 + row * 0.92;
    s.rect({ x, y, w: 4.4, h: 0.8, fill: C.white, radius: 0.08, line: C.line });
    s.rect({ x: x + 0.15, y: y + 0.22, w: 0.36, h: 0.36, fill: C.white, line: C.green, radius: 0.04 });
    s.text(String(i + 1) + ". " + t, { x: x + 0.62, y: y + 0.05, w: 3.7, h: 0.7, size: 10.5, color: C.text, valign: "middle", margin: 0 });
  });
  footer(s, n);
  s.notes("チェックボックス形式。決定事項は事務局で議事録に残す。");
}
// ===== 15. 留意事項（確認中の事項） =====
{
  const s = slide(); n++;
  header(s, "留意事項：本資料作成時点で確認できていないこと", "会議前または会議後に確認が必要な項目");
  const items = [
    ["金利数値は二次情報", "財務省・日銀・常陽銀行の一次情報サイトに接続できず。国債利回り（2026年9月10日）、政策金利、預金金利は検索結果の要約に基づく"],
    ["協会定款の記載", "基本財産の内訳（預金・国債）が定款に記載されているか。認可申請の要否が決まる"],
    ["中途解約利率", "常陽銀行・茨城県信用組合の定期預金の中途解約利率と手数料の有無"],
    ["自動継続後の条件", "8月7日満期の常陽1年定期150万円の継続の有無と利率（5月22日満期の県信大口は6月30日現在の別紙で0.375%・2027.5.22満期を確認済み）"],
    ["投資信託の評価額", "2026年6月30日現在 12,768,757円（+276.9万円、めぶき証券の運用損益報告）。7月以降は未確認"],
    ["利子課税と開催日", "国債利息の源泉徴収の扱い（税理士に確認）。検討会の日付（9月17日は木曜）、理事会は2027年1月予定（日付未確認）"],
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
  s.notes("推測で埋めていない項目の一覧。特に金利数値は当日までに一次情報で差し替える。");
}
// ===== 16. 付録1 基本財産の明細 =====
{
  const s = slide(); n++;
  header(s, "付録1　基本財産の明細（令和8年3月31日現在）", "国債5銘柄 1億1,975万円、定期預金7口 5,525万円");
  const b = [["保管先", "銘柄", "利率", "償還日", "額面（円）"],
    ["野村證券 水戸支店", "利付国債 第469回", "0.7%", "2027.2.1", "10,000,000"],
    ["野村證券 水戸支店", "利付国債 第346回", "0.1%", "2027.3.20", "10,000,000"],
    ["野村證券 水戸支店", "利付国債 第179回", "1.0%", "2030.6.20", "40,000,000"],
    ["野村證券 水戸支店", "利付国債 第183回", "1.6%", "2030.12.20", "24,500,000"],
    ["常陽銀行 本店", "利付国債 第182回", "1.4%", "2030.9.20", "35,250,000"],
    ["計", "加重平均 1.14%", "", "", "119,750,000"]];
  s.table(b, { x: 0.5, y: 1.3, w: 4.4, colW: [1.25, 1.15, 0.45, 0.7, 0.85], size: 8, hilite: 6, align: ["l", "l", "c", "c", "r"] });
  const d = [["預入先", "種類", "利率", "満期日", "金額（円）"],
    ["県信 本店", "1年大口（自継）", "0.375%", "2027.5.22", "21,190,000"],
    ["県信 本店", "1年スーパー（自継）", "0.275%", "2027.2.19", "5,730,000"],
    ["常陽 本店", "2年 自継", "0.125%", "2026.12.24", "6,000,000"],
    ["常陽 本店", "1年 自継", "0.275%", "2027.3.28", "12,100,000"],
    ["常陽 本店", "5年 自継", "0.4%", "2030.9.17", "5,730,000"],
    ["常陽 本店", "1年 自継", "0.275%", "2026.8.7*", "1,500,000"],
    ["常陽 本店", "1年 自継", "0.4%", "2027.3.23", "3,000,000"],
    ["計", "加重平均 0.28%", "", "", "55,250,000"]];
  s.table(d, { x: 5.1, y: 1.3, w: 4.4, colW: [0.85, 1.25, 0.6, 0.85, 0.85], size: 8, hilite: 8, align: ["l", "l", "c", "c", "r"] });
  s.text("* 作成日（2026年9月12日）より前の満期日は自動継続されたものと推定。継続後の利率・満期日は要確認。年間利息：国債 1,365,500円、定期 153,850円（契約利率ベース）", { x: 0.5, y: 4.75, w: 9.0, h: 0.4, size: 8.5, color: C.muted });
  footer(s, n, "財産目録別紙（令和8年3月31日現在）。県信大口は6月30日現在の別紙（検討会資料）で継続後0.375%・満期2027.5.22を確認。*8.7満期分は継続未確認");
  s.notes("明細。令和7年度中に常陽の国債5,975万円が償還され、定期4,000万円の解約分と合わせて2030年償還の3銘柄を取得している。");
}
// ===== 17. 付録2 誤記修正 =====
{
  const s = slide(); n++;
  header(s, "付録2　規程案の誤記・文言の修正提案", "基本方針（案）2件、ガイドライン（案）10件");
  const rows = [["条項", "現行", "修正案"],
    ["基本方針 第4条", "分散型投信信託等", "分散型投資信託等"],
    ["基本方針 第6条", "原則とし複数の金融機関", "原則として複数の金融機関"],
    ["ガイドライン 2(2)", "価格変動リスクを伴う記入商品", "価格変動リスクを伴う金融商品"],
    ["ガイドライン 3(1)", "資金集中による集積性の低下", "資金集中による収益性の低下（文意要確認）"],
    ["ガイドライン 3(3)", "安全性の高い債権と適切な分散", "安全性の高い債券と適切な分散"],
    ["ガイドライン 4(1)", "金利変更リスク", "金利変動リスク"],
    ["ガイドライン 7(1)3", "市場価格変更リスク", "市場価格変動リスク"],
    ["ガイドライン 7(2)", "名称のみで投資または登記を判断せず", "名称のみで投機的取引か否かを判断せず（文意要確認）"],
    ["ガイドライン 8(3)3", "特殊詐欺防止どの他の研修", "特殊詐欺防止その他の研修"],
    ["ガイドライン 10(2)", "前条の結果確認については", "前項の確認結果については"],
    ["ガイドライン 12", "令和〇年〇月〇日から施行", "理事会承認日を記入"],
    ["ガイドライン 第4条（追加）", "―", "同一年に償還を迎える基本財産の額は原則25%以下"]];
  s.table(rows, { x: 0.5, y: 1.3, w: 9.0, colW: [2.0, 3.2, 3.8], size: 9, align: ["l", "l", "l"] });
  footer(s, n, "【更生保護協会】資金運用基本方針.docx／資金運用ガイドライン.docx（2026年8月19日付）");
  s.notes("誤記は理事会付議前に梶副理事長と事務局で修正する。「文意要確認」の2件は原案者に意図を確認。");
}

// ================= pptxgenjs 描画 =================
function toPptx() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "鈴木孝昌"; pres.title = "茨城県更生保護協会 基本財産運用検討会 説明資料（案）";
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
