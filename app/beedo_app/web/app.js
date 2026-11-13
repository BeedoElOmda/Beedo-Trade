/* Beedo-Trade UI. Talks to Python through pywebview (desktop) or /api (dev server). */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n, d = 2) => (n == null || isNaN(n) ? "–" : Number(n).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }));
const RUNGS = { 3: "Confirm Buy", 2: "First Buy", 1: "Alarm Buy", 0: "Hold", "-1": "Alarm Sell", "-2": "First Sell", "-3": "Confirm Sell" };
const rcls = (r) => (r >= 0 ? `r${r}` : `rm${-r}`);
const SUGGEST = [["GOLD", "Gold, EGP per gram (24k)"], ["SILVER", "Silver, EGP per gram"], ["COMI", "Commercial International Bank"], ["TMGH", "Talaat Moustafa Group"], ["SWDY", "Elsewedy Electric"],
  ["ETEL", "Telecom Egypt"], ["EAST", "Eastern Company"], ["EGAL", "Egypt Aluminum"], ["FWRY", "Fawry"], ["ABUK", "Abu Qir Fertilizers"],
  ["HRHO", "EFG Holding"], ["ORAS", "Orascom Construction"], ["PHDC", "Palm Hills"], ["MFPC", "Misr Fertilizers (MOPCO)"],
  ["AMOC", "Alexandria Mineral Oils"], ["ESRS", "Ezz Steel"], ["JUFO", "Juhayna"], ["EFID", "Edita"], ["ORWE", "Oriental Weavers"],
  ["HELI", "Heliopolis Housing"], ["MASR", "Madinet Masr"], ["EMFD", "Emaar Misr"], ["CIEB", "Credit Agricole Egypt"], ["SKPC", "Sidi Kerir Petrochemicals"]];

