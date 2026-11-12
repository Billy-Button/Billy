"""Pipeline tabs: Yesterday and Month (the Week tab is the existing weekly Pipeline screen)."""
import sys, pathlib, datetime as dt, statistics as st
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "kpi"))
import pipe as P
INK, EARTH, SAGE, AMBER = "#2b2622", "#A45823", "#6E8B57", "#E2A23B"
CENTRES = ["South Morang", "Craigieburn"]
# Hours the administration team answers enquiries. An assumption, to review (Cameron, 13 Nov 26).
OPEN, CLOSE = dt.time(8, 30), dt.time(17, 30)
# weekdays the centres were closed (no attendance in Owna) + known ones ahead; the dashboard's closure list is empty until the centres confirm it
CLOSED = {dt.date(*d) for d in [(2026,4,3),(2026,4,6),(2026,6,8),(2026,9,25),(2026,11,3),(2026,12,25),(2026,12,28),(2027,1,1),(2027,1,26)]}
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
GREEN = "#4d6a3a"
TGT_W = {"South Morang": dict(enq=(7,"7"), fc=(10/60,"10 min"), ts=(5.5,"5–6"), tc=(5.5,"5–6"), of=(5.5,"5–6"), pe=(2.5,"2–3"), ec=(2.5,"2–3"), st=(7,"7"), lo=(2.1,"2.1")),
         "Craigieburn":  dict(enq=(35,"35"), fc=(10/60,"10 min"), ts=(23,"23"), tc=(23,"23"), of=(23,"23"), pe=(11,"11"), ec=(11,"11"), st=(33,"33"), lo=(2.1,"2.1"))}
TGT_M = {"South Morang": dict(enq=(31,"31"), fc=(10/60,"10 min"), ts=(24,"24"), tc=(24,"24"), of=(24,"24"), pe=(11,"11"), ec=(11,"11"), st=(30,"30"), lo=(9,"9")),
         "Craigieburn":  dict(enq=(150,"150"), fc=(10/60,"10 min"), ts=(100,"100"), tc=(100,"100"), of=(100,"100"), pe=(48,"48"), ec=(48,"48"), st=(143,"143"), lo=(9,"9"))}
