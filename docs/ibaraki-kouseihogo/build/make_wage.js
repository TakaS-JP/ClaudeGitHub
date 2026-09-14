// 茨城県更生保護協会 職員給与規程（案）検討資料 生成スクリプト（Word）
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, HeadingLevel, BorderStyle, ShadingType, PageNumber, Footer, Header,
  LevelFormat, PageBreak, VerticalAlign, TableLayoutType, ImageRun,
} = require("docx");
const path = require("path");
const LOGO_G = fs.readFileSync(path.join(__dirname, "logo_g.png"));
const logoImg = (w, h) => new ImageRun({ data: LOGO_G, transformation: { width: w, height: h }, type: "png" });
const OUT = process.argv[2] || "wage.docx";

const FONT_BODY = "游明朝", FONT_HEAD = "游ゴシック";
const fontBody = { ascii: FONT_BODY, eastAsia: FONT_BODY, hAnsi: FONT_BODY, cs: FONT_BODY };
const fontHead = { ascii: FONT_HEAD, eastAsia: FONT_HEAD, hAnsi: FONT_HEAD, cs: FONT_HEAD };
const run = (text, opts = {}) => new TextRun({ text, font: fontBody, size: 21, ...opts });
const p = (text, opts = {}) => new Paragraph({ children: Array.isArray(text) ? text : [run(text, opts.run || {})], spacing: { after: 100, line: 300 }, ...opts.para });
const bold = (text, opts = {}) => run(text, { bold: true, ...opts });
const small = (text) => new Paragraph({ children: [run(text, { size: 17, color: "555555" })], spacing: { after: 80 } });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: fontHead, size: 28, bold: true })], spacing: { before: 280, after: 140 } });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: fontHead, size: 23, bold: true })], spacing: { before: 200, after: 100 } });
const bullet = (text) => new Paragraph({ children: Array.isArray(text) ? text : [run(text)], numbering: { reference: "bul", level: 0 }, spacing: { after: 60, line: 290 } });
const num = (text) => new Paragraph({ children: Array.isArray(text) ? text : [run(text)], numbering: { reference: "num1", level: 0 }, spacing: { after: 60, line: 290 } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const border = { style: BorderStyle.SINGLE, size: 4, color: "888888" };
const borders = { top: border, bottom: border, left: border, right: border };
function cell(text, w, o = {}) {
  const lines = String(text).split("\n");
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders, verticalAlign: VerticalAlign.CENTER,
    shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: "auto" } : undefined, margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: lines.map((ln) => new Paragraph({ alignment: o.align || AlignmentType.LEFT, spacing: { after: 0, line: 260 },
      children: [new TextRun({ text: ln, font: o.head ? fontHead : fontBody, size: o.size || 18, bold: !!o.head || !!o.bold })] })) });
}
function table(widths, headRow, rows, opts = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const mk = (r, isHead, ri) => new TableRow({ tableHeader: isHead, children: r.map((t, i) => cell(t, widths[i], { head: isHead, shade: isHead ? "D9E2F3" : (opts.boldRows && opts.boldRows.includes(ri) ? "F2F2F2" : undefined), align: isHead ? AlignmentType.CENTER : ((opts.align || [])[i] || AlignmentType.LEFT), bold: opts.boldRows && opts.boldRows.includes(ri), size: opts.size })) });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED, rows: [mk(headRow, true, -1), ...rows.map((r, i) => mk(r, false, i))] });
}
const R = AlignmentType.RIGHT, C = AlignmentType.CENTER, L = AlignmentType.LEFT;
const yen = (n) => n.toLocaleString("ja-JP");

// ---------- 前提数値 ----------
const HOURS_M = 120; // 週30時間（1日6時間×5日）、年間所定労働日数240日と仮定した月平均所定労働時間
const MIN_NOW = 1074, MIN_NEXT = 1136;
const scen = [
  ["S1", "規程案のまま", 130000],
  ["S2", "2026年10月改定の最低賃金1,136円に準拠", 136400],
  ["S3", "時給1,200円相当", 144000],
  ["S4", "時給1,300円相当", 156000],
];
const calc = (b) => ({ hourly: b / HOURS_M, annual: b * 12 + 120000 + b * 2 });

