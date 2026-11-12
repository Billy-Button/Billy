"""Pipeline tabs: Yesterday and Month (the Week tab is the existing weekly Pipeline screen)."""
import sys, pathlib, datetime as dt, statistics as st
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "kpi"))
import pipe as P
INK, EARTH, SAGE, AMBER = "#2b2622", "#A45823", "#6E8B57", "#E2A23B"
CENTRES = ["South Morang", "Craigieburn"]
# Hours the administration team answers enquiries. An assumption, to review (Cameron, 13 Nov 26).
OPEN, CLOSE = dt.time(8, 30), dt.time(17, 30)
CLOSED = {dt.date(2026, 11, 3)}          # centre closed days (Cup Day)
SNAP = dt.datetime.fromisoformat(P.SNAP); TODAY = SNAP.date()
def workday(d): return d.weekday() < 5 and d not in CLOSED
Y = TODAY - dt.timedelta(days=1)
while not workday(Y): Y -= dt.timedelta(days=1)
EXTRA = [Y + dt.timedelta(days=i) for i in range(1, (TODAY - Y).days)]      # weekend / closed days after Y
MON = Y - dt.timedelta(days=Y.weekday())
LW0 = MON - dt.timedelta(days=7); LW = [LW0 + dt.timedelta(days=i) for i in range(5)]
LW_OPEN = sum(workday(d) for d in LW)
WK = [MON + dt.timedelta(days=i) for i in range((Y - MON).days + 1)]
fd = lambda d: f"{d.day} {d:%b %y}"
YLAB = f"{Y:%a} {fd(Y)}" + (" + weekend" if EXTRA else "")
EV = {}
for c, p, k, n, x in P.D: EV[(c, dt.date.fromisoformat(p), k)] = (n, x)
def ev(c, days, k, j=0): return sum(EV.get((c, d, k), (0, 0))[j] for d in days)
# ---- first contact, business-hours clock ----
def bmin(a, b):
    """Minutes between a and b counted only inside OPEN-CLOSE on working days."""
    if b <= a: return 0
    tot, d = 0, a.date()
    while d <= b.date():
        if workday(d):
            s, e = max(a, dt.datetime.combine(d, OPEN)), min(b, dt.datetime.combine(d, CLOSE))
            if e > s: tot += (e - s).total_seconds() / 60
        d += dt.timedelta(days=1)
    return tot
def in_hours(t): return workday(t.date()) and OPEN <= t.time() < CLOSE
FCR = []
for c, e, t, s in P.F:
    e = dt.datetime.fromisoformat(e); t = dt.datetime.fromisoformat(t) if t else None
    FCR.append((c, e, t, s, (t - e).total_seconds() / 60 if t else None, bmin(e, t) if t else None))
def fc_set(c, days=None, month=None):
    return [r for r in FCR if r[0] == c and ((days and r[1].date() in days) or (month and r[1].strftime("%Y-%m") == month))]
def fmt_min(m):
    if m is None: return "–"
    if m < 1: return "&lt;1<small>min</small>"
    if m < 90: return f"{m:.0f}<small>min</small>"
    if m < 60 * 9 * 1.5: return f"{m/60:.1f}<small>hrs</small>"
    return f"{m/540:.1f}<small>work days</small>"
def plain(m): return fmt_min(m).replace("<small>", " ").replace("</small>", "").replace("&lt;", "under ")
def raw_plain(m):
    if m is None: return "–"
    return "under 1 min" if m < 1 else f"{m:.0f} min" if m < 90 else f"{m/60:.1f} hrs" if m < 48 * 60 else f"{m/1440:.1f} days"
def waiting(c):
    w = [r for r in FCR if r[0] == c and r[2] is None and r[3] == "new enquiry" and (TODAY - r[1].date()).days <= 30]
    out = sum(1 for r in w if not in_hours(r[1]))
    return len(w), out, len(w) - out
# ---- Yesterday ----
ROWS = [("enq", "New Enquiry", "families · LineLeader", True), ("fc", "Time to first contact", "enquiry to first human contact", False),
        ("ts", "Tours Scheduled", "families · LineLeader", True), ("tc", "Tours Completed", "families · LineLeader", True),
        ("of", "Offered", "families · LineLeader", True), ("pe", "Pending", "Owna form in", True),
        ("ec", "Enrolment complete", "pulled into Owna · $50 charged", False), ("st", "Started", "spots a week · first day in Owna", False),
        ("lo", "Lost spots", "spots a week · leaving Owna, not school leavers", False)]