/* ---------- backend bridge ---------- */
const ready = new Promise((res) => {
  if (window.pywebview?.api) return res();
  window.addEventListener("pywebviewready", res);
  setTimeout(() => { if (!window.pywebview) res(); }, 400); // dev server mode
});
async function api(name, ...args) {
  await ready;
  if (window.pywebview?.api) return window.pywebview.api[name](...args);
  const r = await fetch(`/api/${name}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(args) });
  return r.json();
}

/* ---------- state ---------- */
let settings = { watchlist: [], cash: 50000, risk_pct: 2, theme: "dark" };
let current = null, charts = null;
const save = (patch) => { Object.assign(settings, patch); api("save_settings", patch); };
const toast = (msg) => { const t = $("#toast"); t.textContent = msg; t.classList.remove("hidden"); clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.add("hidden"), 2600); };

/* ---------- navigation ---------- */
function go(page) {
  $$(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.page === page));
  $$(".page").forEach((p) => p.classList.toggle("active", p.id === `page-${page}`));
  if (page === "analyze" && charts) requestAnimationFrame(() => charts.fit());
  if (page === "metals" && !metalsLoaded) loadMetals();
}
$$(".nav-item").forEach((b) => b.addEventListener("click", () => go(b.dataset.page)));

/* ---------- theme ---------- */
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  $("#themeBtn").textContent = theme === "dark" ? "Light mode" : "Dark mode";
  if (charts) charts.restyle();
}
["#guideBtn", "#guideBtn2"].forEach((id) => $(id).addEventListener("click", async () => {
  const r = await api("open_guide");
  toast(r && r.online ? "Opening the online guide…" : "Opening the user guide…");
}));
$("#themeBtn").addEventListener("click", () => { const t = settings.theme === "dark" ? "light" : "dark"; save({ theme: t }); applyTheme(t); });

/* ---------- number formats ---------- */
const pct = (v, d = 1) => (v == null ? "–" : `${fmt(v, d)}%`);
const signed = (v) => { if (v == null) return "–"; if (Math.abs(v) < 0.05) return "0.0%"; return `<span class="${v > 0 ? "pos" : "neg"}">${v > 0 ? "+" : ""}${fmt(v, 1)}%</span>`; };
function big(v) {  // EGP amounts: 443.8 bn, 61.6 bn, 950 mn
  if (v == null) return "–";
  const a = Math.abs(v);
  return a >= 1e9 ? `${fmt(v / 1e9, 1)} bn` : a >= 1e6 ? `${fmt(v / 1e6, 0)} mn` : fmt(v, 0);
}
const vol = (v) => (v == null ? "–" : v >= 1e6 ? `${fmt(v / 1e6, 2)} M` : `${fmt(v / 1e3, 0)} K`);

/* ---------- ladder ---------- */
function ladder(el, active, labels = true) {
  el.innerHTML = [-3, -2, -1, 0, 1, 2, 3].map((r) =>
    `<div><div class="seg ${rcls(r)} ${r === active ? "on" : ""}"></div>${labels ? `<div class="lab">${RUNGS[r]}</div>` : ""}</div>`).join("");
}
const qcls = (lvl) => (lvl == null ? "qn" : `q${lvl}`);
const qbadge = (label, lvl, score) => `<span class="badge ${qcls(lvl)}">${esc(label || "Not rated")}${score != null ? ` · ${score}` : ""}</span>`;
const verdictChip = (v) => (v ? `<span class="vchip tone-${esc(v.tone)}" title="${esc(v.text)}">${esc(v.short)}</span>` : "");
const badge = (r, big = false) => `<span class="badge ${big ? "big" : ""} ${rcls(r)}">${esc(RUNGS[r])}</span>`;

/* ---------- analyse ---------- */
function show(id) { ["empty", "loading", "result"].forEach((x) => $(`#${x}`).classList.toggle("hidden", x !== id)); }
function showError(e, symbol) {
  const box = $("#error");
  const tips = /no price history|daily bars/i.test(e) ? "Yahoo Finance may not carry this stock. Try <b>Import CSV</b> with daily prices (date, open, high, low, close, volume)."
    : /reach Yahoo|urlopen|connection/i.test(e) ? "Check your internet connection, firewall or VPN, then try again." : "Check the code and try again.";
  box.innerHTML = `<b>Couldn't analyse ${esc(symbol || "this stock")}</b>${esc(e)}<div class="tiny" style="margin-top:6px">${tips}</div>`;
  box.classList.remove("hidden");
}
async function analyse(symbol) {
  symbol = (symbol || "").trim().toUpperCase();
  if (!symbol) return;
  go("analyze");
  $("#symbol").value = symbol;
  $("#error").classList.add("hidden");
  show("loading");
  const btn = $("#searchForm button"); btn.disabled = true;
  try { render(await api("analyze", symbol)); } catch (e) { show(current ? "result" : "empty"); showError(String(e), symbol); }
  finally { btn.disabled = false; }
}
function render(d) {
  if (!d || d.cancelled) { show(current ? "result" : "empty"); return; }
  if (d.error) { show(current ? "result" : "empty"); showError(d.error, d.symbol); return; }
  current = d;
  show("result");
  const s = d.signal;
  $("#rSym").textContent = d.symbol;
  $("#rName").textContent = d.name;
  $("#rClose").textContent = `${fmt(d.last_bar.c)} EGP`;
  $("#rDate").textContent = `Close of ${d.last_bar.d} · ${d.source}`;
  $("#rBadge").outerHTML = `<div class="badge big ${rcls(s.rung)}" id="rBadge">${esc(s.label)}</div>`;
  $("#rWhy").textContent = s.why.charAt(0).toUpperCase() + s.why.slice(1) + ".";
  ladder($("#ladder"), s.rung);
  const lv = d.levels, sup = lv.recent_90d.supports_nearest_first[0], res = lv.recent_90d.resistances_nearest_first[0];
  const stat = (k, v, sub) => `<div class="stat"><div class="k">${k}</div><div class="v">${v}</div><div class="s">${sub}</div></div>`;
  $("#stats").innerHTML =
    stat("RSI 14", fmt(d.rsi.now, 1), esc(d.rsi.zone)) +
    stat("Volume", `${fmt(d.volume_ratio, 2)}×`, "vs 20-day average") +
    stat("Support", sup ? fmt(sup) : "–", sup ? `${fmt(lv.pct_to_nearest_recent_support, 1)}% below` : "none below") +
    stat("Resistance", res ? fmt(res) : "–", res ? `${fmt(lv.pct_to_nearest_recent_resistance, 1)}% above` : "none above");
  $("#aCash").textContent = d.actions.cash;
  $("#aShare").textContent = d.actions.shareholder;
  $("#checklist").innerHTML = d.steps.map((st) => `<li>
      <span class="num">${st.n}</span><span class="name">${esc(st.name)}</span>
      <span class="reading">${esc(st.reading)}${st.note ? `<span class="note">${esc(st.note)}</span>` : ""}</span>
      ${badge(st.rung)}</li>`).join("");
  $("#nUp").innerHTML = d.next.up.map((x) => `<li>${esc(x)}</li>`).join("") || "<li class='muted'>Already fully bullish</li>";
  $("#nDown").innerHTML = d.next.down.map((x) => `<li>${esc(x)}</li>`).join("") || "<li class='muted'>Already fully bearish</li>";
  const metal = d.kind === "metal";  // no company behind a metal: hide ratios, rating and combined view
  $("#keyFigures").closest(".card").classList.toggle("hidden", metal);
  $("#fundGrid").closest(".card").classList.toggle("hidden", metal);
  $("#verdict").classList.toggle("hidden", metal);
  if (!metal) renderFundamentals(d);
  drawCharts(d);
  updatePlan();
}

function renderKeyFigures(d) {
  const f = (d.fundamentals || {}).figures || {}, close = d.last_bar.c;
  const row = (k, v, hint = "") => `<div class="kf-row"${hint ? ` title="${esc(hint)}"` : ""}><span>${k}</span><b>${v}</b></div>`;
  const lo = f.low_52w, hi = f.high_52w;
  const pos = lo != null && hi > lo ? Math.max(0, Math.min(100, ((close - lo) / (hi - lo)) * 100)) : null;
  const groups = [
    ["Valuation", [row("Market cap", `${big(f.market_cap)} EGP`), row("P/E", ratio(f.pe), "Price / earnings per share (last 12 months)"),
      row("P/B", ratio(f.pb), "Price / book value per share"), row("P/S", ratio(f.ps), "Price / sales per share"),
      row("EV / EBITDA", ratio(f.ev_ebitda)), row("EPS (12 m)", f.eps == null ? "–" : `${fmt(f.eps, 2)} EGP`), row("Dividend yield", pct(f.dividend_yield))]],
    ["Profitability", [row("Return on equity", pct(f.roe)), row("Return on assets", pct(f.roa)), row("Gross margin", pct(f.gross_margin)),
      row("Operating margin", pct(f.operating_margin)), row("Net margin", pct(f.net_margin))]],
    ["Financial health", [row("Debt / equity", ratio(f.debt_to_equity)), row("Current ratio", ratio(f.current_ratio), "Current assets / current liabilities: above 1 means short-term bills are covered"),
      row("Total debt", `${big(f.total_debt)} EGP`), row("Free cash flow", `${big(f.free_cash_flow)} EGP`)]],
    ["Growth & size", [row("Revenue (12 m)", `${big(f.revenue)} EGP`), row("Net income", `${big(f.net_income)} EGP`),
      row("Revenue growth", signed(f.revenue_growth)), row("EPS growth", signed(f.eps_growth))]],
    ["Price & risk", [row("Performance 1 M", signed(f.perf_1m)), row("Performance 3 M", signed(f.perf_3m)), row("Year to date", signed(f.perf_ytd)),
      row("Performance 1 Y", signed(f.perf_1y)), row("Beta (1 Y)", ratio(f.beta), "Above 1 = moves more than the market"),
      row("Volatility (month)", pct(f.volatility_1m)), row("Avg volume (30 d)", vol(f.avg_volume))]],
  ];
  $("#keyFigures").innerHTML = groups.map(([t, rows]) => `<div class="kf-group"><div class="kf-title">${t}</div>${rows.join("")}</div>`).join("") +
    (pos == null ? "" : `<div class="range"><div class="kf-title">52-week range</div><div class="range-bar"><span style="left:${pos}%"></span></div>
      <div class="range-ends"><span>${fmt(lo)}</span><span>Now ${fmt(close)} · ${fmt(pos, 0)}% of range</span><span>${fmt(hi)}</span></div></div>`);
  $("#kfMeta").textContent = (d.fundamentals || {}).error ? "Couldn't load company figures" : "Last 12 months of reported results · TradingView";
}

function renderFundamentals(d) {
  renderKeyFigures(d);
  const f = d.fundamentals || {}, q = f.quality || {};
  const v = $("#verdict");
  v.className = `verdict tone-${d.verdict ? d.verdict.tone : "neutral"}`;
  v.innerHTML = `<span class="k">Combined view: company + chart</span>${esc(d.verdict ? d.verdict.text : "")}`;
  $("#fundBadge").innerHTML = qbadge(q.label, q.level, q.score);
  $("#fundMeta").textContent = [f.sector, f.industry !== f.sector ? f.industry : "", f.market_cap ? `market cap ${fmt(f.market_cap / 1e9, 1)} bn EGP` : ""].filter(Boolean).join(" · ");
  $("#fundWhy").textContent = (f.error ? "Couldn't load fundamentals: " : "") + (q.why || "") + (f.bank ? " Bank: margin and debt checks don't apply to banks and are skipped." : "");
  const unit = (r) => (r.value == null ? "–" : `${fmt(r.value, r.unit === "%" ? 1 : 2)}${r.unit}`);
  const peer = (r) => { const p = (f.peers || {})[r.key]; return p ? `${p.group} median ${fmt(p.median, r.unit === "%" ? 1 : 2)}${r.unit}` : ""; };
  $("#fundGrid").innerHTML = (f.rules || []).map((r) => `<div class="metric ${r.score == null ? "qn" : `q${r.score}`}">
      <div class="t"><span>${esc(r.title)}</span><span class="chip-s">${esc(r.label)}</span></div>
      <div class="v">${unit(r)}</div><div class="w">${esc(r.why)}</div>${peer(r) ? `<div class="w">${esc(peer(r))}</div>` : ""}</div>`).join("")
    || `<div class="muted">No company data for ${esc(d.symbol)}.</div>`;
}
$("#searchForm").addEventListener("submit", (e) => { e.preventDefault(); analyse($("#symbol").value); });
$("#csvBtn").addEventListener("click", async () => {
  $("#error").classList.add("hidden");
  const d = await api("analyze_csv", $("#symbol").value.trim());
  render(d);
  if (d && !d.error && !d.cancelled) toast(`Analysed ${d.symbol} from your CSV`);
});

/* ---------- charts ---------- */
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
function chartOpts() {
  return { autoSize: true, layout: { background: { type: "solid", color: "transparent" }, textColor: css("--muted"), fontFamily: "Segoe UI, sans-serif" },
    grid: { vertLines: { color: css("--line") }, horzLines: { color: css("--line") } },
    rightPriceScale: { borderColor: css("--line") }, timeScale: { borderColor: css("--line"), rightOffset: 4 }, crosshair: { mode: 0 } };
}
function drawCharts(d) {
  const LC = window.LightweightCharts;
  if (!LC) { $("#priceChart").textContent = "Chart library failed to load."; return; }
  if (charts) charts.destroy();
  const pc = LC.createChart($("#priceChart"), chartOpts());
  const rc = LC.createChart($("#rsiChart"), { ...chartOpts(), timeScale: { ...chartOpts().timeScale, visible: false } });
  const candles = pc.addCandlestickSeries({ upColor: css("--r2"), downColor: css("--rm3"), wickUpColor: css("--r2"), wickDownColor: css("--rm3"), borderVisible: false });
  candles.setData(d.chart.candles);
  candles.priceScale().applyOptions({ scaleMargins: { top: 0.06, bottom: 0.24 } });
  const vol = pc.addHistogramSeries({ priceScaleId: "", priceFormat: { type: "volume" }, lastValueVisible: false, priceLineVisible: false });
  vol.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
  const volData = () => d.chart.volume.map((v) => ({ time: v.time, value: v.value, color: v.up ? css("--r2") + "55" : css("--rm3") + "55" }));
  vol.setData(volData());
  const line = (key, color) => { const s = pc.addLineSeries({ color, lineWidth: 2, priceLineVisible: false, lastValueVisible: false, crosshairMarkerVisible: false }); s.setData(d.chart[key]); return s; };
  const mas = { ma5: line("ma5", css("--ma5")), ma9: line("ma9", css("--ma9")), ma18: line("ma18", css("--ma18")) };

  const lv = d.levels.recent_90d;
  let lines = [];
  const drawLevels = (on) => {
    lines.forEach((l) => candles.removePriceLine(l)); lines = [];
    if (!on) return;
    lv.supports_nearest_first.slice(0, 2).forEach((p, i) => lines.push(candles.createPriceLine({ price: p, color: css("--sup"), lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: `S${i + 1}` })));
    lv.resistances_nearest_first.slice(0, 2).forEach((p, i) => lines.push(candles.createPriceLine({ price: p, color: css("--res"), lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: `R${i + 1}` })));
  };
  const markers = d.chart.swings.map((s) => ({ time: s.time, position: s.type === "H" ? "aboveBar" : "belowBar",
    color: s.type === "H" ? css("--res") : css("--sup"), shape: s.type === "H" ? "arrowDown" : "arrowUp", size: 0.7 }))
    .sort((a, b) => (a.time < b.time ? -1 : 1));
  const drawSwings = (on) => candles.setMarkers(on ? markers : []);

  // RSI: pad with blank points so both charts share bar indexes and scroll together
  const rsiMap = new Map(d.chart.rsi.map((p) => [p.time, p.value]));
  const rsi = rc.addLineSeries({ color: css("--accent-2"), lineWidth: 2, priceLineVisible: false });
  rsi.setData(d.chart.candles.map((c) => (rsiMap.has(c.time) ? { time: c.time, value: rsiMap.get(c.time) } : { time: c.time })));
  [[70, css("--rm3")], [50, css("--muted")], [30, css("--r2")]].forEach(([p, c]) => rsi.createPriceLine({ price: p, color: c, lineWidth: 1, lineStyle: 2, axisLabelVisible: true, title: "" }));
  rsi.priceScale().applyOptions({ autoScale: false, scaleMargins: { top: 0.1, bottom: 0.1 } });
  rsi.applyOptions({ autoscaleInfoProvider: () => ({ priceRange: { minValue: 0, maxValue: 100 } }) });

  let syncing = false;
  const sync = (from, to) => from.timeScale().subscribeVisibleLogicalRangeChange((r) => { if (syncing || !r) return; syncing = true; to.timeScale().setVisibleLogicalRange(r); syncing = false; });
  sync(pc, rc); sync(rc, pc);

  const state = { ma5: true, ma9: true, ma18: true, levels: true, swings: true };
  $$("#toggles input").forEach((cb) => { cb.checked = state[cb.dataset.layer]; });
  const apply = () => {
    Object.entries(mas).forEach(([k, s]) => s.applyOptions({ visible: state[k] }));
    drawLevels(state.levels); drawSwings(state.swings);
  };
  apply();
  const fit = () => { const n = d.chart.candles.length; pc.timeScale().setVisibleLogicalRange({ from: Math.max(0, n - 130), to: n + 3 }); };
  fit();
  charts = {
    fit,
    toggle: (k, v) => { state[k] = v; apply(); },
    restyle: () => {
      [pc, rc].forEach((c) => c.applyOptions(chartOpts())); rc.applyOptions({ timeScale: { visible: false } });
      candles.applyOptions({ upColor: css("--r2"), downColor: css("--rm3"), wickUpColor: css("--r2"), wickDownColor: css("--rm3") });
      mas.ma5.applyOptions({ color: css("--ma5") }); mas.ma9.applyOptions({ color: css("--ma9") }); mas.ma18.applyOptions({ color: css("--ma18") });
      vol.setData(volData()); apply();
    },
    destroy: () => { pc.remove(); rc.remove(); },
  };
}
$$("#toggles input").forEach((cb) => cb.addEventListener("change", () => charts && charts.toggle(cb.dataset.layer, cb.checked)));

/* ---------- trade plan ---------- */
let planTimer;
async function updatePlan() {
  if (!current) return;
  const cash = $("#cash").value, risk = $("#risk").value;
  const p = await api("plan", current.symbol, cash, risk);
  const box = $("#plan");
  if (p.error) { box.innerHTML = `<div class="warn">${esc(p.error)}</div>`; return; }
  const rows = [["Entry (last close)", `${fmt(p.entry)} EGP`], ["Stop (below support)", `${fmt(p.stop)} EGP`],
    [current.kind === "metal" ? "Risk per gram" : "Risk per share", `${fmt(p.risk_per_share)} (${fmt(p.risk_pct, 1)}%)`], ["Target (2R)", `${fmt(p.target)} EGP`]];
  if (p.first_resistance) rows.push(["First resistance", `${fmt(p.first_resistance)} EGP`]);
  if (p.shares != null) rows.push([current.kind === "metal" ? "Grams" : "Shares", fmt(p.shares, 0)], ["Cost", `${fmt(p.cost, 0)} EGP`], ["Loss if stopped", `${fmt(p.loss_at_stop, 0)} EGP (${fmt(p.loss_pct_of_cash, 1)}%)`]);
  const note = current.signal.rung < 2 ? "<div class='warn'>The signal isn't a First or Confirm Buy: treat this as a plan to have ready, not a trade for today.</div>" : "";
  box.innerHTML = `<dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>${(p.warnings || []).map((w) => `<div class="warn">${esc(w)}</div>`).join("")}${note}`;
}
["#cash", "#risk"].forEach((id) => $(id).addEventListener("input", () => {
  clearTimeout(planTimer);
  planTimer = setTimeout(() => { save({ cash: Number($("#cash").value) || 0, risk_pct: Number($("#risk").value) || 2 }); updatePlan(); }, 300);
}));

/* ---------- watchlist ---------- */
function drawChips() {
  $("#wChips").innerHTML = settings.watchlist.map((s) => `<span class="chip">${esc(s)}<button class="x" data-del="${esc(s)}" aria-label="Remove ${esc(s)}">✕</button></span>`).join("");
  $("#quick").innerHTML = settings.watchlist.map((s) => `<button class="chip" data-go="${esc(s)}">${esc(s)}</button>`).join("");
}
document.addEventListener("click", (e) => {
  const del = e.target.closest("[data-del]"), gotoBtn = e.target.closest("[data-go]"), link = e.target.closest("[data-url]");
  if (del) { save({ watchlist: settings.watchlist.filter((s) => s !== del.dataset.del) }); drawChips(); }
  if (gotoBtn) analyse(gotoBtn.dataset.go);
  if (link) { e.preventDefault(); api("open_url", link.dataset.url); }
});
$("#addForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const s = $("#addSym").value.trim().toUpperCase();
  if (!/^[A-Z0-9]{2,6}$/.test(s)) return toast("Enter an EGX code such as COMI");
  if (!settings.watchlist.includes(s)) save({ watchlist: [...settings.watchlist, s] });
  $("#addSym").value = ""; drawChips();
});
$("#scanBtn").addEventListener("click", async () => {
  const btn = $("#scanBtn"), body = $("#wTable tbody");
  if (!settings.watchlist.length) return toast("Add a stock first");
  btn.disabled = true; btn.textContent = "Scanning…";
  body.innerHTML = `<tr><td colspan="14" class="muted center">Checking ${settings.watchlist.length} stocks…</td></tr>`;
  try {
    const rows = await api("scan", settings.watchlist);
    rows.sort((a, b) => (b.rung ?? -9) - (a.rung ?? -9) || (b.quality_score ?? -1) - (a.quality_score ?? -1));
    fillTable("#wTable", rows);
  } finally { btn.disabled = false; btn.textContent = "Scan all"; }
});
const ratio = (v) => (v == null ? "–" : fmt(v, 2));
function resultRow(r) {
  if (r.error) return `<tr><td><b>${esc(r.symbol)}</b></td><td colspan="13" class="why">${esc(r.error)}</td></tr>`;
  return `<tr class="click" data-go="${esc(r.symbol)}" tabindex="0" title="${esc(r.verdict ? r.verdict.text : "")}">
    <td><b>${esc(r.symbol)}</b><div class="muted tiny ellipsis">${esc(r.name)}</div></td>
    <td class="num">${fmt(r.close)}<div class="muted tiny">${esc(r.date)}</div></td><td>${badge(r.rung)}</td>
    <td>${qbadge(r.quality, r.quality_level, r.quality_score)}</td>
    <td class="num">${ratio(r.pe)}</td><td class="num">${ratio(r.pb)}</td><td class="num">${pct(r.roe)}</td><td class="num">${pct(r.net_margin)}</td>
    <td class="num">${ratio(r.debt_to_equity)}</td><td class="num">${signed(r.eps_growth)}</td><td class="num">${pct(r.dividend_yield)}</td>
    <td class="num">${big(r.market_cap)}</td><td class="num">${signed(r.perf_ytd)}</td><td>${verdictChip(r.verdict)}</td></tr>`;
}
// Tables keep their rows so a header click can re-sort them; missing values always sort last
const tableRows = {};
function fillTable(id, rows) { tableRows[id] = rows; $(`${id} tbody`).innerHTML = rows.map(resultRow).join(""); }
$$("th[data-sort]").forEach((th) => th.addEventListener("click", () => {
  const table = th.closest("table"), id = `#${table.id}`, key = th.dataset.sort, rows = tableRows[id];
  if (!rows || !rows.length) return;
  const dir = th.dataset.dir === "desc" ? "asc" : "desc";
  $$("th", table).forEach((h) => { delete h.dataset.dir; }); th.dataset.dir = dir;
  const val = (r) => (key === "verdict" ? r.verdict && r.verdict.short : r[key]);
  fillTable(id, [...rows].sort((a, b) => {
    const x = val(a), y = val(b);
    if (x == null || y == null) return (x == null) - (y == null);
    return (typeof x === "string" ? x.localeCompare(y) : x - y) * (dir === "asc" ? 1 : -1);
  }));
}));

/* ---------- screener ---------- */
async function loadSectors() {
  const s = await api("sectors");
  if (Array.isArray(s)) $("#fSector").innerHTML = `<option value="">All sectors</option>` + s.map((x) => `<option>${esc(x)}</option>`).join("");
}
$("#runScreener").addEventListener("click", async () => {
  const btn = $("#runScreener"), body = $("#sTable tbody");
  btn.disabled = true; btn.textContent = "Screening…";
  body.innerHTML = `<tr><td colspan="14" class="muted center">Rating every EGX company, then checking the best ones with your course method…</td></tr>`;
  $("#sSummary").textContent = "";
  try {
    const r = await api("screener", Number($("#fQuality").value), Number($("#fSignal").value), $("#fSector").value);
    if (r.error) { body.innerHTML = `<tr><td colspan="14" class="why">${esc(r.error)}</td></tr>`; return; }
    $("#sSummary").textContent = `Rated ${r.rated} companies · ${r.passed_quality} met the quality filter · checked the top ${r.checked} with the course checklist` +
      (r.skipped_no_prices ? ` · ${r.skipped_no_prices} skipped (no price history)` : "") + ` · ${r.results.length} match. Click a column header to sort.`;
    fillTable("#sTable", r.results);
    if (!r.results.length) body.innerHTML = `<tr><td colspan="14" class="muted center">No company matches right now. Try "Strong or Fair" or "Any buy, including Alarm Buy".</td></tr>`;
  } finally { btn.disabled = false; btn.textContent = "Run screener"; }
});
$("#sTable").addEventListener("keydown", (e) => { const tr = e.target.closest("tr[data-go]"); if (tr && e.key === "Enter") analyse(tr.dataset.go); });
$("#wTable").addEventListener("keydown", (e) => { const tr = e.target.closest("tr[data-go]"); if (tr && e.key === "Enter") analyse(tr.dataset.go); });

/* ---------- start ---------- */
(async function init() {
  $("#symbols").innerHTML = SUGGEST.map(([c, n]) => `<option value="${c}">${esc(n)}</option>`).join("");
  ladder($("#ladderLegend"), 99);
  settings = { ...settings, ...(await api("get_settings")) };
  const info = await api("info");
  $("#version").textContent = `Version ${info.version}`;
  $("#aboutInfo").textContent = `Version ${info.version}. Your settings are saved in ${info.data_dir}.`;
  $("#cash").value = settings.cash; $("#risk").value = settings.risk_pct;
  // Deep links (used for the guide's screenshots): #a=COMI, #p=watchlist&scan, #p=about, &theme=light, &role=shareholder
  const h = new URLSearchParams(location.hash.slice(1));
  applyTheme(h.get("theme") || settings.theme); drawChips();
  if (h.get("a")) analyse(h.get("a"));
  else if (h.get("p")) { go(h.get("p")); if (h.has("scan")) $("#scanBtn").click(); if (h.has("run")) $("#runScreener").click(); }
  loadSectors();
  $("#symbol").focus();
})();

/* ---------- gold & silver ---------- */
let metalsLoaded = false;
async function loadMetals() {
  metalsLoaded = true;
  const err = $("#metalsError"); err.classList.add("hidden");
  const m = await api("metals");
  if (!m || m.error) { err.innerHTML = `<b>Couldn't load prices</b>${esc(m ? m.error : "")}`; err.classList.remove("hidden"); metalsLoaded = false; return; }
  const g = m.gold, s = m.silver;
  const buttons = (code) => `<div class="btn-row"><button class="primary small" data-go="${code}">Analyze with my course method</button>
    <button class="ghost small" data-watch="${code}">Add to watchlist</button></div>`;
  const card = (cls, title, x, body) => `<div class="card metal">
      <div class="metal-top"><div class="metal-name"><i class="metal-dot ${cls}"></i>${title}</div><span class="muted tiny">${esc(x.date)}</span></div>${body}
      <div class="kf-row"><span>Per ounce</span><b>$${fmt(x.usd_oz)} · ${fmt(x.egp_oz, 0)} EGP</b></div>
      <div class="kf-row"><span>Change today (USD)</span><b>${signed(x.change_usd)}</b></div>
      <div class="kf-row"><span>1 year (USD)</span><b>${signed(x.perf_1y_usd)}</b></div>
      <div class="kf-row"><span>52-week range (USD/oz)</span><b>${fmt(x.low_52w_usd)} – ${fmt(x.high_52w_usd)}</b></div>`;
  const ratioPos = Math.max(0, Math.min(100, ((m.gold_silver_ratio - 40) / (120 - 40)) * 100));
  $("#metalsGrid").innerHTML =
    card("gold", "Gold", g, `<div><div class="muted tiny">24k, per gram</div><div class="metal-big">${fmt(g.karats["24k"])} EGP</div></div>
      <div class="karats">${["24k", "21k", "18k"].map((k) => `<div class="karat"><div class="k">${k}</div><div class="v">${fmt(g.karats[k], 0)}</div></div>`).join("")}</div>`) + buttons("GOLD") + `</div>` +
    card("silver", "Silver", s, `<div><div class="muted tiny">999, per gram</div><div class="metal-big">${fmt(s.egp_gram)} EGP</div></div>`) + buttons("SILVER") + `</div>` +
    `<div class="card metal"><div class="metal-name">Market</div>
      <div><div class="muted tiny">US dollar, official rate</div><div class="metal-big">${fmt(m.usd_egp)} EGP</div><div class="muted tiny">${signed(m.usd_egp_change)} today · ${esc(m.fx_date)}</div></div>
      <div><div class="kf-title">Gold / silver ratio</div><div class="metal-big">${fmt(m.gold_silver_ratio, 1)}</div>
      <div class="ratio-bar"><span style="left:${ratioPos}%"></span></div><div class="range-ends"><span>40 · gold cheap</span><span>120 · silver cheap</span></div>
      <p class="muted tiny">How many ounces of silver one ounce of gold buys. Above about 80, silver is cheap compared with gold; below about 50, gold is.</p></div></div>`;
  $("#metalsNote").textContent = `${m.source}. These are international prices: Egyptian shop prices for jewellery and bars add a local premium and workmanship fees. Not investment advice.`;
}
$("#metalsRefresh").addEventListener("click", () => { metalsLoaded = false; $("#metalsGrid").innerHTML = '<div class="card skeleton h160"></div>'.repeat(3); loadMetals(); });
document.addEventListener("click", (e) => {
  const w = e.target.closest("[data-watch]");
  if (!w) return;
  if (!settings.watchlist.includes(w.dataset.watch)) { save({ watchlist: [...settings.watchlist, w.dataset.watch] }); drawChips(); }
  toast(`${w.dataset.watch} is on your watchlist`);
});