const children = [];
// 表紙
children.push(
  new Paragraph({ alignment: C, spacing: { before: 1500, after: 200 }, children: [logoImg(85, 100)] }),
  new Paragraph({ alignment: C, spacing: { before: 200, after: 200 }, children: [new TextRun({ text: "更生保護法人 茨城県更生保護協会", font: fontHead, size: 30 })] }),
  new Paragraph({ alignment: C, spacing: { after: 200 }, children: [new TextRun({ text: "職員給与規程（案）等の検討", font: fontHead, size: 40, bold: true })] }),
  new Paragraph({ alignment: C, spacing: { after: 800 }, children: [new TextRun({ text: "提出資料（案）", font: fontHead, size: 40, bold: true })] }),
  new Paragraph({ alignment: C, spacing: { after: 120 }, children: [run("検討会　令和8年（2026年）9月17日（木）又は18日（金） 11:30〜　於：景山（開催日は要確認）", { size: 22 })] }),
  new Paragraph({ alignment: C, spacing: { before: 1600, after: 120 }, children: [run("作成日：2026年9月12日（2026年9月14日改訂：理事会を2027年1月予定として日程を修正）", { size: 20 })] }),
  new Paragraph({ alignment: C, spacing: { after: 120 }, children: [run("作成：理事　鈴木 孝昌", { size: 22 })] }),
  new Paragraph({ alignment: C, spacing: { before: 600 }, children: [run("本資料は、2026年8月22日にBoxへ保存された「職員給与規程」（附則の施行日が空欄の案）、現行「職員就業規則」（平成26年6月1日施行）、令和8年7月23日付 事務局「書類送付ご案内」添付の平成25年案および理事会議事録、令和8年度理事会資料に基づく。", { size: 18, color: "555555" })] }),
  pageBreak(),
);

// 1 結論
children.push(h1("1．結論（本検討会への提案）"));
children.push(p([bold("提案1　"), run("「職員給与規程（案）」は、基本給表の水準を2026年10月18日（予定）改定後の茨城県最低賃金1,136円以上に引き上げたうえで理事会に付議する。案の基本給（週30時間勤務 月額130,000円）は時給換算で約1,083円であり、現行の最低賃金1,074円は僅かに上回るが、改定後の1,136円を下回る。理事会は2027年1月の予定で最低賃金の発効（2026年10月18日）より後になるため、発効日から理事会承認までの間は、現行就業規則第7条2項に基づく理事長の決定により暫定的に最低賃金以上の基本給を支給し、理事会で規程の承認と併せて追認する。")]));
children.push(p([bold("提案2　"), run("週30時間勤務の基本給は月額136,400円以上（時給1,136円相当）とし、協会の財政状況を踏まえ、時給1,200円相当（月額144,000円）を目安に検討する。年間人件費の増加は現行案比で約9万〜20万円。")]));
children.push(p([bold("提案3　"), run("時間外手当の1時間当たり単価の算式（案第9条2項）を、労働基準法施行規則第19条に沿って「基本給月額÷月平均所定労働時間（年間所定労働時間÷12）」に改める。案の算式（2週間の勤務時間×26で除す）は年間休日を考慮せず、単価が法定算式より低くなる。")]));
children.push(p([bold("提案4　"), run("給与規程と同時に現行就業規則を改正し、年次有給休暇を労働基準法第39条の付与日数（週30時間以上勤務は勤続6年6か月以上で年20日）に合わせる。現行規則の「年間10日」は勤続1年6か月以上の職員には法定を下回る。")]));
children.push(p([bold("提案5　"), run("退職手当（現行就業規則第15条：退職時の月額給与×勤務年数）の見込額と退職給与引当金（令和8年3月31日現在1,650,000円）の差を確認し、引当金の年間繰入額（現行150,000円）の見直しか、算定方法の見直しのいずれかを決める。")]));
children.push(p([bold("提案6　"), run("社会保険（健康保険・厚生年金）の適用状況、現行の支給実額、職員本人の同意（労働契約法第9条・第10条）を事務局で確認し、必要に応じて社会保険労務士の確認を経て理事会に付議する。")]));
children.push(h2("提案の理由（要点）"));
children.push(bullet("茨城県最低賃金は2025年10月12日から時間額1,074円。茨城地方最低賃金審議会は2026年8月24日に1,136円（62円引上げ）を答申し、発効は2026年10月18日の予定（二次情報。茨城労働局の告示で要確認）。"));
children.push(bullet("案の基本給表は全区分が時給1,080〜1,100円程度で設計されており、10月改定後は非常勤（1,100円）を含め全区分が最低賃金を下回る。"));
children.push(bullet("平成25年5月の理事会で就業規則案は「内容を検討のうえ再提出」の議長裁定となり、平成26年7月理事会で現行就業規則が承認された。当時の理事会でも「職員の待遇、特に給与について他法人との比較を承知したい」との意見が出ている。"));
children.push(bullet("令和7年度の給料手当は1,850,000円（決算）で、一般会計支出21,868,211円の8.5%。時給1,200円相当への引上げでも年間20万円程度の増加にとどまる。"));
children.push(pageBreak());

