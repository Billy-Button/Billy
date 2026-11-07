import base64, pathlib, html as H
icon = open("/home/claude/wp/icon_b64.txt").read()
logo = open("/home/claude/wp/logo_b64.txt").read()

F = pathlib.Path("/home/claude/wp/fonts")
fred = base64.b64encode((F / "Fredoka-sub.ttf").read_bytes()).decode()
nun = base64.b64encode((F / "Nunito-sub.ttf").read_bytes()).decode()

SAGE, EARTH, SKY, INK, YEL = "#6E8B57", "#A45823", "#5E80A0", "#2B2320", "#FDC546"
W = 300  # svg width units
FX, TX = 96, 262  # x of forecast tick and target tick
LEFT, RIGHT = 10, 290


def pos(v, f, t, higher_better):
    """x position of value v on a bar from forecast f to target t."""
    if t is None:
        # no target: forecast at centre-ish, one forecast-unit = 60 units, direction by higher_better
        unit = (f if f else 1.0)
        x = FX + ((v - f) / unit) * 90 * (1 if higher_better else -1)
    else:
        if t == f:
            return FX
        x = FX + (v - f) / (t - f) * (TX - FX)
    return max(LEFT, min(RIGHT, x))


def bar(this, last, fcst, target, higher_better, fmt, fcst_lbl, target_lbl, last_lbl):
    xf = FX
    xt = TX if target is not None else None
    xv = pos(this, fcst, target, higher_better)
    xl = pos(last, fcst, target, higher_better) if last is not None else None
    # improving if moving from forecast in the direction of target (or of "better" when no target)
    if target is not None:
        improving = (this - fcst) * (target - fcst) > 0
    else:
        improving = (this - fcst) > 0 if higher_better else (this - fcst) < 0
    on_fcst = abs(this - fcst) < 1e-9
    fill = SAGE if improving else EARTH
    x1, x2 = sorted([xf, xv])
    parts = []
    # track
    parts.append(f'<line x1="{LEFT}" y1="22" x2="{RIGHT}" y2="22" stroke="rgba(43,35,32,.14)" stroke-width="6" stroke-linecap="round"/>')
    if xt is not None:
        parts.append(f'<line x1="{xf}" y1="22" x2="{xt}" y2="22" stroke="rgba(43,35,32,.22)" stroke-width="6" stroke-linecap="round"/>')
    # progress fill
    if not on_fcst:
        parts.append(f'<line x1="{x1}" y1="22" x2="{x2}" y2="22" stroke="{fill}" stroke-width="6" stroke-linecap="round"/>')
    # forecast tick
    parts.append(f'<line x1="{xf}" y1="12" x2="{xf}" y2="32" stroke="{INK}" stroke-width="2"/>')
    parts.append(f'<text x="{xf}" y="43" text-anchor="middle" class="tk">{fcst_lbl}</text>')
    # target tick
    if xt is not None:
        parts.append(f'<line x1="{xt}" y1="12" x2="{xt}" y2="32" stroke="{INK}" stroke-width="2"/>')
        parts.append(f'<text x="{xt}" y="43" text-anchor="middle" class="tk">{target_lbl}</text>')
    else:
        parts.append(f'<line x1="{TX}" y1="12" x2="{TX}" y2="32" stroke="rgba(43,35,32,.25)" stroke-width="2" stroke-dasharray="3 3"/>')
        parts.append(f'<text x="{TX}" y="43" text-anchor="middle" class="tk tbc">{target_lbl or "none yet"}</text>')
    # last week hollow marker
    if xl is not None:
        parts.append(f'<circle cx="{xl}" cy="22" r="5.5" fill="#FBF6EE" stroke="{INK}" stroke-width="1.6" opacity=".7"/>')
        parts.append(f'<text x="{xl}" y="7" text-anchor="middle" class="tk">{last_lbl}</text>')
    # this week marker
    parts.append(f'<circle cx="{xv}" cy="22" r="8" fill="{fill if not on_fcst else SKY}" stroke="#FBF6EE" stroke-width="2.5"/>')
    return f'<svg viewBox="0 0 {W} 50" class="bar" role="img">{"".join(parts)}</svg>'


