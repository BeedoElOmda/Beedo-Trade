// Builds "Beedo-Trade User Guide.docx" for the Windows app. Usage: node make_guide.js <shots-dir> <out.docx> <version>
const fs = require('fs'), path = require('path');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, HeadingLevel, LevelFormat,
  BorderStyle, AlignmentType, PageBreak, Footer, PageNumber, VerticalAlign, ImageRun, TableOfContents } = require('docx');

const [SHOTS, OUT, VERSION] = process.argv.slice(2);
const FONT = 'Arial', MONO = 'Consolas', NAVY = '1F3A5F', TEAL = '117A8B', GREEN = '1E8449', AMBER = 'B9770E', RED = 'C0392B', GREY = '595959';
const W = 9026;

const run = (text, o = {}) => new TextRun({ text, ...o });
const P = (c, o = {}) => new Paragraph({ spacing: { after: 120 }, ...o, children: typeof c === 'string' ? [run(c)] : c });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [run(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(t)] });
const bullet = (c) => new Paragraph({ numbering: { reference: 'bul', level: 0 }, spacing: { after: 60 }, children: typeof c === 'string' ? [run(c)] : c });
const num = (c, ref = 'num') => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 80 }, children: typeof c === 'string' ? [run(c)] : c });
const numR = (ref, c) => num(c, ref);
const b = (t) => run(t, { bold: true });
const ui = (t) => run(t, { bold: true, color: TEAL });
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noB = { top: none, bottom: none, left: none, right: none };
const line = (c = 'D0D7DE') => ({ style: BorderStyle.SINGLE, size: 4, color: c });
const box = (c) => ({ top: line(c), bottom: line(c), left: line(c), right: line(c) });
const gap = (n = 160) => new Paragraph({ spacing: { after: n }, children: [] });

function cell(children, w, o = {}) {
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders: o.borders || box('D0D7DE'),
    shading: o.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: o.fill } : undefined,
    margins: o.margins || { top: 100, bottom: 100, left: 140, right: 140 }, verticalAlign: o.valign || VerticalAlign.TOP,
    children: Array.isArray(children) ? children : [children] });
}
const table = (widths, rows) => new Table({ width: { size: widths.reduce((a, c) => a + c, 0), type: WidthType.DXA }, columnWidths: widths,
  rows: rows.map((r, i) => new TableRow({ children: r, tableHeader: i === 0 })) });
function dataTable(widths, header, rows, rowFill) {
  const hdr = header.map((h, i) => cell(P([run(h, { bold: true, color: 'FFFFFF', size: 20 })], { spacing: { after: 0 } }), widths[i], { fill: NAVY }));
  return table(widths, [hdr, ...rows.map((r, ri) => r.map((c, i) => cell(typeof c === 'string' ? P([run(c, { size: 20 })], { spacing: { after: 0 } }) : c,
    widths[i], { fill: (rowFill && rowFill(ri)) || (ri % 2 ? 'F6F8FA' : undefined) })))]);
}
function callout(kind, title, text) {
  const k = { tip: [GREEN, 'E9F7EF', 'TIP'], note: [TEAL, 'E8F6F8', 'NOTE'], warn: [AMBER, 'FEF5E7', 'IMPORTANT'] }[kind];
  return table([W], [[cell([P([run(`${k[2]}  `, { bold: true, color: k[0], size: 18 }), run(title, { bold: true, size: 21 })], { spacing: { after: 60 } }),
    P(typeof text === 'string' ? [run(text, { size: 20 })] : text, { spacing: { after: 0 } })], W,
    { fill: k[1], borders: { top: none, bottom: none, right: none, left: { style: BorderStyle.SINGLE, size: 24, color: k[0] } } })]]);
}
function shot(file, caption, widthPx = 600) {
  const buf = fs.readFileSync(path.join(SHOTS, file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20); // PNG header
  return [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new ImageRun({ type: 'png', data: buf,
      transformation: { width: widthPx, height: Math.round(widthPx * h / w) }, altText: { title: caption, description: caption, name: file } })] }),
    P([run(caption, { italics: true, size: 18, color: GREY })], { alignment: AlignmentType.CENTER, spacing: { after: 200 } })];
}
function stepCard(n, title, body) {
  return table([800, W - 800], [[
    cell(P([run(String(n), { bold: true, size: 36, color: 'FFFFFF' })], { alignment: AlignmentType.CENTER, spacing: { after: 0 } }), 800, { fill: TEAL, borders: noB, valign: VerticalAlign.CENTER }),
    cell([P([run(title, { bold: true, size: 23, color: NAVY })], { spacing: { after: 40 } }), ...(Array.isArray(body) ? body : [P(body, { spacing: { after: 0 } })])],
      W - 800, { fill: 'F6F8FA', borders: noB })]]);
}
const steps = (...cards) => cards.flatMap((c, i) => [stepCard(i + 1, c[0], c[1]), gap(80)]);