LOWER = {"fc", "lo"}
def bars(labels, vals, avg, tgt, tlab, fmtv=lambda v: f"{v:g}", lower=False, marks=(), groups=None, avgname="3-mth average"):
    W, H, L, R, T, B = 340, (124 if groups else 112), 4, 84, 22, (28 if groups else 16)
    vv = sorted(v for v in vals if v is not None)
    med = vv[len(vv) // 2] if vv else 0
    cap = max(3 * med, med + 4) if not lower else max(3 * med, med + 4, 3 * tgt)   # a bar above this is unusual: it runs off the top
    spike = lambda v: v is not None and len(vv) >= 5 and v > cap
    top = max([v for v in vv if not spike(v)] + [avg or 0, 0.0001])
    pinned = (not lower) and tgt > 2.2 * top
    hi = max(top, 0 if pinned else tgt) * 1.12; n = len(vals); bw = (W - L - R) / n
    ys = lambda v: T + (H - T - B) * (1 - min(v, hi) / hi); g = ""
    SOFT, SOFTG = "#8a8178", "#7d8f70"
    yt = T - 12 if pinned else ys(tgt); ya = ys(avg) if avg is not None else None
    g += f'<line x1="{L}" y1="{yt:.1f}" x2="{W-R+2}" y2="{yt:.1f}" stroke="{SOFTG}" stroke-width="1.2" opacity=".8"/>'
    if ya is not None: g += f'<line x1="{L}" y1="{ya:.1f}" x2="{W-R+2}" y2="{ya:.1f}" stroke="{SOFT}" stroke-width="1.2" stroke-dasharray="5 3" opacity=".9"/>'
    for i, v in enumerate(vals):
        x = L + i * bw; last = i == n - 1
        g += f'<text x="{x+bw/2:.1f}" y="{H-B+10}" text-anchor="middle" font-size="8" font-weight="{800 if last else 600}" fill="{INK}" opacity="{.9 if last else .55}">{labels[i]}</text>'
        if v is None: continue
        col = AMBER if (lower and v > tgt) else EARTH; sp = spike(v); y0 = T - 6 if sp else ys(v)
        g += f'<rect x="{x+1.5:.1f}" y="{y0:.1f}" width="{bw-3:.1f}" height="{max(H-B-y0,1):.1f}" rx="2.5" fill="{col}" opacity="{1 if last else .34}"/>'
        if sp:
            g += f'<path d="M{x+bw/2-4:.1f},{y0-1:.1f} L{x+bw/2:.1f},{y0-6:.1f} L{x+bw/2+4:.1f},{y0-1:.1f} z" fill="{col}" opacity="{1 if last else .55}"/>'
            g += f'<text x="{x+bw/2+6:.1f}" y="{y0-1:.1f}" font-size="8.5" font-weight="800" fill="{INK}" opacity=".8" stroke="#FBF6EE" stroke-width="2.5" paint-order="stroke">{fmtv(v)}{"*" if i in marks else ""}</text>'
        else:
            g += f'<text x="{x+bw/2:.1f}" y="{ys(v)-3:.1f}" text-anchor="middle" font-size="8" font-weight="800" fill="{INK}" opacity="{1 if last else .6}" stroke="#FBF6EE" stroke-width="2.5" paint-order="stroke">{fmtv(v)}{"*" if i in marks else ""}</text>'
    if groups:
        i0 = 0
        for j in range(1, n + 1):
            if j == n or groups[j] != groups[i0]:
                xa, xb = L + i0 * bw + 2, L + j * bw - 2
                g += f'<line x1="{xa:.1f}" y1="{H-13}" x2="{xb:.1f}" y2="{H-13}" stroke="{INK}" opacity=".25"/>'
                g += f'<text x="{(xa+xb)/2:.1f}" y="{H-3}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{INK}" opacity=".6">{groups[i0]}</text>'
                i0 = j
    la, lt = ya, yt
    if ya is not None and abs(la - lt) < 21:
        mid = (ya + yt) / 2; up_a = ya <= yt
        la = mid - 10.5 if up_a else mid + 10.5; lt = mid + 10.5 if up_a else mid - 10.5
    g += f'<text x="{W-R+5}" y="{lt+3:.1f}" font-size="8.5" font-weight="700" fill="{SOFTG}">{"▲ " if pinned else ""}Target {tlab}</text>'
    if ya is not None:
        g += f'<text x="{W-R+5}" y="{la+1:.1f}" font-size="8.5" font-weight="700" fill="{SOFT}">Forecast {fmtv(avg)}</text>'
        g += f'<text x="{W-R+5}" y="{la+9.5:.1f}" font-size="6.8" font-weight="600" fill="{SOFT}">= {avgname}</text>'
    return f'<svg class="pm-ch" viewBox="0 0 {W} {H}">{g}</svg>'
def fmt1(v): return f"{v:.1f}".rstrip("0").rstrip(".")
def fhrs(v): return f"{v*60:.0f}m" if v < 1 else f"{v:.0f}h"
def chart_row(c, k, label, unit, labels, vals, tg, kids=None, marks=(), groups=None, n_avg=None, note=""):
    tv, tl = tg[c][k]; use = [v for v in (vals[-n_avg:] if n_avg else vals) if v is not None]
    avg = sum(use) / len(use) if use else None; v = vals[-1]
    if k == "fc":
        big = fmt_min(v * 60) if v is not None else "–"; f = fhrs; fc_txt = ("–" if avg is None else f"{avg*60:.0f} min" if avg < 1 else f"{avg:.0f} hrs")
    else:
        big = n0(v) if v is not None else "–"; f = fmt1; fc_txt = fmt1(avg) if avg is not None else "–"
    extra = f"{kids:g} {'child' if kids == 1 else 'children'} · " if kids else ""
    sub = f"{extra}Forecast {fc_txt} · Target {tl}" + (f"<br><i>{note}</i>" if note else "")
    ch = bars(labels, vals, avg, tv, tl, f, k in LOWER, marks, groups, "3-mth average")
    return (f'<li class="pd-r"><div class="pd-t"><b>{label}</b><span>{unit}</span></div>'
            f'<div class="pd-b"><div class="pd-n">{big}</div><div class="pd-s">{sub}</div></div>{ch}</li>')
# ---- Week: 13 complete Mon-Fri weeks ----
WE = TODAY - dt.timedelta(days=1)
while WE.weekday() != 4: WE -= dt.timedelta(days=1)
WEEKS = [[WE - dt.timedelta(days=7 * (12 - i) + 4 - j) for j in range(5)] for i in range(13)]
WLAB = f"Fri {fd(WE)}"
def week(c):
    labels = [str(w[-1].day) for w in WEEKS]; groups = [f"{w[-1]:%b}" for w in WEEKS]; marks = {i for i, w in enumerate(WEEKS) if any(d in CLOSED for d in w)}
    rows = ""
    for k, label, unit, _ in ROWS:
        note = ""
        if k == "fc":
            vals, cn = [], []
            for w in WEEKS:
                s = fc_set(c, w); got = [r[5] for r in s if r[2]]; vals.append(st.median(got) / 60 if got else None); cn.append((len(got), len(s)))
            note = f"median in work hours · {cn[-1][0]} of {cn[-1][1]} contacted"; kids = None
        else:
            vals = [ev(c, w, k) for w in WEEKS]; kids = ev(c, WEEKS[-1], k, 1) if k in ("st", "lo") else None
        rows += chart_row(c, k, label, unit, labels, vals, TGT_W, kids, marks, groups, note=note)
    note = (f'<p class="pd-note">The 13 complete Monday-to-Friday weeks to {WLAB}. The number under each bar is the Friday the week ended, with the month beneath. Dark bar = the week just closed. '
            f'Dashed line = the average of the 13 weeks, the three-month rule: this is the forecast. Grey-green line = the target; ▲ beside it means the target is above the top of the chart. A bar that runs off the top with ▲ and its number is an unusual week, kept off the scale so the other weeks stay readable. '
            f'* = a week with a closed day. Lost spots and Time to first contact are better when lower; amber bars are above target. '
            f'Time to first contact counts work hours only (8:30am to 5:30pm, Monday to Friday: an assumption, to review). '
            f'Enquiries arriving on a weekend are not yet in any week: a question to settle.</p>')
    return f'<div class="pd"><ul class="pd-l">{rows}</ul>{note}</div>'
def month(c):
    labels = [f"{dt.date.fromisoformat(m+'-01'):%b}" for m in MONTHS]; rows = ""
    for k, label, unit, _ in ROWS:
        note = ""; kids = None
        if k == "fc":
            vals, cn = [], []
            for m in MONTHS:
                s = fc_set(c, month=m); got = [r[5] for r in s if r[2]]; vals.append(st.median(got) / 60 if got else None); cn.append((len(got), len(s)))
            note = f"median in work hours · {cn[-1][0]} of {cn[-1][1]} contacted"
        else:
            vals = [MS[(c, m, k)][0] if (c, m, k) in MS else (sum(v[0] for (cc, d, kk), v in EV.items() if cc == c and kk == k and d.strftime("%Y-%m") == m) if k == "ec" and m >= "2026-04" else (None if k == "ec" else 0)) for m in MONTHS]
            kids = MS.get((c, LM, k), (0, 0))[1] if k in ("st", "lo") else None
        rows += chart_row(c, k, label, unit.replace("spots a week", "spots"), labels, vals, TGT_M, kids, n_avg=3, note=note)
    note = (f'<p class="pd-note">Complete months only, {dt.date.fromisoformat(MONTHS[0]+"-01"):%B} to {LASTM:%B %Y}; LineLeader history starts after the February import. '
            f'Dark bar = the month just closed. Dashed line = the average of the last three months, the three-month rule: this is the forecast. '
            f'Grey-green line = the target; ▲ beside it means the target is above the top of the chart. A bar that runs off the top with ▲ and its number is an unusual month, kept off the scale. Lost spots here are children who left (school leavers apart). '
            f'Time to first contact counts work hours only (8:30am to 5:30pm, Monday to Friday: an assumption, to review).</p>')
    return f'<div class="pd"><ul class="pd-l">{rows}</ul>{note}</div>'
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
      window.scrollTo(0,0); }
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