// 2 現状
children.push(h1("2．現状"));
children.push(h2("2-1．規程の経緯"));
children.push(table([2200, 7438], ["時期", "経緯"], [
  ["平成25年5月8日", "理事会に「就業規則（案）」「給与細則（案）」「退職慰労金支給細則（案）」を当日動議で上程。定年年齢、他法人との給与比較、職員数の弾力化について意見が出て、「内容を検討のうえ再提出」の議長裁定。平成25年度予算に基づく給与執行は承認"],
  ["平成26年7月", "鬼澤理事長時代の理事会で、大野理事立案の就業規則（全17条）を審議承認。施行日は平成26年6月1日。給与は「基本給及び諸手当」とのみ規定し、金額の定めはない"],
  ["令和8年7月23日", "検討会開催。事務局から平成25年案のコピーと議事録のコピーを理事へ送付"],
  ["令和8年8月22日", "「職員給与規程」（附則の施行日が空欄、作成者・作成日の記載なし）と現行就業規則をBoxに保存"],
], { align: [L, L] }));
small("出典：理事会議事録（平成25年5月8日）、事務局「書類送付ご案内」（令和8年7月23日）、Box「0.鈴木孝昌／(更生保護協会)」20260822_更生保護法人茨城県更生保護協会職員給与規程.pdf");

children.push(h2("2-2．現行就業規則（平成26年6月1日施行）の要点"));
children.push(table([2400, 7238], ["項目", "現行の定め"], [
  ["職員", "事務局長及び主事等。理事長が任命（第2条）"],
  ["任用期間", "3年（再任可）。新規採用者は3か月を試用（第3条）"],
  ["勤務時間", "始業9時30分、終業16時30分、休憩12〜13時（1日6時間、週30時間）（第4条）"],
  ["休日", "土日、祝日、年末年始（12月29日〜1月3日）、保護観察所の閉庁日（第5条）"],
  ["有給休暇", "年間10日。病気・慶弔は必要の範囲で有給（第6条）"],
  ["給与", "基本給及び諸手当。諸手当は職務内容・経験・能力・資格等と協会の財政状況を勘案して付加（第7条）。金額の定めなし"],
  ["通勤手当", "実費（第9条）"],
  ["支払日", "毎月16日。休日の場合は前日（第10条）"],
  ["期末手当", "6月・12月に支給することができる（第11条）"],
  ["定年", "満70歳に達する日の属する年度末で自然退職（第13条）"],
  ["退職手当", "退職時の月額給与×勤務年数（1年未満の端数は6月以上切上げ、6月未満切捨て）。名誉信用毀損による解任の場合は不支給（第15条）"],
  ["改正", "理事会の議決（第17条）"],
], { align: [L, L] }));