// ---------- content ----------
const cover = [
  gap(1500),
  table([W], [[cell([
    P([run('BEEDO-TRADE', { bold: true, size: 64, color: 'FFFFFF' })], { alignment: AlignmentType.CENTER, spacing: { after: 100 } }),
    P([run('for Windows', { size: 32, color: 'D6EAF8' })], { alignment: AlignmentType.CENTER, spacing: { after: 0 } })],
    W, { fill: NAVY, borders: noB, margins: { top: 560, bottom: 560, left: 300, right: 300 } })]]),
  table([W], [[cell(P([run('User Guide', { bold: true, size: 26, color: 'FFFFFF' })], { alignment: AlignmentType.CENTER, spacing: { after: 0 } }),
    W, { fill: TEAL, borders: noB, margins: { top: 160, bottom: 160, left: 200, right: 200 } })]]),
  gap(500),
  P([run('Analyse Egyptian Exchange stocks with the Beedo technical-analysis course method: one signal, clear actions, and the evidence behind them.', { size: 24, color: GREY })], { alignment: AlignmentType.CENTER }),
  gap(1300),
  P([run(`Version ${VERSION}  \u2022  November 2026`, { size: 20, color: GREY })], { alignment: AlignmentType.CENTER }),
  new Paragraph({ children: [new PageBreak()] }),
  P([run('Contents', { bold: true, size: 32, color: NAVY })]),
  new TableOfContents('Contents', { hyperlink: true, headingStyleRange: '1-2' }),
  P([run('If the page numbers above are missing, right-click the table and choose Update Field.', { italics: true, size: 18, color: GREY })]),
];

const welcome = [
  h1('1. Welcome'),
  P('Beedo-Trade is a Windows program that applies the Beedo technical-analysis course to Egyptian Exchange (EGX) stocks. You type a stock code, and it shows:'),
  bullet([b('One signal'), run(' on the course ladder, from Confirm Sell to Confirm Buy')]),
  bullet([b('What to do'), run(' if you hold cash, and if you already own the stock')]),
  bullet([b('An interactive chart'), run(' with the moving averages, support and resistance lines, swing points, volume and RSI')]),
  bullet([b('The 11-step checklist'), run(', with the evidence for every step')]),
  bullet([b('A trade plan'), run(' sized to your cash and risk')]),
  bullet([b('A watchlist'), run(' that scans all your stocks at once')]),
  h2('What you need'),
  dataTable([3000, 6026], ['Requirement', 'Details'], [
    ['Windows 10 or 11 (64-bit)', 'Any recent Windows PC.'],
    ['Internet connection', 'To download daily prices. Each analysis takes a few seconds.'],
    ['Microsoft Edge WebView2', 'Built into Windows 11 and most Windows 10 PCs. Setup tells you if it is missing.'],
  ]),
  gap(),
  callout('warn', 'Not investment advice', 'Beedo-Trade is a learning and decision-support tool. It never places orders, and free price data can be delayed. Always check the live price and the day\u2019s EGX disclosures before trading.'),
];

