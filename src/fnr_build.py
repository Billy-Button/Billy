import base64, pathlib, html as H
icon = open("/home/claude/wp/icon_b64.txt").read()
logo = open("/home/claude/wp/logo_b64.txt").read()

F = pathlib.Path("/home/claude/wp/fonts")
fred = base64.b64encode((F / "Fredoka-sub.ttf").read_bytes()).decode()
nun = base64.b64encode((F / "Nunito-sub.ttf").read_bytes()).decode()

SAGE, EARTH, SKY, INK, YEL = "#6E8B57", "#A45823", "#5E80A0", "#2B2320", "#FDC546"
AMBER = "#E39B2D"
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


def bar(this, last, fcst, target, higher_better, fmt, fcst_lbl, target_lbl, last_lbl, hd=False):
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
    if target is not None:
        past_target = (this - target) * (target - fcst) >= 0
        fill = SAGE if past_target else (AMBER if improving or on_fcst else EARTH)
    else:
        fill = AMBER if (improving or on_fcst) else EARTH
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
    parts.append(f'<text x="{xf}" y="8" text-anchor="middle" class="tk">{fcst_lbl}</text>')
    # target tick
    if xt is not None:
        parts.append(f'<line x1="{xt}" y1="12" x2="{xt}" y2="32" stroke="{INK}" stroke-width="2"/>')
        parts.append(f'<text x="{xt}" y="8" text-anchor="middle" class="tk">{target_lbl}</text>')
    else:
        parts.append(f'<line x1="{TX}" y1="12" x2="{TX}" y2="32" stroke="rgba(43,35,32,.25)" stroke-width="2" stroke-dasharray="3 3"/>')
        parts.append(f'<text x="{TX}" y="8" text-anchor="middle" class="tk tbc">{target_lbl}</text>')
    # this week marker
    parts.append(f'<circle cx="{xv}" cy="22" r="8" fill="{fill}" stroke="#FBF6EE" stroke-width="2.5"/>')
    # last week hollow ring, drawn on top so an unchanged week shows as a ringed dot
    if xl is not None:
        parts.append(f'<circle cx="{xl}" cy="22" r="5.5" fill="none" stroke="{INK}" stroke-width="1.6" opacity=".75"/>')
    h = 38
    if hd:
        h = 50
        parts.append(f'<text x="{xf}" y="44" text-anchor="middle" class="hd">forecast</text>')
        parts.append(f'<text x="{TX}" y="44" text-anchor="middle" class="hd">target</text>')
    return f'<svg viewBox="0 0 {W} {h}" class="bar" role="img">{"".join(parts)}</svg>'


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


