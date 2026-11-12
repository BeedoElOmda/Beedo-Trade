/* Beedo-Trade UI. Talks to Python through pywebview (desktop) or /api (dev server). */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n, d = 2) => (n == null || isNaN(n) ? "–" : Number(n).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }));
const RUNGS = { 3: "Confirm Buy", 2: "First Buy", 1: "Alarm Buy", 0: "Hold", "-1": "Alarm Sell", "-2": "First Sell", "-3": "Confirm Sell" };
const rcls = (r) => (r >= 0 ? `r${r}` : `rm${-r}`);
const SUGGEST = [["COMI", "Commercial International Bank"], ["TMGH", "Talaat Moustafa Group"], ["SWDY", "Elsewedy Electric"],
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
let settings = { watchlist: [], cash: 50000, risk_pct: 2, role: "cash", theme: "dark" };
let current = null, charts = null;
const save = (patch) => { Object.assign(settings, patch); api("save_settings", patch); };
const toast = (msg) => { const t = $("#toast"); t.textContent = msg; t.classList.remove("hidden"); clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.add("hidden"), 2600); };

/* ---------- navigation ---------- */
function go(page) {
  $$(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.page === page));
  $$(".page").forEach((p) => p.classList.toggle("active", p.id === `page-${page}`));
  if (page === "analyze" && charts) requestAnimationFrame(() => charts.fit());
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

/* ---------- role ---------- */
function applyRole(role) {
  $$(".segmented button").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.role === role)));
  $$(".actions .action").forEach((a) => a.classList.toggle("mine", a.dataset.role === role));
}
$$(".segmented button").forEach((b) => b.addEventListener("click", () => { save({ role: b.dataset.role }); applyRole(b.dataset.role); }));

/* ---------- ladder ---------- */
function ladder(el, active, labels = true) {
  el.innerHTML = [-3, -2, -1, 0, 1, 2, 3].map((r) =>
    `<div><div class="seg ${rcls(r)} ${r === active ? "on" : ""}"></div>${labels ? `<div class="lab">${RUNGS[r]}</div>` : ""}</div>`).join("");
}
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
  applyRole(settings.role);
  $("#checklist").innerHTML = d.steps.map((st) => `<li>
      <span class="num">${st.n}</span><span class="name">${esc(st.name)}</span>
      <span class="reading">${esc(st.reading)}${st.note ? `<span class="note">${esc(st.note)}</span>` : ""}</span>
      ${badge(st.rung)}</li>`).join("");
  $("#nUp").innerHTML = d.next.up.map((x) => `<li>${esc(x)}</li>`).join("") || "<li class='muted'>Already fully bullish</li>";
  $("#nDown").innerHTML = d.next.down.map((x) => `<li>${esc(x)}</li>`).join("") || "<li class='muted'>Already fully bearish</li>";
  drawCharts(d);
  updatePlan();
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
    ["Risk per share", `${fmt(p.risk_per_share)} (${fmt(p.risk_pct, 1)}%)`], ["Target (2R)", `${fmt(p.target)} EGP`]];
  if (p.first_resistance) rows.push(["First resistance", `${fmt(p.first_resistance)} EGP`]);
  if (p.shares != null) rows.push(["Shares", fmt(p.shares, 0)], ["Cost", `${fmt(p.cost, 0)} EGP`], ["Loss if stopped", `${fmt(p.loss_at_stop, 0)} EGP (${fmt(p.loss_pct_of_cash, 1)}%)`]);
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
  body.innerHTML = `<tr><td colspan="6" class="muted center">Checking ${settings.watchlist.length} stocks…</td></tr>`;
  try {
    const rows = await api("scan", settings.watchlist);
    rows.sort((a, b) => (b.rung ?? -9) - (a.rung ?? -9));
    body.innerHTML = rows.map((r) => r.error
      ? `<tr><td><b>${esc(r.symbol)}</b></td><td colspan="5" class="why">${esc(r.error)}</td></tr>`
      : `<tr class="click" data-go="${esc(r.symbol)}" tabindex="0"><td><b>${esc(r.symbol)}</b><div class="muted tiny">${esc(r.name)}</div></td>
         <td class="num">${fmt(r.close)}<div class="muted tiny">${esc(r.date)}</div></td><td>${badge(r.rung)}</td>
         <td class="num">${fmt(r.rsi, 1)}</td><td class="why">${esc(r.ma)}</td><td class="why">${esc(r.why)}</td></tr>`).join("");
  } finally { btn.disabled = false; btn.textContent = "Scan all"; }
});
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
  applyTheme(h.get("theme") || settings.theme); applyRole(h.get("role") || settings.role); drawChips();
  if (h.get("a")) analyse(h.get("a"));
  else if (h.get("p")) { go(h.get("p")); if (h.has("scan")) $("#scanBtn").click(); }
  $("#symbol").focus();
})();