const install = [
  h1('2. Installing Beedo-Trade'),
  ...steps(
    ['Download the installer', [P([run('Download '), b(`Beedo-Trade-Setup-${VERSION}.exe`), run(' from the Releases page of github.com/BeedoElOmda/Beedo-Trade, or use the copy you were given.')], { spacing: { after: 0 } })]],
    ['Open it', [P([run('Double-click the file. If Windows shows '), b('"Windows protected your PC"'), run(', click '), ui('More info'), run(', then '), ui('Run anyway'), run('. This appears because the app isn\u2019t code-signed; it is normal for small independent programs.')], { spacing: { after: 0 } })]],
    ['Choose who to install for', [P([run('Pick '), ui('Install for me only (recommended)'), run('. It needs no administrator password and installs into your user folder. Choose '), ui('Install for all users'), run(' only if several people use this PC: Windows will ask for administrator approval, and it installs into Program Files.')], { spacing: { after: 0 } })]],
    ['Accept the notice', [P([run('Read the notice (not investment advice, plus the MIT license), select '), ui('I accept the agreement'), run(', then '), ui('Next'), run('.')], { spacing: { after: 0 } })]],
    ['Keep the suggested folder', [P([run('Click '), ui('Next'), run('. The suggested folder already matches your choice in step 3.')], { spacing: { after: 0 } })]],
    ['Shortcuts and install', [P([run('Tick '), ui('Create a desktop shortcut'), run(' if you want one, then click '), ui('Install'), run('.')], { spacing: { after: 0 } })]],
    ['Finish', [P([run('Leave '), ui('Start Beedo-Trade now'), run(' ticked and click '), ui('Finish'), run('. You can also open this guide from here.')], { spacing: { after: 0 } })]],
  ),
  callout('note', 'Error "Access is denied" (Error 5) during setup', [run('This happens when '), b('Install for me only'), run(' is combined with a folder inside C:\\Program Files, which only an administrator can write to. Setup now warns you before this can happen. Either keep the suggested folder, or start again and choose '), b('Install for all users'), run('.')]),
  gap(),
  P([run('After installing you will find '), b('Beedo-Trade'), run(', '), b('Beedo-Trade User Guide'), run(' and '), b('Uninstall Beedo-Trade'), run(' in the Start menu. The first launch can take 10 to 20 seconds while Windows checks the new program; later launches are faster.')]),
];

const first = [
  h1('3. Your first analysis'),
  ...shot('home.png', 'The start screen: type a code or pick one of your watchlist stocks.', 560),
  num([run('Type an EGX code in the search box, for example '), b('COMI'), run('. Suggestions appear as you type.')]),
  num([run('Press '), ui('Enter'), run(' or click '), ui('Analyze'), run('.')]),
  num([run('Choose your position at the top right: '), ui('Cash holder'), run(' (you don\u2019t own it) or '), ui('Shareholder'), run(' (you do). The matching advice is highlighted.')]),
  gap(),
  callout('tip', 'Use the 4-letter EGX code', 'For example COMI (CIB), TMGH (Talaat Moustafa), SWDY (Elsewedy), ETEL (Telecom Egypt), EAST (Eastern Company), EGAL (Egypt Aluminum).'),
];