def profile_row(label, unit, total, total_sub, months, change, neg=False, cell_unit="last wk"):
    """months: list of (label, this, last_or_spots)"""
    def sub(l):
        if l in ("—", None): return ''
        return f'<div class="pm-l">{"%s spots" % l if cell_unit == "spots" else "last wk " + fmt(l, neg)}</div>'
    cells = "".join(f'<div class="pm"><div class="pm-k">{m}</div><div class="pm-v">{fmt(t, neg)}</div>{sub(l)}</div>' for m, t, l in months)
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
      <div class="cols"><div class="num"><span class="k">{places} places</span></div><svg viewBox="0 0 300 14" class="bar"><text x="{FX}" y="11" text-anchor="middle" class="hd">Forecast</text><text x="{TX}" y="11" text-anchor="middle" class="hd">Target</text></svg></div>
      <ul class="measures">{''.join(rows)}</ul>
    </section>"""



# ============================================================
# WEEK'S FIGURES — the only part that changes each issue
# ============================================================
ISSUE = "2.3"
WEEK_LABEL = "6 Nov 26"                 # Friday that closes the week
SNAPSHOT = "Sat 7 Nov 26, 3:06 am AEDT"  # dashboard build the figures come from
FORECAST_WINDOW = "weeks of 3 Aug to 26 Oct"
LASTWEEK_ASOF = "Fri 30 Oct"

# bar(this, last, forecast, target, higher_is_better, unit, forecast_label, target_label, last_label)
DATA = {
 "South Morang": {"places": 108, "rows": [
  ("sec", "Base case", "end Feb 27"),
  ("bar", "Occupancy", "incl. casual days", "80%", "433 spots · 9 casual", (80.2, 79.4, 78.2, 85, True, "%", "78%", "85%", "79%")),
  ("q", "− Leaving for school", "gone by end Jan", 33, "−102 spots",
      [("Nov", 1, 1), ("Dec", 3, 9), ("Jan–Feb", 1, 5), ("No date", 28, 87)],
      "28 have no finish date in Owna", True),
  ("q", "+ Enrolled, not started", "in Owna, start date ahead", 5, "+10 spots",
      [("Nov", 2, 3), ("Dec", 1, 2), ("Jan", 1, 2), ("Feb+", 1, 3)], "2 pulled through this week", False),
  ("q", "+ Pending", "Owna form in, not pulled through", 1, "+2 spots asked",
      [("Past start", 0, 0), ("Nov–Dec", 0, 0), ("Jan–Feb", 1, 2), ("Later / none", 0, 0)],
      "+1 form in, 2 pulled through · 1 more gone quiet", False),
  ("bar", "= Base case, end Feb 27", "if nothing else changes", "63%", "341 spots", (63.1, None, 78.2, 85, True, "%", "78%", "85%", "")),
  ("sec", "Performance", "this week"),
  ("bar", "New enquiries", "families", "4", "last week 4", (4, 4, 4.3, 7, True, "", "4.3", "7", "4")),
  ("bar", "Tours completed", "families", "1", "last week 4", (1, 4, 4.2, 5.5, True, "", "4.2", "5–6", "4")),
  ("bar", "Enrolment complete", "pulled into Owna · $50 charged", "2", "last week 2", (2, 2, 1.2, 2.5, True, "", "1.2", "2–3", "2")),
  ("bar", "Started", "spots a week · first day in the week", "0", "no starts", (0, 0, 3.0, 7, True, "", "3.0", "7", "0")),
  ("bar", "Lost spots", "spots a week · not school leavers", "7", "2 children", (7, 3, 2.4, 2.1, False, "", "2.4", "2.1", "3")),
 ]},
 "Craigieburn": {"places": 174, "rows": [
  ("sec", "Base case", "end Feb 27"),
  ("bar", "Occupancy", "incl. casual days", "36%", "309 spots · 8 casual", (35.5, 35.1, 33.9, 70, True, "%", "34%", "70%", "35%")),
  ("q", "− Leaving for school", "gone by end Jan", 22, "−79 spots",
      [("Nov", 1, 5), ("Dec", 0, 0), ("Jan–Feb", 0, 0), ("No date", 21, 74)],
      "21 have no finish date in Owna", True),
  ("q", "+ Enrolled, not started", "in Owna, start date ahead", 5, "+7 spots",
      [("Nov", 2, 1), ("Dec", 1, 2), ("Jan", 0, 0), ("Feb+", 2, 4)], "3 started this week", False),
  ("q", "+ Pending", "Owna form in, not pulled through", 13, "+28 spots asked",
      [("Past start", 2, 1), ("Nov–Dec", 3, 8), ("Jan–Feb", 6, 17), ("Later / none", 2, 2)],
      "+2 forms in, 0 pulled · 9 more gone quiet, not counted", False),
  ("bar", "= Base case, end Feb 27", "if nothing else changes", "30%", "265 spots", (30.5, None, 33.9, 70, True, "%", "34%", "70%", "")),
  ("sec", "Performance", "this week"),
  ("bar", "New enquiries", "families", "5", "last week 5", (5, 5, 7.7, 35, True, "", "7.7", "35", "5")),
  ("bar", "Tours completed", "families", "5", "last week 4", (5, 4, 5.8, 23, True, "", "5.8", "23", "4")),
  ("bar", "Enrolment complete", "pulled into Owna · $50 charged", "0", "last week 6", (0, 6, 2.2, 11, True, "", "2.2", "11", "6")),
  ("bar", "Started", "spots a week · first day in the week", "11", "3 children started", (11, 0, 4.4, 33, True, "", "4.4", "33", "0")),
  ("bar", "Lost spots", "spots a week · not school leavers", "0", "none", (0, 4, 3.8, 2.1, False, "", "3.8", "2.1", "4")),
 ]},
}
# ============================================================

def build_rows(rows):
    out = []
    for r in rows:
        if r[0] == "sec":
            _, title, sub = r
            out.append(f'<li class="sec"><span class="sec-t">{title}</span><span class="sec-s">{sub}</span></li>')
            continue
        if r[0] == "q":
            _, label, unit, total, sub, months, change, neg = r
            out.append(profile_row(label, unit, total, sub, months, change, neg=neg, cell_unit="spots").replace('<li class="m">','<li class="m q">',1))
            continue
        if r[0] == "bar":
            _, label, unit, big, sub, args = r
            h = row(label, unit, big, sub, bar(*args, hd=label in ("Occupancy", "New enquiries") or label.startswith("= Base case")))
            if label == "Occupancy":
                h = h.replace('<li class="m">', '<li class="m lead">', 1)
            if label.startswith("= Base case"):
                h = h.replace('<li class="m">', '<li class="m total">', 1)
            out.append(h)
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
.toggle {{ position:sticky; top:0; z-index:5; display:flex; gap:6px; padding:12px 18px 6px; background:var(--cream); }}
.toggle button {{ flex:1 1 0; font:inherit; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; padding:10px 8px; border-radius:999px; border:2px solid var(--earth); background:transparent; color:var(--earth); cursor:pointer; -webkit-tap-highlight-color:transparent; }}
.toggle button[aria-selected="true"] {{ background:var(--earth); color:var(--cream); }}
.screen[hidden] {{ display:none; }}
.foot summary {{ cursor:pointer; font-weight:800; color:var(--ink); }}
.foot p {{ margin:6px 0 0; }}
.defs {{ margin:6px 0 0; }} .defs dt {{ font-weight:700; color:var(--ink); margin-top:7px; }} .defs dd {{ margin:1px 0 0; }}
.ctx {{ padding:8px 18px 0; font-size:12px; color:var(--ink-70); line-height:1.4; }}
.ctx b {{ color:var(--ink); }}
.legend {{ display:flex; gap:6px 10px; flex-wrap:wrap; padding:6px 18px 0; font-size:10.5px; font-weight:600; color:var(--ink-50); }}
.legend span {{ display:inline-flex; align-items:center; gap:5px; }}
.dot {{ width:11px; height:11px; border-radius:50%; display:inline-block; }}
.ring {{ background:transparent; border:1.6px solid var(--ink); opacity:.7; width:10px; height:10px; }}
.centre {{ padding:0 18px 2px; }}
.c-head {{ display:flex; align-items:center; gap:8px; padding-bottom:6px; border-bottom:2px solid var(--earth); }}
.c-idx {{ width:22px; height:22px; border-radius:50%; background:var(--earth); color:var(--cream); font-size:12px; display:inline-flex; align-items:center; justify-content:center; }}
h2 {{ margin:0; font-size:20px; line-height:1; }}
.c-places {{ margin-left:auto; font-size:10.5px; color:var(--ink-50); font-weight:700; text-align:right; }}
.measures {{ list-style:none; margin:0; padding:0; }}
.m {{ padding:12px 0 8px; }}
.sec {{ display:flex; align-items:baseline; gap:8px; padding:26px 0 2px; }}
.sec-t {{ font-family:'Fredoka',sans-serif; font-weight:600; font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--earth); }} .sec-s {{ font-size:10.5px; color:var(--ink-50); margin-left:auto; }}
.m.lead {{ padding:10px 0 8px; }}
.m.total {{ padding:14px 0 12px; margin-top:4px; background:#fff; border-radius:14px; padding-left:14px; padding-right:14px; }}
.m.total .big {{ font-size:40px; }} .m.total .m-label {{ font-size:17px; }}
.m.lead .m-label {{ font-size:19px; }} .m.lead .big {{ font-size:44px; }}
.m.q {{ padding:8px 0 6px; }}


.m-top {{ display:flex; align-items:baseline; gap:8px; }}
.m-label {{ font-size:14px; font-weight:700; }}
.m-unit {{ font-size:11px; color:var(--ink-50); margin-left:auto; text-align:right; white-space:nowrap; }}
.prov {{ font-size:9.5px; font-weight:800; text-transform:uppercase; letter-spacing:.06em; color:var(--earth); border:1px solid var(--earth); border-radius:4px; padding:0 4px; }}
.m-body {{ display:flex; align-items:center; gap:10px; margin-top:2px; }}
.num {{ flex:0 0 78px; }}
.big {{ font-size:34px; line-height:1; font-variant-numeric:tabular-nums; }}
.s {{ font-size:10.5px; color:var(--ink-70); margin-top:2px; line-height:1.2; white-space:nowrap; }}
.bar {{ flex:1 1 0; min-width:0; width:100%; height:auto; display:block; overflow:visible; }}
.cols {{ display:none; }}
.cols .k {{ font-size:9.5px; font-weight:800; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-50); }}
.hd {{ font-family:"Nunito",sans-serif; font-size:10px; font-weight:700; fill:rgba(43,35,32,.55); }}
.hd-l {{ text-transform:none; letter-spacing:0; font-weight:700; }}
.tk {{ font-family:"Nunito",sans-serif; font-size:9.5px; font-weight:700; fill:rgba(43,35,32,.62); }}
.tbc {{ fill:rgba(43,35,32,.45); }}
.prof {{ flex:1 1 0; min-width:0; display:grid; grid-template-columns:repeat(4,1fr); gap:4px; }}
.pm {{ text-align:center; padding:4px 2px 2px; }}
.pm-k {{ font-size:9px; white-space:nowrap; font-weight:800; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-50); }}
.pm-v {{ font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:20px; line-height:1.05; margin-top:1px; }}
.pm-l {{ font-size:9.5px; color:var(--ink-50); margin-top:1px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.neg {{ color:#B3261E; }}
.pm-chg {{ font-size:11px; color:var(--ink-50); margin-top:4px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
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
    <span><i class="dot" style="background:{EARTH}"></i>below forecast</span>
    <span><i class="dot" style="background:{AMBER}"></i>forecast to target</span>
    <span><i class="dot" style="background:{SAGE}"></i>at target</span>
    <span><i class="dot ring"></i>last week</span>
  </div>
  <div class="screens">
    <div id="south-morang" class="screen" role="tabpanel" aria-labelledby="tab-sm">{sm}</div>
    <div id="craigieburn" class="screen" role="tabpanel" aria-labelledby="tab-cb" hidden>{cb}</div>
  </div>
  <details class="foot">
    <summary>About the numbers</summary>
    <p><b>Issue {ISSUE}.</b> Figures from the Billy Button dashboard build of {SNAPSHOT}. The report is cut each Saturday morning from the overnight build, which closes the Monday-to-Friday week; nothing entered after 6 pm Friday counts. Forecast = average of the last 13 full weeks ({FORECAST_WINDOW}), the three-month rule. Solid dot = this week; ring = last week; green = moved from forecast toward target, brown = moved away.</p>
    <p><b>How each measure is counted</b> — one line each, in the order shown, using the dashboard's terms, which are LineLeader's and Owna's own words where the data is theirs. The base case is a snapshot: occupancy now, less leavers, plus the two queues, equals the book at end February; month cells show children with their spots. The performance rows are weekly rates against the forecast and target, with last week as the hollow ring. Colours: brown below forecast, amber between forecast and target, green at or beyond target.</p>
    <dl class="defs">
      <dt>Occupancy</dt><dd>All Owna booked child-days Mon–Fri, casual days included, ÷ licensed places × 5. The sub-line shows the casual days inside the total.</dd>
      <dt>− Leaving for school</dt><dd>Children whose Owna record says they start school in 2027, by the month of their Owna finish date. "No date" = no finish date entered yet. The forecast assumes every leaver has gone by the end of January; last season at South Morang 40% of leaver spots went in December, 44% in January, 16% in February.</dd>
      <dt>+ Enrolled, not started</dt><dd>Children with an Owna enrolment whose start date is after the snapshot, by start month, with their booked days a week as the spots they add. Last week as at {LASTWEEK_ASOF}. The byline shows pulled in and started out.</dd>
      <dt>+ Pending</dt><dd>Families whose Owna enrolment form is in but has not yet been pulled through (Owna shows them as Pending), by the start month the parent gave. "Past start" = that month has passed and the child is still not in Owna. Families more than 60 days past the step's target are gone quiet (the dashboard's term: mostly lost, not yet closed in LineLeader); they are named in the byline and left out of the count and the base case. Pending is not yet a start: of the Jan–Aug 26 cohorts, forms that went on to a start were 25 of 32 at South Morang (78%) and 43 of 66 at Craigieburn (65%).</dd>
      <dt>= Base case, end Feb 27</dt><dd>Occupancy now, less the school leavers (all assumed gone by end January), plus due-to-start and pending spots (most start by February), ÷ licensed places × 5. Where each centre lands if nothing else changes: no new enquiries, no new losses, every pending family starts. The gap from here to the forecast and target is what the flow below has to deliver.</dd>
      <dt>New enquiries</dt><dd>New LineLeader enquiries in the week, counted in families (the dashboard's certified weekly metric).</dd>
      <dt>Tours completed</dt><dd>Tours that took place in the week, counted in families (certified weekly metric).</dd>
      <dt>Enrolment complete</dt><dd>Children pulled into Owna in the week: room, days and compliance confirmed, the account created and the $50 charged. This is the conversion the forecast is built on.</dd>
      <dt>Started</dt><dd>Booked days a week of children whose Owna start date fell in the week. Same children as "Enrolled, not started", counted the week they walk in. Extra days added by existing children are not in it.</dd>
      <dt>Lost spots</dt><dd>Booked days a week of Owna formal withdrawals by finish week. School leavers are shown separately; day reductions are not included.</dd>
    </dl>
    <p><b>Targets</b> are weekly rates: occupancy at 30 Jun 27 (South Morang 85%, Craigieburn 70%); spots gained from the Target chain in children × average days (South Morang 7, Craigieburn 33 a week); spots lost 9 a month per centre; enquiries, tours and enrolled from the model's Target chain (South Morang 31 enquiries a month, Craigieburn 150, at certified conversion). Pending, due to start and school leavers are the forward book and carry no target.</p>
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