def n0(v): return f"{v:g}"
def arrow(y, avg):
    if abs(y - avg) < 0.5: return '<span class="pd-ar lvl">● level</span>'
    return '<span class="pd-ar up">▲ up</span>' if y > avg else '<span class="pd-ar dn">▼ down</span>'
def y_row(c, k, label, unit, arr):
    days = [Y] + EXTRA
    if k == "fc":
        s = fc_set(c, days); got = [r for r in s if r[2]]
        big = f"{len(got)}<small>of {len(s)}</small>" if s else "–"
        sub = ("contacted so far · median " + plain(st.median(r[5] for r in got)) + " in work hours") if got else ("no new enquiries" if not s else "none contacted yet")
        lw = fc_set(c, LW); lg = [r for r in lw if r[2]]
        note = f"Last week {len(lg)} of {len(lw)} contacted" + (f" · median {plain(st.median(r[5] for r in lg))}" if lg else "")
        return f'<li class="pd-r"><div class="pd-t"><b>{label}</b><span>{unit}</span></div><div class="pd-b"><div class="pd-n">{big}</div><div class="pd-s">{sub}<br><i>{note}</i></div></div></li>'
    y = ev(c, days, k); wk = ev(c, WK + EXTRA, k); lw = ev(c, LW, k); avg = lw / LW_OPEN
    kids = ev(c, days, k, 1)
    extra = f" · {kids:g} {'child' if kids == 1 else 'children'}" if k in ("st", "lo") and y else ""
    sub = f"{n0(wk)} so far this week{extra}<br><i>Last week {n0(lw)} · {avg:.1f} a day</i>"
    a = arrow(y, avg) if arr else ""
    return f'<li class="pd-r"><div class="pd-t"><b>{label}</b><span>{unit}</span></div><div class="pd-b"><div class="pd-n">{n0(y)}</div><div class="pd-s">{sub}</div>{a}</div></li>'
def yesterday(c):
    w, out, inh = waiting(c)
    wl = (f'<div class="pd-wait{" on" if w else ""}"><b>Waiting for first contact: {w}</b>'
          + (f'<span>{out} came in overnight or on a weekend · {inh} in work hours</span>' if w else '<span>Every new enquiry has been contacted or moved on.</span>') + '</div>')
    rows = "".join(y_row(c, *r) for r in ROWS)
    note = (f'<p class="pd-note">What happened on {YLAB}, as recorded by this morning. ▲ ▼ ● compares the day with last week\'s average a day '
            f'(week ending {fd(LW[-1])}, {LW_OPEN} open days). No arrow on the rows that are too small to read day by day. '
            f'Work hours for answering enquiries are taken as 8:30am to 5:30pm, Monday to Friday: an assumption, to review.</p>')
    return f'<div class="pd">{wl}<ul class="pd-l">{rows}</ul>{note}</div>'