const reading = [
  h1('4. Reading the result'),
  h2('4.1  The signal and what to do'),
  ...shot('g_signal.png', 'COMI: First Buy, with the actions for both positions, the key numbers and the combined view.'),
  P('The coloured badge is the overall signal. The bar under it is the course\u2019s signal ladder, with your stock\u2019s position lit up:'),
  dataTable([2000, 3700, 3326], ['Signal', 'Meaning', 'Typical action'], [
    ['Confirm Buy', 'Trend, moving averages, RSI and volume agree upward', 'Cash holder: buy the full position'],
    ['First Buy', 'An uptrend is starting but isn\u2019t confirmed', 'Cash holder: buy part (e.g. half)'],
    ['Alarm Buy', 'Early signs of a turn upward', 'Get ready, don\u2019t buy yet'],
    ['Hold', 'No clear signal, or a sideways market', 'Stay as you are'],
    ['Alarm Sell', 'Early signs of a turn downward', 'Shareholder: tighten your stop'],
    ['First Sell', 'A downtrend is starting', 'Shareholder: reduce'],
    ['Confirm Sell', 'Everything agrees downward', 'Shareholder: sell'],
  ], (ri) => ['D5F5E3', 'E9F7EF', 'E8F8F5', 'F2F3F4', 'FEF5E7', 'FDEBD0', 'FADBD8'][ri]),
  gap(),
  P([run('The sentence next to the badge says why. When a signal is held back by a course rule (for example "price is still below MA18" or "the market is moving sideways"), it says so. The four boxes show '), b('RSI'), run(', today\u2019s '), b('volume'), run(' against its 20-day average, and the nearest '), b('support'), run(' and '), b('resistance'), run('. The '), b('Combined view'), run(' at the bottom joins this signal with the company’s fundamentals rating (section 6).')]),
  ...shot('sell.png', 'A shareholder view of a Confirm Sell (ABUK): the shareholder advice is highlighted.', 520),
  h2('4.2  The chart'),
  ...shot('g_chart.png', 'Candles with MA 5 / 9 / 18, support (S) and resistance (R) lines, swing arrows, volume and RSI.'),
  bullet([b('Moving averages: '), run('MA5 (pink), MA9 (yellow), MA18 (blue). The course\u2019s crossovers are 5\u00D79 = Alarm, 5\u00D718 = First, 9\u00D718 = Confirm.')]),
  bullet([b('S1 / S2 and R1 / R2: '), run('the nearest recent support (green) and resistance (red) levels.')]),
  bullet([b('Arrows: '), run('swing highs (red, pointing down) and swing lows (green, pointing up). Use them to judge patterns such as head and shoulders, double tops or triangles (checklist steps 10 and 11).')]),
  bullet([b('RSI panel: '), run('with the 30, 50 and 70 lines.')]),
  bullet([b('Controls: '), run('scroll the mouse wheel over the chart to zoom, drag to move back in time, and use the tick boxes above the chart to show or hide each layer.')]),
  h2('4.3  Checklist, triggers and trade plan'),
  ...shot('g_checklist.png', 'The 11-step checklist (left), what would change the signal, and the trade plan (right).'),
  P([b('11-step checklist: '), run('each course step with its reading and its rung on the ladder. Steps 10 and 11 (chart patterns) are judged by you on the chart.')]),
  P([b('What would change the signal: '), run('the next events up and down, such as "MA9 crossing above MA18 = Confirm Buy" or "a close below 126.81 = support broken".')]),
  P([b('Trade plan: '), run('enter your cash and the most you are willing to lose per trade (default 2%). It shows the entry (last close), a stop just below support, a 2R target, the number of shares, the cost and the loss if the stop is hit. Yellow notes warn when resistance is in the way. On weaker signals the plan is labelled as one to have ready, not a trade for today.')]),
];

const watch = [
  h1('5. Watchlist'),
  ...shot('watchlist.png', 'The watchlist after "Scan all", strongest buy first.'),
  numR('num2', [run('Open '), ui('Watchlist'), run(' in the left menu.')]),
  numR('num2', [run('Type a code in '), ui('Add EGX code'), run(' and click '), ui('Add'), run('. Remove a stock with the \u2715 on its chip.')]),
  numR('num2', [run('Click '), ui('Scan all'), run('. Every stock is analysed and sorted from the strongest buy to the strongest sell, with each company’s rating and the combined view.')]),
  numR('num2', 'Click any row to open its full analysis.'),
  P('Your watchlist is saved automatically and shown as quick-pick buttons on the start screen.'),
];