children.push(h2("2-3．職員体制と人件費の実績"));
children.push(table([3600, 2200, 3638], ["項目", "数値", "出典"], [
  ["事務局職員", "事務局長 鈴木直子（就任 平成22年9月26日）1名", "令和8年度理事会資料 役職員名簿（令和8年4月1日現在）"],
  ["勤続年数（2026年9月時点）", "約16年（2010年9月26日就任）", "就任日から算定（平成25年当時は主事）"],
  ["令和7年度 給料手当（決算）", "1,850,000円", "令和7年度一般会計収支決算報告（予算どおり）"],
  ["令和7年度 退職給与引当金繰入", "150,000円", "同上"],
  ["令和7年度 福利厚生費", "36,141円（労働保険他）", "同上"],
  ["退職給与積立金残高（令和8年3月31日）", "1,650,000円", "職員退職手当特別会計、財産目録"],
  ["人件費計（給料手当＋引当繰入＋福利厚生）", "2,036,141円（支出総額の9.3%）", "計算値"],
], { align: [L, L, L] }));
small("給料手当1,850,000円の内訳（基本給・手当・期末手当の別）は理事会資料に記載がなく、現行の支給実額は事務局で要確認。");
children.push(pageBreak());

// 3 給与規程（案）
children.push(h1("3．職員給与規程（案）の要点"));
children.push(table([2200, 7438], ["条項", "案の内容"], [
  ["第2条 給与の種類", "一般職員：基本給＋諸手当（役職手当・時間外勤務手当・通勤手当ほか）。非常勤職員：基本給のみ"],
  ["第3条 支給日", "毎月16日。基本給・役職手当は当月分、通勤手当・時間外は前月分。本人の申出で口座振込可"],
  ["第4条 基本給（別表）", "一般職員 A：週30時間 月額130,000円／B：週20〜30時間未満 88,000〜127,600円／C：週10〜20時間未満 44,000〜83,600円。非常勤：時給1,100円"],
  ["第6条 昇給", "年1回2月に決定し4月支給分から。経営状況等によりやむを得ない場合は理事会に諮り停止・延伸可"],
  ["第7条 役職手当", "事務局長 月額10,000円、主事 月額5,000円（兼務は上位のみ）"],
  ["第8条 通勤手当", "公共交通：定期券相当の実費（上限20,000円）。自家用車：通勤距離1kmにつき15円（上限20,000円）。自転車：2,000円。2km未満は不支給"],
  ["第9条 時間外手当", "時間外の全時間に1時間当たり基本給の125%（22時〜5時は150%）。1時間当たり額＝基本給月額×12÷（2週間の勤務時間×26）"],
  ["第10条 給与の減額", "欠勤・遅刻・早退は1時間当たり額を減額"],
  ["第11条 賞与", "年2回（6月・12月）、各基本給1月分以内。採用6月未満・支給日不在籍者は不支給"],
  ["第11条（重複） 改訂", "規程の変更は理事会の承認"],
  ["附則", "施行日は空欄"],
], { align: [L, L] }));
small("出典：Box「0.鈴木孝昌／(更生保護協会)」20260822_更生保護法人茨城県更生保護協会職員給与規程.pdf（作成者・作成日の記載なし）。");
children.push(pageBreak());