# ---- Month ----
MS = {}
for c, p, k, n, x in P.M: MS[(c, p, k)] = (n, x)
LASTM = (TODAY.replace(day=1) - dt.timedelta(days=1)); LM = LASTM.strftime("%Y-%m")
MONTHS = sorted({p for (c, p, k) in MS if "2026-03" <= p <= LM})
MLAB = f"{LASTM.day} {LASTM:%b %y}"
def bars(vals, fmtv=lambda v: f"{v:g}", col=EARTH):
    W, H, L, R, T, B = 340, 96, 6, 62, 14, 16
    hi = max([v for v in vals if v is not None] + [1]) * 1.12; n = len(vals); bw = (W - L - R) / n
    ys = lambda v: T + (H - T - B) * (1 - v / hi); g = ""
    for i, v in enumerate(vals):
        x = L + i * bw; last = i == n - 1
        g += f'<text x="{x+bw/2:.1f}" y="{H-4}" text-anchor="middle" font-size="9" fill="{INK}" opacity=".5">{dt.date.fromisoformat(MONTHS[i]+"-01"):%b}</text>'
        if v is None: continue
        g += f'<rect x="{x+3:.1f}" y="{ys(v):.1f}" width="{bw-6:.1f}" height="{max(H-B-ys(v),1):.1f}" rx="3" fill="{col}" opacity="{1 if last else .32}"/>'
        g += f'<text x="{x+bw/2:.1f}" y="{ys(v)-3:.1f}" text-anchor="middle" font-size="9" font-weight="800" fill="{INK}" opacity="{1 if last else .6}" stroke="#FBF6EE" stroke-width="2.5" paint-order="stroke">{fmtv(v)}</text>'
    last3 = [v for v in vals[-3:] if v is not None]
    if last3:
        a = sum(last3) / len(last3); x0 = L + (n - 3) * bw
        g += f'<line x1="{x0:.1f}" y1="{ys(a):.1f}" x2="{W-R+2}" y2="{ys(a):.1f}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="5 3"/>'
        g += f'<text x="{W-R+5}" y="{ys(a)+3:.1f}" font-size="9" font-weight="800" fill="{INK}">3-mth avg {fmtv(a)}</text>'
    return f'<svg class="pm-ch" viewBox="0 0 {W} {H}">{g}</svg>'
def m_row(c, k, label, unit, _):
    if k == "ec":
        return (f'<li class="pd-r" style="opacity:.45"><div class="pd-t"><b>{label}</b><span>{unit}</span></div>'
                f'<div class="pd-s">Monthly history starts November 26, when Owna began sending the date each child was pulled in.</div></li>')
    if k == "fc":
        vals, cnt = [], []
        for m in MONTHS:
            s = fc_set(c, month=m); got = [r[5] for r in s if r[2]]
            vals.append(st.median(got) / 60 if got else None); cnt.append((len(got), len(s)))
        v = vals[-1]; g, s = cnt[-1]
        raw = [r[4] for r in fc_set(c, month=LM) if r[2]]
        big = fmt_min(v * 60) if v is not None else "–"
        sub = f"median in work hours · {g} of {s} contacted" + (f"<br><i>By the clock: {raw_plain(st.median(raw))}</i>" if raw else "")
        ch = bars(vals, lambda x: f"{x:.0f}h", col=SAGE)
    else:
        vals = [MS.get((c, m, k), (0, 0))[0] for m in MONTHS]; v = vals[-1]; pv = vals[-2]
        kids = MS.get((c, LM, k), (0, 0))[1]
        big = n0(v); extra = f"{kids:g} children · " if k in ("st", "lo") else ""
        sub = f"{extra}{dt.date.fromisoformat(MONTHS[-2]+'-01'):%B} was {n0(pv)}"
        ch = bars(vals, col=(AMBER if k == "lo" else EARTH))
    return (f'<li class="pd-r"><div class="pd-t"><b>{label}</b><span>{unit.replace("spots a week", "spots")}</span></div>'
            f'<div class="pd-b"><div class="pd-n">{big}</div><div class="pd-s">{sub}</div></div>{ch}</li>')
def month(c):
    rows = "".join(m_row(c, *r) for r in ROWS)
    note = (f'<p class="pd-note">Complete months only, {dt.date.fromisoformat(MONTHS[0]+"-01"):%B} to {LASTM:%B %Y}; LineLeader history starts after the February import. '
            f'Dark bar = the month just closed. Dashed line = average of the last three months, the three-month rule. '
            f'Lost spots here are children who left (school leavers apart). Time to first contact counts work hours only (8:30am to 5:30pm, Monday to Friday: an assumption, to review).</p>')
    return f'<div class="pd">{"".join(["<ul class=\"pd-l\">", rows, "</ul>"])}{note}</div>'