const fund = [
  h1('6. Company fundamentals and the Screener'),
  P('Your course tells you when to buy or sell. Fundamentals tell you whether the company is worth owning at all. Beedo-Trade rates every company with standard rules, then combines that rating with the course signal.'),
  h2('6.1  The fundamentals card'),
  ...shot('g_fund.png', 'COMI: rated Strong (83). Each tile shows the figure, its rating and the median of similar companies.'),
  P('Each figure is rated Good, Fair or Poor, and shown next to the median of similar companies (same industry where possible, otherwise the same sector or the whole market):'),
  dataTable([2500, 3300, 3226], ['Check', 'Good', 'Poor'], [
    ['P/E (valuation)', '10 or less, or well below peers', 'Over 30, far above peers, or loss-making'],
    ['P/B (price vs book)', '1.5 or less (banks: 1.0)', 'Over 5 (banks: 2.5) and above peers'],
    ['Return on equity', '15% or more', 'Under 8%'],
    ['Net profit margin', '10% or more', 'Under 3%'],
    ['Debt to equity', '0.5 or less', 'Over 1.5'],
    ['Earnings / revenue growth', '20% or more a year', 'Falling'],
    ['Dividend yield (bonus)', '4% or more', 'No penalty for paying no dividend'],
  ]),
  gap(80),
  P([b('Overall rating: '), run('Strong (70 or more out of 100), Fair (45 to 69) or Weak (under 45). Banks skip the margin and debt checks, which don’t fit how banks work. If fewer than three key figures are reported, the rating is '), b('Not enough data'), run('. This is common for smaller companies.')]),
  callout('note', 'Why growth needs 20% to count as good', 'Egypt’s high inflation lifts every company’s sales and profits in pounds. Growth below inflation means the business is shrinking in real terms, so 20% a year is the bar for "Good".'),
  gap(),
  h2('6.2  The combined view'),
  dataTable([2200, 2200, 4626], ['Company', 'Course signal', 'Combined view'], [
    ['Strong', 'First / Confirm Buy', 'Best setup: a strong company with a buy signal'],
    ['Strong', 'Alarm Buy or Hold', 'Put it on your watchlist and wait for a buy signal'],
    ['Strong', 'Any sell', 'Wait for the chart to turn before buying'],
    ['Fair', 'First / Confirm Buy', 'Acceptable: consider a smaller position'],
    ['Weak', 'First / Confirm Buy', 'Speculative: small size, or skip it'],
    ['Weak', 'No buy signal', 'Avoid'],
  ], (ri) => ['D5F5E3', 'E8F6F8', 'FEF5E7', 'E8F6F8', 'FEF5E7', 'FADBD8'][ri]),
  h2('6.3  The Screener'),
  ...shot('g_screener.png', 'The Screener: strong companies that are in a buy zone right now.', 470),
  numR('num5', [run('Open '), ui('Screener'), run(' in the left menu.')]),
  numR('num5', [run('Choose the '), ui('Company quality'), run(' (Strong only, or Strong or Fair), the '), ui('Technical signal'), run(' you want, and optionally a '), ui('Sector'), run('.')]),
  numR('num5', [run('Click '), ui('Run screener'), run('. It rates every EGX company, then runs your course checklist on the best 40. This takes 10 to 40 seconds.')]),
  numR('num5', 'Click any row to open its full analysis.'),
  gap(80),
  callout('tip', 'Use the Screener to find ideas, then check them', 'The Screener narrows about 300 stocks to a short list. Open each result, read its chart and checklist, and confirm the live price and the day’s news before acting.'),
];

const csv = [
  h1('7. Stocks without price history (Import CSV)'),
  P('Prices come from Yahoo Finance, which covers the larger, widely traded EGX stocks but not every company. If a stock isn\u2019t covered, you\u2019ll see "Yahoo Finance has no price history". You can still analyse it from a file of daily prices:'),
  numR('num3', [run('Export daily prices from your broker or a charting website as a '), b('CSV'), run(' file, with at least 60 trading days (a year is best).')]),
  numR('num3', [run('Type the stock code in the search box (optional, used as the name), then click '), ui('Import CSV'), run(' and choose the file.')]),
  gap(80),
  dataTable([3000, 6026], ['The file needs', 'Accepted forms'], [
    ['Date', '2026-11-05, 05/11/2026 or 11/05/2026 (one style for the whole file)'],
    ['Open, High, Low', 'Plain numbers; thousands separators like 1,234.5 are fine'],
    ['Close', 'A column named Close, Price or Last'],
    ['Volume (optional)', 'Volume or Vol.; values like 1.2M or 850K are understood'],
  ]),
];