def row(label, unit, this_txt, this_sub, b, prov=False):
    p = '<span class="prov">partial</span>' if prov else ""
    return f"""
      <li class="m">
        <div class="m-top"><span class="m-label">{label}</span>{p}<span class="m-unit">{unit}</span></div>
        <div class="m-body">
          <div class="num"><div class="big">{this_txt}</div><div class="s">{this_sub}</div></div>
          {b}
        </div>
      </li>"""


def fmt(v, neg):
    return f'<span class="neg">({v})</span>' if neg and v not in (0, "0") else str(v)


def profile_row(label, unit, total, total_sub, months, change, neg=False):
    """months: list of (label, this, last)"""
    cells = "".join(f'<div class="pm"><div class="pm-k">{m}</div><div class="pm-v">{fmt(t, neg)}</div><div class="pm-l">last wk {fmt(l, neg)}</div></div>' for m, t, l in months)
    total = fmt(total, neg)
    return f"""
      <li class="m">
        <div class="m-top"><span class="m-label">{label}</span><span class="m-unit">{unit}</span></div>
        <div class="m-body">
          <div class="num"><div class="big">{total}</div><div class="s">{total_sub}</div></div>
          <div class="prof">{cells}</div>
        </div>
        <div class="pm-chg">{change}</div>
      </li>"""


def centre(idx, name, places, rows):
    return f"""
    <section class="centre">
      <header class="c-head"><span class="c-idx">{idx}</span><h2>{name}</h2><span class="c-places">{places} licensed places</span></header>
      <div class="cols"><div class="num"><span class="k">This week</span></div><svg viewBox="0 0 300 14" class="bar"><text x="{FX}" y="11" text-anchor="middle" class="hd">Forecast</text><text x="{TX}" y="11" text-anchor="middle" class="hd">Target</text></svg></div>
      <ul class="measures">{''.join(rows)}</ul>
    </section>"""



# ============================================================
# WEEK'S FIGURES — the only part that changes each issue
# ============================================================
ISSUE = "2.1"
WEEK_LABEL = "6 Nov 26"                 # Friday that closes the week
SNAPSHOT = "Sat 7 Nov 26, 3:06 am AEDT"  # dashboard build the figures come from
FORECAST_WINDOW = "weeks of 3 Aug to 26 Oct"
LASTWEEK_ASOF = "Fri 30 Oct"