// 4 法令適合性
children.push(h1("4．法令との適合性の確認"));
children.push(h2("4-1．最低賃金（最も重要）"));
children.push(p("茨城県最低賃金は2025年10月12日から時間額1,074円。2026年10月18日（予定）から1,136円（茨城地方最低賃金審議会の2026年8月24日答申、二次情報）。月給制の場合は「月給÷月平均所定労働時間」で時間額に換算して比較する。年間所定労働日数を240日（2026年の平日261日から祝日17日・年末年始の平日4日を除いた概算）と仮定すると、週30時間勤務の月平均所定労働時間は120時間となる。"));
children.push(table([2600, 1500, 1500, 1500, 2538], ["区分（案）", "月額（下限）", "時給換算", "現行1,074円", "改定後1,136円"], [
  ["A 週30時間", "130,000円", "1,083円", "適合（＋9円）", "不適合（▲53円）"],
  ["B 週20〜30時間未満（20時間の場合）", "88,000円", "1,100円", "適合", "不適合"],
  ["C 週10〜20時間未満（10時間の場合）", "44,000円", "1,100円", "適合", "不適合"],
  ["非常勤（時給）", "1,100円", "1,100円", "適合", "不適合（▲36円）"],
], { align: [L, R, R, C, C] }));
small("換算：A＝130,000÷120、B＝88,000÷（4時間×240日÷12＝80時間）、C＝44,000÷（2時間×240日÷12＝40時間）。役職手当は最低賃金の比較対象に含まれるが、通勤手当・賞与・時間外割増は除外される。年間所定労働日数は事務局の暦で要確認。");
children.push(p([bold("必要水準　"), run("週30時間勤務で1,136円を満たす月額は136,400円以上（1,136円×120時間＝136,320円）。非常勤は時給1,136円以上。")]));

children.push(h2("4-2．時間外手当の単価算式"));
children.push(p("案第9条2項の算式は「基本給月額×12÷（2週間の勤務時間×26）」であり、週30時間の場合の分母は1,560時間（年間休日を考慮しない）。1時間当たり額は130,000×12÷1,560＝1,000円となる。労働基準法施行規則第19条は月給制の割増賃金の基礎を「月額÷月における所定労働時間数（月により異なる場合は1年間の平均）」と定めており、この算式では1,083円（130,000÷120）となる。案の算式は法定算式より単価が約8%低くなるため、「基本給月額÷月平均所定労働時間」に改める。"));

children.push(h2("4-3．年次有給休暇（就業規則の課題）"));
children.push(p("労働基準法第39条により、週30時間以上勤務する職員の付与日数は勤続6か月10日、1年6か月11日、2年6か月12日、3年6か月14日、4年6か月16日、5年6か月18日、6年6か月以上20日。現行就業規則第6条の「年間10日」は勤続1年6か月以上の職員には法定を下回り、その部分は無効（労働基準法第13条）となる。勤続16年の事務局長には年20日の付与が必要。"));

children.push(h2("4-4．社会保険・労働保険"));
children.push(p("更生保護法人は法人であるため健康保険・厚生年金保険の強制適用事業所となり、週30時間勤務の職員は原則として被保険者に該当する（70歳以上は厚生年金の対象外、75歳以上は健康保険の対象外）。令和7年度の福利厚生費36,141円（労働保険他）からは社会保険料の事業主負担（月額給与の約15%、年間約25万円規模）が計上されていないように見えるため、適用状況と職員の年齢・加入状況を事務局で確認する。"));

children.push(h2("4-5．労働条件の変更手続"));
children.push(p("職員が10人未満のため就業規則の労働基準監督署への届出義務はないが、給与規程は就業規則の一部であり、現行の支給額を下回る変更は労働契約法第9条・第10条の不利益変更に当たり、職員の同意が必要となる。現行の支給実額を確認したうえで、案の金額との差を把握する。"));

children.push(h2("4-6．通勤手当の非課税限度額"));
children.push(p("自家用車通勤の非課税限度額は片道距離に応じて月額4,200円〜66,400円（2026年4月1日以後支払分から65km以上の区分が細分化）。案第8条(2)の「通勤距離1kmにつき15円」は、1日当たり（片道×2）か月当たりかが読み取れないため、「片道距離×2×出勤日数×15円」等に明確化し、非課税限度額の範囲内で設計する。"));
children.push(pageBreak());