const settings = [
  h1('8. Settings, updates and data'),
  h2('8.1  Light or dark'),
  P([run('Click '), ui('Light mode'), run(' / '), ui('Dark mode'), run(' at the bottom of the left menu.')]),
  ...shot('light.png', 'Light theme (EAST, Confirm Buy).', 520),
  h2('8.2  What Beedo-Trade remembers'),
  P('Your watchlist, cash, risk %, position (cash holder or shareholder) and theme are saved automatically in your user profile, in the folder %APPDATA%\\BeedoTrade. The About page shows the exact folder.'),
  h2('8.3  Updating to a new version'),
  numR('num4', [run('On the '), ui('About'), run(' page, click '), ui('Check for updates'), run('. This opens the GitHub Releases page.')]),
  numR('num4', 'Download the newer Beedo-Trade-Setup file and run it. It replaces the old version in place and closes Beedo-Trade first if it is open.'),
  numR('num4', 'Your watchlist and settings are kept.'),
];

const uninstall = [
  h1('9. Uninstalling'),
  P('Use either of the standard Windows ways:'),
  stepCard('A', 'From Windows Settings', [P([run('Open '), ui('Settings \u2192 Apps \u2192 Installed apps'), run(', find '), b('Beedo-Trade'), run(', click the '), ui('\u22EF'), run(' button and choose '), ui('Uninstall'), run('.')], { spacing: { after: 0 } })]),
  gap(80),
  stepCard('B', 'From the Start menu', [P([run('Open the Start menu, find '), b('Uninstall Beedo-Trade'), run(' and click it.')], { spacing: { after: 0 } })]),
  gap(),
  P([run('At the end, Beedo-Trade asks whether to '), b('also delete your settings and watchlist'), run('. Choose '), ui('No'), run(' to keep them for a future install, or '), ui('Yes'), run(' to remove everything. The program, its shortcuts and this guide are always removed.')]),
];

const trouble = [
  h1('10. Troubleshooting'),
  dataTable([3300, 5726], ['Problem', 'What to do'], [
    ['Setup: "Access is denied" (Error 5)', 'Choose "Install for me only" and keep the suggested folder, or choose "Install for all users" to install into Program Files (needs administrator approval).'],
    ['"Windows protected your PC"', 'Click More info, then Run anyway. The app isn\u2019t code-signed.'],
    ['The app window stays blank', 'Install Microsoft Edge WebView2 (free from Microsoft), then start Beedo-Trade again.'],
    ['"Yahoo Finance has no price history"', 'Yahoo doesn\u2019t carry that stock. Use Import CSV (section 7).'],
    ['"Could not reach Yahoo Finance"', 'Check your internet connection, firewall or VPN, then try again.'],
    ['Prices look a day old', 'Free data can lag, and on Friday and Saturday the latest price is Thursday\u2019s close. Check the live price in your broker app.'],
    ['Company rating says "Not enough data"', 'TradingView has too few reported figures for that company (common for smaller firms). Use the technical signal and keep positions small.'],
    ['The first start is slow', 'Normal: Windows checks a new program the first time. Later starts are faster.'],
  ]),
  gap(),
  P([run('Still stuck? On the About page, click '), ui('Report a problem'), run(' to open an issue on GitHub, and describe what you did and what you saw.')]),
  gap(),
  callout('warn', 'Not investment advice', 'Beedo-Trade applies a technical-analysis method for learning and decision support. It does not know your full financial situation and does not place orders. You make every decision.'),
];

const doc = new Document({
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 36, bold: true, color: NAVY },
        paragraph: { spacing: { before: 0, after: 200 }, keepNext: true, outlineLevel: 0, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: TEAL, space: 6 } } } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 26, bold: true, color: TEAL },
        paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    ...['num', 'num2', 'num3', 'num4', 'num5'].map((reference) => ({ reference, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] })),
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [P([run(`Beedo-Trade for Windows ${VERSION}  \u2022  page `, { size: 16, color: GREY }),
      new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GREY })], { alignment: AlignmentType.CENTER, spacing: { after: 0 } })] }) },
    children: [...cover, ...welcome, ...install, ...first, ...reading, ...watch, ...fund, ...csv, ...settings, ...uninstall, ...trouble],
  }],
});
Packer.toBuffer(doc).then((buf) => fs.writeFileSync(OUT, buf));