# bar(this, last, forecast, target, higher_is_better, unit, forecast_label, target_label, last_label)
DATA = {
 "South Morang": {"places": 108, "rows": [
  ("bar", "Occupancy", "no casual days", "79%", "424 spots", (78.5, 78.9, 76.4, 85, True, "%", "76%", "85%", "79%")),
  ("bar", "Enquiries", "families", "4", "last week 4", (4, 4, 4.3, 7, True, "", "4.3", "7", "4")),
  ("bar", "Tours completed", "families", "1", "last week 4", (1, 4, 4.2, 5.5, True, "", "4.2", "5–6", "4")),
  ("bar", "New enrolments", "children into Owna this week", "2", "last week 2", (2, 2, 1.2, 2.5, True, "", "1.2", "2–3", "2")),
  ("bar", "Lost spots", "spots a week · excludes school leavers", "7", "2 children", (7, 3, 2.4, 2.1, False, "", "2.4", "2.1", "3")),
  ("prof", "$50 deposit paid", "families · not yet enrolled · start month given", 2, "",
      [("Overdue", 0, "—"), ("Nov–Dec", 0, "—"), ("Jan–Feb", 1, "—"), ("Later / none", 1, "—")],
      "Last week 3", False),
  ("prof", "Enrolled, due to start", "children · by start month", 5, "",
      [("Nov", 2, 2), ("Dec", 1, 1), ("Jan", 1, 0), ("Feb+", 1, 0)], "Last week 3", False),
  ("prof", "School leavers", "children · starting school 2027", 33, "102 spots",
      [("Nov", 1, 2), ("Dec", 3, 3), ("Jan–Feb", 1, 1), ("No date", 28, 28)],
      "Forecast: all 33 gone by end Jan · 28 have no date in Owna", True),
 ]},
 "Craigieburn": {"places": 174, "rows": [
  ("bar", "Occupancy", "no casual days", "35%", "301 spots", (34.6, 34.0, 32.8, 70, True, "%", "33%", "70%", "34%")),
  ("bar", "Enquiries", "families", "5", "last week 5", (5, 5, 7.7, 35, True, "", "7.7", "35", "5")),
  ("bar", "Tours completed", "families", "5", "last week 4", (5, 4, 5.8, 23, True, "", "5.8", "23", "4")),
  ("bar", "New enrolments", "children into Owna this week", "0", "last week 6", (0, 6, 2.2, 11, True, "", "2.2", "11", "6")),
  ("bar", "Lost spots", "spots a week · excludes school leavers", "0", "none", (0, 4, 3.8, 2.1, False, "", "3.8", "2.1", "4")),
  ("prof", "$50 deposit paid", "families · not yet enrolled · start month given", 22, "",
      [("Overdue", 5, "—"), ("Nov–Dec", 4, "—"), ("Jan–Feb", 8, "—"), ("Later / none", 5, "—")],
      "Last week 20", False),
  ("prof", "Enrolled, due to start", "children · by start month", 5, "",
      [("Nov", 2, 5), ("Dec", 1, 1), ("Jan", 0, 0), ("Feb+", 2, 2)], "Last week 8", False),
  ("prof", "School leavers", "children · starting school 2027", 22, "79 spots",
      [("Nov", 1, 1), ("Dec", 0, 0), ("Jan–Feb", 0, 0), ("No date", 21, 21)],
      "Forecast: all 22 gone by end Jan · 21 have no date in Owna", True),
 ]},
}
# ============================================================

def build_rows(rows):
    out = []
    for r in rows:
        if r[0] == "bar":
            _, label, unit, big, sub, args = r
            out.append(row(label, unit, big, sub, bar(*args)))
        else:
            _, label, unit, total, sub, months, change, neg = r
            out.append(profile_row(label, unit, total, sub, months, change, neg=neg))
    return out

sm = centre(1, "South Morang", DATA["South Morang"]["places"], build_rows(DATA["South Morang"]["rows"]))
cb = centre(2, "Craigieburn", DATA["Craigieburn"]["places"], build_rows(DATA["Craigieburn"]["rows"]))

html = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#FDC546">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Billy">
<link rel="apple-touch-icon" href="data:image/png;base64,{icon}">
<link rel="icon" href="data:image/png;base64,{icon}">
<title>Billy · Friday Night Report</title>
<style>
@font-face {{ font-family: "Fredoka"; src: url(data:font/ttf;base64,{fred}) format("truetype"); font-weight: 300 700; font-display: swap; }}
@font-face {{ font-family: "Nunito";  src: url(data:font/ttf;base64,{nun}) format("truetype"); font-weight: 200 1000; font-display: swap; }}
:root {{ --yellow:#FDC546; --earth:#A45823; --sky:#5E80A0; --sage:#6E8B57; --ink:#2B2320; --cream:#FBF6EE;
  --ink-70:rgba(43,35,32,.72); --ink-50:rgba(43,35,32,.52); --ink-12:rgba(43,35,32,.12); --ink-06:rgba(43,35,32,.06); }}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; padding:0; background:var(--cream); color:var(--ink); }}