// 5 水準の試算
children.push(h1("5．基本給水準の試算（週30時間勤務・A区分）"));
children.push(table([1000, 3400, 1300, 1200, 1500, 1238], ["案", "内容", "月額基本給", "時給換算", "年間人件費\n（概算）", "現行案比"], scen.map(([k, name, b], i) => { const c = calc(b), base = calc(scen[0][2]).annual; return [k, name, yen(b) + "円", yen(Math.round(c.hourly)) + "円", yen(c.annual) + "円", (c.annual - base >= 0 ? "+" : "") + yen(c.annual - base) + "円"]; }), { align: [C, L, R, R, R, R], boldRows: [2] }));
small("年間人件費＝基本給×12＋役職手当（事務局長10,000円×12）＋賞与（基本給×2か月、案第11条の上限）。社会保険料の事業主負担・退職給与引当繰入・福利厚生費は含まない。参考：令和7年度 給料手当決算 1,850,000円。");
children.push(p("S2は2026年10月改定後の最低賃金の下限であり、次回改定（例年10月）で再び下回る可能性が高い。S3（時給1,200円相当）は当面の改定に耐える水準として推奨する。基本給表は月額を固定せず「時給×月平均所定労働時間」で毎年度見直す方式にすると、最低賃金改定への追随が容易になる。"));
children.push(p("なお、B・C区分および非常勤の時給についても、同じ基準時給（1,136円以上、推奨1,200円）で再計算する。"));

// 6 退職金
children.push(h1("6．退職手当の見込みと引当金"));
children.push(p("現行就業規則第15条：退職手当＝退職時の月額給与×勤務年数。「月額給与」に役職手当を含むかは規定上明確でないため、両方を示す。"));
children.push(table([2600, 1700, 1700, 1700, 1938], ["前提", "月額給与", "勤続16年（2026年）", "勤続20年（2030年）", "引当金残高（見込み）"], [
  ["S1 基本給のみ", "130,000円", "2,080,000円", "2,600,000円", "2026年 1,650,000円\n2030年 2,250,000円"],
  ["S1 基本給＋役職手当", "140,000円", "2,240,000円", "2,800,000円", "同上"],
  ["S3 基本給のみ", "144,000円", "2,304,000円", "2,880,000円", "同上"],
  ["S3 基本給＋役職手当", "154,000円", "2,464,000円", "3,080,000円", "同上"],
], { align: [L, R, R, R, L] }));
small("引当金は令和8年3月31日現在1,650,000円、年150,000円繰入（令和7年度実績）で試算。勤続年数は就任日（平成22年9月26日）から算定。");
children.push(p("いずれの前提でも退職手当の見込額が引当金を43万〜83万円上回る。対応案は、(a) 引当金の年間繰入額を150,000円から250,000〜300,000円に引き上げる、(b) 平成25年案のように「引当金の範囲内で理事会が決定」する方式に改める、(c) 算定基礎を基本給に限定する、のいずれか。職員の既得の期待に関わるため、(a)を基本に検討することを提案する。"));
children.push(pageBreak());