css = """
.pfbar{position:sticky;top:var(--tb,64px);z-index:5;background:var(--cream);box-shadow:0 6px 8px -8px rgba(43,35,32,.25)}
.pfbar .toggle{position:static;box-shadow:none}
.pdtabs{display:flex;gap:0;margin:0 18px 8px;border:1.5px solid var(--earth);border-radius:10px;overflow:hidden}
.pdtabs button{flex:1 1 0;font:inherit;font-weight:800;font-size:13px;padding:7px 4px;border:0;background:transparent;color:var(--earth);cursor:pointer}
.pdtabs button+button{border-left:1.5px solid var(--earth)}
.pdtabs button[aria-selected="true"]{background:var(--earth);color:var(--cream)}
.pd{padding:6px 18px 10px}.pd-l{list-style:none;margin:0;padding:0}
.pd-r{padding:10px 0;border-bottom:1px solid rgba(43,35,32,.09)}
.pd-t{display:flex;justify-content:space-between;align-items:baseline;gap:8px}.pd-t b{font-family:"Fredoka","Nunito",sans-serif;font-weight:600;font-size:16px}.pd-t span{font-size:11px;color:rgba(43,35,32,.55);text-align:right}
.pd-b{display:flex;align-items:center;gap:12px;margin-top:2px}
.pd-n{flex:0 0 78px;font-family:"Fredoka","Nunito",sans-serif;font-weight:600;font-size:30px;line-height:1.1;white-space:nowrap}.pd-n small{font-size:12px;font-weight:700;margin-left:3px;color:rgba(43,35,32,.6)}
.pd-s{flex:1 1 auto;font-size:12.5px;font-weight:700;line-height:1.35}.pd-s i{font-style:normal;font-weight:600;color:rgba(43,35,32,.55)}
.pd-ar{flex:0 0 auto;font-size:12px;font-weight:800;border-radius:999px;padding:3px 9px;white-space:nowrap}
.pd-ar.up{background:rgba(110,139,87,.18);color:#4d6a3a}.pd-ar.dn{background:rgba(164,88,35,.15);color:#7a3f17}.pd-ar.lvl{background:rgba(43,35,32,.07);color:rgba(43,35,32,.6)}
.pd-wait{border-radius:12px;padding:10px 12px;margin:4px 0 6px;background:rgba(110,139,87,.14)}.pd-wait.on{background:rgba(226,162,59,.22)}
.pd-wait b{display:block;font-family:"Fredoka","Nunito",sans-serif;font-weight:600;font-size:16px}.pd-wait span{font-size:12.5px;font-weight:700}
.pd-note{font-size:11.5px;line-height:1.45;color:rgba(43,35,32,.6);margin:10px 0 0}
.pm-ch{display:block;width:100%;height:auto;margin-top:6px}
"""
js = """
  (function(){ var c='sm', p='w';
    function show(){ ['sm','cb'].forEach(function(a){ ['d','w','m'].forEach(function(b){ var e=document.getElementById('pf-'+a+'-'+b); if(e) e.hidden=!(a===c&&b===p); }); });
      var s=document.getElementById('pf-sub'); if(s) s.textContent=s.getAttribute('data-'+p);
      var l=document.getElementById('pf-legend'); if(l) l.style.display=(p==='w'?'':'none'); window.scrollTo(0,0); }
    Array.prototype.slice.call(document.querySelectorAll('.toggle.pf button')).forEach(function(t){ t.addEventListener('click', function(){ c=t.dataset.pf==='pf-cb'?'cb':'sm'; show(); }); });
    var pt=Array.prototype.slice.call(document.querySelectorAll('.pdtabs button'));
    pt.forEach(function(t){ t.addEventListener('click', function(){ pt.forEach(function(x){ x.setAttribute('aria-selected', x===t?'true':'false'); }); p=t.dataset.pd; show(); }); });
  })();
"""
if __name__ == "__main__":
    print("Y", Y, "extra", EXTRA, "wk", WK[0], "lw", LW[0], LW_OPEN, "months", MONTHS)
    for c in CENTRES:
        print(c, "waiting", waiting(c))
        for k, lab, u, a in ROWS:
            if k != "fc": print("  ", k, ev(c, [Y] + EXTRA, k), "wk", ev(c, WK, k), "lw", ev(c, LW, k), "| Oct", MS.get((c, LM, k)))
        for wd, nm in ((LW, "lw"), (WK, "wk")):
            s = fc_set(c, wd); g = [r for r in s if r[2]]
            print("  fc", nm, len(g), len(s), "fair", round(st.median(r[5] for r in g)) if g else None, "raw", round(st.median(r[4] for r in g)) if g else None)