body {{ font-family:"Nunito",system-ui,-apple-system,"Segoe UI",sans-serif; font-size:14px; line-height:1.35; -webkit-font-smoothing:antialiased; -webkit-text-size-adjust:100%; }}
h1, h2, .big, .c-idx {{ font-family:"Fredoka","Nunito",sans-serif; font-weight:600; letter-spacing:-0.005em; }}
.page {{ max-width:430px; margin:0 auto; }}
.band {{ background:var(--yellow); padding:14px 18px 12px; display:flex; align-items:center; gap:14px; }}
.logo {{ width:84px; height:auto; flex:0 0 auto; }}
.ttl {{ min-width:0; }}
.sub {{ font-size:12.5px; font-weight:700; color:var(--earth); margin-top:5px; white-space:nowrap; }}
h1 {{ margin:0; font-size:25px; line-height:1.05; white-space:nowrap; }}
.brand {{ font-family:"Fredoka",sans-serif; font-weight:600; font-size:11px; letter-spacing:.12em; text-transform:uppercase; color:var(--earth); margin-bottom:4px; }}
.meta {{ font-size:10.5px; font-weight:700; color:var(--earth); opacity:.85; margin-top:2px; }}
.byline {{ display:flex; justify-content:space-between; align-items:baseline; padding:10px 18px 0; font-size:13px; font-weight:700; color:var(--ink); white-space:nowrap; }}
.byline .meta {{ color:var(--ink-50); }}
.toggle {{ position:sticky; top:0; z-index:5; display:flex; gap:6px; padding:10px 18px; background:var(--cream); border-bottom:1px solid var(--ink-12); }}
.toggle button {{ flex:1 1 0; font:inherit; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; padding:10px 8px; border-radius:999px; border:2px solid var(--earth); background:transparent; color:var(--earth); cursor:pointer; -webkit-tap-highlight-color:transparent; }}
.toggle button[aria-selected="true"] {{ background:var(--earth); color:var(--cream); }}
.screen[hidden] {{ display:none; }}
.foot summary {{ cursor:pointer; font-weight:800; color:var(--ink); }}
.foot p {{ margin:6px 0 0; }}
.ctx {{ padding:8px 18px 0; font-size:12px; color:var(--ink-70); line-height:1.4; }}
.ctx b {{ color:var(--ink); }}
.legend {{ display:flex; gap:10px 12px; flex-wrap:nowrap; white-space:nowrap; padding:12px 16px 2px; font-size:12.5px; font-weight:700; color:var(--ink-70); }}
.legend span {{ display:inline-flex; align-items:center; gap:5px; }}
.dot {{ width:16px; height:16px; border-radius:50%; display:inline-block; }}
.ring {{ background:transparent; border:1.8px solid var(--ink); opacity:.7; width:13px; height:13px; }}
.centre {{ padding:12px 18px 2px; }}
.c-head {{ display:flex; align-items:center; gap:8px; padding-bottom:6px; border-bottom:2px solid var(--earth); }}
.c-idx {{ width:22px; height:22px; border-radius:50%; background:var(--earth); color:var(--cream); font-size:12px; display:inline-flex; align-items:center; justify-content:center; }}
h2 {{ margin:0; font-size:20px; line-height:1; }}
.c-places {{ margin-left:auto; font-size:10.5px; color:var(--ink-50); font-weight:700; text-align:right; }}
.measures {{ list-style:none; margin:0; padding:0; }}
.m {{ padding:8px 0 4px; border-bottom:1px solid var(--ink-12); }}
.m:last-child {{ border-bottom:0; }}
.m-top {{ display:flex; align-items:baseline; gap:8px; }}
.m-label {{ font-size:14px; font-weight:800; }}
.m-unit {{ font-size:11px; color:var(--ink-50); margin-left:auto; text-align:right; white-space:nowrap; }}
.prov {{ font-size:9.5px; font-weight:800; text-transform:uppercase; letter-spacing:.06em; color:var(--earth); border:1px solid var(--earth); border-radius:4px; padding:0 4px; }}
.m-body {{ display:flex; align-items:center; gap:10px; margin-top:2px; }}
.num {{ flex:0 0 78px; }}
.big {{ font-size:34px; line-height:1; font-variant-numeric:tabular-nums; }}
.s {{ font-size:10.5px; color:var(--ink-70); margin-top:2px; line-height:1.2; white-space:nowrap; }}
.bar {{ flex:1 1 0; min-width:0; width:100%; height:auto; display:block; overflow:visible; }}
.cols {{ display:flex; align-items:center; gap:10px; padding:6px 0 0; }}
.cols .k {{ font-size:9.5px; font-weight:800; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-50); }}
.hd {{ font-family:"Nunito",sans-serif; font-size:9.5px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; fill:rgba(43,35,32,.55); }}
.hd-l {{ text-transform:none; letter-spacing:0; font-weight:700; }}
.tk {{ font-family:"Nunito",sans-serif; font-size:9.5px; font-weight:700; fill:rgba(43,35,32,.62); }}
.tbc {{ fill:rgba(43,35,32,.45); }}
.prof {{ flex:1 1 0; min-width:0; display:grid; grid-template-columns:repeat(4,1fr); gap:4px; }}
.pm {{ text-align:center; background:var(--ink-06); border-radius:8px; padding:5px 2px 4px; }}
.pm-k {{ font-size:9px; white-space:nowrap; font-weight:800; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-50); }}
.pm-v {{ font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:20px; line-height:1.05; margin-top:1px; }}
.pm-l {{ font-size:9.5px; color:var(--ink-50); margin-top:1px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.neg {{ color:#B3261E; }}
.pm-chg {{ font-size:11.5px; color:var(--ink-70); margin-top:5px; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.foot {{ padding:10px 18px 22px; font-size:10.5px; line-height:1.4; color:var(--ink-70); border-top:1px solid var(--ink-12); margin-top:8px; }}
.foot b {{ color:var(--ink); }}
@media print {{
  @page {{ size:A4 portrait; margin:10mm; }}
  .toggle {{ display:none; }}
  .screen[hidden] {{ display:block; }}
  .screens {{ display:grid; grid-template-columns:1fr 1fr; column-gap:22px; }}
  .foot {{ display:block; }} .foot summary {{ display:none; }}
  html, body {{ background:#fff; }}
  * {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  .page {{ max-width:100%; }}
  .band {{ border-radius:8px; }}
  .wrap2 {{ display:grid; grid-template-columns:1fr 1fr; column-gap:22px; }}
  .m {{ break-inside:avoid; }}
}}
</style>
</head>
<body>
<div class="page">
  <header class="band">
    <img class="logo" src="data:image/png;base64,{logo}" alt="Billy Button Early Learning">
    <div class="ttl"><h1>Friday Night Report</h1><div class="sub">Weekly occupancy report · {WEEK_LABEL}</div></div>
  </header>
  <nav class="toggle" role="tablist" aria-label="Centre">
    <button type="button" role="tab" id="tab-sm" aria-controls="south-morang" aria-selected="true" data-target="south-morang">South Morang</button>
    <button type="button" role="tab" id="tab-cb" aria-controls="craigieburn" aria-selected="false" data-target="craigieburn">Craigieburn</button>
  </nav>
  <div class="legend">
    <span><i class="dot" style="background:{SAGE}"></i>this week, toward target</span>
    <span><i class="dot" style="background:{EARTH}"></i>away from it</span>
    <span><i class="dot ring"></i>last week</span>
  </div>
  <div class="screens">
    <div id="south-morang" class="screen" role="tabpanel" aria-labelledby="tab-sm">{sm}</div>
    <div id="craigieburn" class="screen" role="tabpanel" aria-labelledby="tab-cb" hidden>{cb}</div>
  </div>
  <details class="foot">
    <summary>About the numbers</summary>
    <p><b>Issue {ISSUE}.</b> Figures from the Billy Button dashboard build of {SNAPSHOT}. The report is cut each Saturday morning from the overnight build, which closes the Monday-to-Friday week; nothing entered after 6 pm Friday counts. Forecast = average of the last 13 full weeks ({FORECAST_WINDOW}), the three-month rule. Solid dot = this week; ring = last week; green = moved from forecast toward target, brown = moved away.</p>
    <p><b>How each measure is counted.</b> Occupancy: Owna booked child-days, permanent enrolments only (no casual days), Mon–Fri ÷ licensed places × 5. Enquiries and tours completed: the dashboard's certified weekly metrics, counted in families. New enrolments: children pulled into Owna in the week. Lost spots: Owna formal withdrawals by finish week, school leavers apart; day reductions not included. $50 deposit paid, not yet enrolled: LineLeader families with the Owna form in and the $50 paid who have not yet been pulled into Owna, by the start month the parent gave (Overdue = that month has passed and the child is still not in Owna). The total is the families waiting; "Last week" is the same count a week earlier (in this first issue estimated from forms received and children pulled in the week). A deposit is not an enrolment: of the Jan–Aug 26 cohorts, deposits that went on to start were 25 of 32 at South Morang (78%) and 43 of 66 at Craigieburn (65%; 28 of 41 excluding the January opening group). Enrolled, due to start: children with an Owna enrolment whose start date is after the snapshot, by start month; last week as at {LASTWEEK_ASOF}. School leavers: children whose Owna record says they start school in 2027, by the month of their Owna finish date; "No date" means no finish date is entered yet. The forecast assumes every school leaver has gone by the end of January; last season at South Morang 40% of leaver spots went in December, 44% in January and 16% in February.</p>
    <p><b>Targets</b> are weekly rates: occupancy at 30 Jun 27 (South Morang 85%, Craigieburn 70%); lost spots 9 a month per centre; enquiries, tours and enrolments from the model's Target chain (South Morang 31 enquiries a month, Craigieburn 150, at certified conversion). The deposit and due-to-start profiles are the forward book and carry no target.</p>
  </details>
</div>
<script>
(function(){{
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.toggle button'));
  var screens = {{'south-morang': document.getElementById('south-morang'), 'craigieburn': document.getElementById('craigieburn')}};
  function show(id, push){{
    if(!screens[id]) id = 'south-morang';
    Object.keys(screens).forEach(function(k){{ screens[k].hidden = (k !== id); }});
    tabs.forEach(function(t){{ t.setAttribute('aria-selected', t.dataset.target === id ? 'true' : 'false'); }});
    try {{ localStorage.setItem('bbw-centre', id); }} catch(e) {{}}
    if(push && location.hash !== '#' + id){{ try {{ history.replaceState(null, '', '#' + id); }} catch(e) {{ location.hash = id; }} }}
    window.scrollTo(0, 0);
  }}
  tabs.forEach(function(t){{ t.addEventListener('click', function(){{ show(t.dataset.target, true); }}); }});
  window.addEventListener('hashchange', function(){{ show(location.hash.replace('#',''), false); }});
  var start = location.hash.replace('#','');
  if(!screens[start]){{ try {{ start = localStorage.getItem('bbw-centre') || 'south-morang'; }} catch(e) {{ start = 'south-morang'; }} }}
  show(start, false);
  // swipe between screens
  var x0 = null, y0 = null;
  document.addEventListener('touchstart', function(e){{ x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }}, {{passive:true}});
  document.addEventListener('touchend', function(e){{
    if(x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null;
    if(Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 1.5){{
      var cur = screens['south-morang'].hidden ? 'craigieburn' : 'south-morang';
      show(dx < 0 ? 'craigieburn' : 'south-morang', true);
    }}
  }}, {{passive:true}});
}})();
</script>
</body>
</html>
"""
if __name__ == "__main__":
    out = pathlib.Path("/mnt/user-data/outputs"); out.mkdir(parents=True, exist_ok=True)
    p = out / f"261106 - Friday Night Report - v{ISSUE}.html"
    p.write_text(html, encoding="utf-8")
    print(p, len(html) // 1024, "KB")