// 7 修正提案
children.push(h1("7．給与規程（案）・就業規則の修正提案"));
children.push(table([2000, 3600, 4038], ["条項", "現行の記載", "修正案"], [
  ["案 別表 基本給", "A 130,000円ほか（時給約1,080〜1,100円）", "基準時給1,136円以上（推奨1,200円）×月平均所定労働時間で再計算。毎年度見直し"],
  ["案 第9条2項", "基本給月額×12÷（2週間の勤務時間×26）", "基本給月額÷月平均所定労働時間（年間所定労働時間÷12）"],
  ["案 第11条（2か所）", "賞与と規程の改訂が同じ条番号", "改訂を第12条に繰り下げ"],
  ["案 第4条／第7条", "「別紙」と「別表」が混在", "「別表」に統一"],
  ["案 第3条2項", "「ただし。役職手当については」", "「ただし、役職手当については」"],
  ["案 第8条(1)", "「定期券で算出された金額のいずれか低い実費」", "「定期券の額又は実費のいずれか低い額」"],
  ["案 第8条(2)", "通勤距離1kmにつき15円（期間の単位が不明）", "片道距離×2×出勤日数×15円（月額）。非課税限度額の範囲内"],
  ["案 第2条3項", "「就業規則第7条第1項に基づき付加給付」", "付加できる手当の種類を列挙（扶養手当・資格手当等の要否を決定）"],
  ["案 附則", "施行日が空欄", "2027年1月の理事会承認日（基本給の最低賃金対応部分は令和8年10月18日に遡及適用）"],
  ["就業規則 第6条", "年次有給休暇 年間10日", "労働基準法第39条の付与日数表（勤続6年6か月以上20日）"],
  ["就業規則 第9条", "通勤手当は実費", "給与規程第8条による（上限設定と整合）"],
  ["就業規則 第11条", "期末手当", "「賞与」に用語統一（給与規程第11条と整合）"],
  ["就業規則 第15条", "退職時の月額給与×勤務年数", "「月額給与」の範囲（役職手当の含否）を明記。引当金との関係を規定"],
], { align: [L, L, L], size: 17 }));

// 8 手続き
children.push(h1("8．手続きとスケジュール（案）"));
children.push(table([2400, 7238], ["時期", "手続き"], [
  ["2026年9月17日又は18日", "検討会：基準時給、退職金の扱い、就業規則の同時改正の方針を決定"],
  ["2026年9月〜10月", "事務局：現行支給実額・社会保険適用状況・年間所定労働日数の確認。必要に応じ社会保険労務士に規程案の確認を依頼。職員への説明と同意"],
  ["2026年10月18日", "茨城県最低賃金1,136円発効（予定）。理事会前のため、理事長の決定（現行就業規則第7条2項）により暫定的に時給換算1,136円以上の基本給の支給を開始。差額が生じた場合は発効日に遡って支払う"],
  ["2026年11月〜12月", "給与規程・就業規則改正案の確定（社会保険労務士の確認後）、理事会資料の作成"],
  ["2027年1月 理事会", "給与規程・就業規則改正の承認（就業規則第17条、給与規程案第11条）。暫定措置の追認"],
  ["2027年2月", "給与規程第6条に基づく昇給の初回決定（4月支給分から）"],
], { align: [L, L] }));
small("最低賃金は規程の有無にかかわらず発効日から適用されるため、理事会承認（2027年1月）を待たずに支給額を引き上げる必要がある。");

// 9 諮問
children.push(h1("9．本検討会で決めていただきたい事項"));
children.push(num("基本給表の基準時給を、最低賃金1,136円（S2）とするか、1,200円（S3）またはそれ以上とするか。"));
children.push(num("基本給表を「時給×月平均所定労働時間」で毎年度見直す方式に改めるか。"));
children.push(num("時間外手当の単価算式を法定算式に改めることの承認。"));
children.push(num("就業規則（有給休暇日数、通勤手当、期末手当の用語、退職手当の算定基礎）を同時に改正するか。"));
children.push(num("退職手当と引当金の差への対応（繰入増額、理事会決定方式、算定基礎の限定のいずれか）。"));
children.push(num("扶養手当・資格手当・慶弔金（平成25年案にあり、今回の案にはない）を設けるか。"));
children.push(num("社会保険労務士への確認依頼の要否と、理事会付議の時期。"));

// 10 確認できなかった事項
children.push(h1("10．本資料作成時点で確認できなかった事項"));
children.push(bullet("給与規程（案）の作成者・作成日、および本検討会での取扱い（9月の検討会の議題に含まれるか）。理事会は2027年1月の予定と聞いているが、日付は未確認。"));
children.push(bullet("現行の支給実額（基本給・手当・期末手当の内訳）。令和7年度の給料手当1,850,000円の内訳は理事会資料に記載がない。"));
children.push(bullet("社会保険（健康保険・厚生年金）の適用状況と職員の年齢。"));
children.push(bullet("年間所定労働日数（本資料は240日と仮定）。保護観察所の閉庁日の日数。"));
children.push(bullet("2026年10月改定の最低賃金1,136円と発効日10月18日は二次情報（審議会答申の報道）。茨城労働局の告示で要確認。労働基準法・労働契約法の条文も一次情報サイトに接続できず、二次情報に基づく。"));
children.push(bullet("退職手当の「月額給与」に役職手当を含むかの解釈、過去の退職者への支給実績。"));
children.push(bullet("他県の更生保護協会の職員給与水準（平成25年理事会で比較の要望があったが、データは入手できていない）。"));

// 11 出典
children.push(h1("11．出典一覧"));
children.push(table([3800, 2000, 3838], ["資料", "日付", "所在"], [
  ["更生保護法人茨城県更生保護協会職員給与規程（案）・現行職員就業規則", "規程案：作成日記載なし（Box保存 2026年8月22日）／就業規則：平成26年6月1日施行", "Box「0.鈴木孝昌／(更生保護協会)」20260822_更生保護法人茨城県更生保護協会職員給与規程.pdf"],
  ["事務局「書類送付ご案内」、平成25年就業規則（案）・給与細則（案）・退職慰労金支給細則（案）", "令和8年7月23日", "Box「0.鈴木孝昌／(更生保護協会)」20260723_書類送付ご案内.pdf"],
  ["理事会議事録（第4号議案 就業規則（案）について）", "平成25年5月8日", "Box「0.鈴木孝昌／(更生保護協会)」20130508_理事会議事録（就業規則案・基本財産変更）.pdf"],
  ["令和8年度理事会資料（令和7年度決算、財産目録、役職員名簿）", "令和8年5月13日", "Box「0.鈴木孝昌／(更生保護協会)」202605_更生保護法人茨城県更生保護協会.pdf"],
  ["茨城県最低賃金 時間額1,074円", "2025年10月12日発効", "茨城県、つくば市、小美玉市の公表資料（二次情報）"],
  ["茨城県最低賃金 時間額1,136円（62円引上げ）答申、発効予定2026年10月18日", "答申 2026年8月24日", "株式会社ゼロプラス記事、STRIDE、ろうどうDB（二次情報）。一次情報：茨城労働局"],
  ["年次有給休暇の付与日数（労働基準法第39条）", "―", "厚生労働省「確かめよう労働条件」Q&A、連合 労働相談Q&A"],
  ["社会保険の加入要件（法人は強制適用、週所定労働時間が通常の労働者の4分の3以上）", "―", "弥生、社労士ナビ、連合 労働相談Q&A（二次情報）。一次情報：日本年金機構"],
  ["通勤手当の非課税限度額（2026年4月改正）", "2026年4月1日施行", "OBC、電通総研、ラクラス各解説記事（二次情報）。一次情報：国税庁"],
], { align: [L, L, L], size: 16 }));

const doc = new Document({
  creator: "鈴木孝昌", title: "茨城県更生保護協会 職員給与規程（案）等の検討 提出資料（案）",
  styles: { default: { document: { run: { font: fontBody, size: 21 } } }, paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: fontHead, size: 28, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "1F3864", space: 2 } } } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: fontHead, size: 23, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
  ] },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "・", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 480, hanging: 240 } } } }] },
    { reference: "num1", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1．", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 420 } } } }] },
  ] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: R, children: [logoImg(13, 15), run("　"), run("茨城県更生保護協会　職員給与規程（案）等の検討 提出資料（案）　2026年9月12日", { size: 16, color: "777777" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: C, children: [new TextRun({ children: [PageNumber.CURRENT, " / ", PageNumber.TOTAL_PAGES], font: fontBody, size: 16, color: "777777" })] })] }) },
    children }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("written", OUT, buf.length); });
