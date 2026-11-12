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
# A week runs Saturday to Friday, so every day belongs to exactly one week (Cameron, 13 Nov 26).
LASTD = TODAY - dt.timedelta(days=1)                                   # the latest day in the data
CUR_FRI = LASTD + dt.timedelta(days=(4 - LASTD.weekday()) % 7)         # the Friday that closes the week LASTD is in
WK = [CUR_FRI - dt.timedelta(days=6 - i) for i in range(7) if CUR_FRI - dt.timedelta(days=6 - i) <= LASTD]
LW = [CUR_FRI - dt.timedelta(days=13 - i) for i in range(7)]            # the week before it, Sat..Fri
LW_OPEN = sum(workday(d) for d in LW)
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
ROWS = [("enq", "New Enquiry", "families · LineLeader", True), ("fc", "First contact in 1 hour", "share of enquiries · work hours", False),
        ("ts", "Tours Scheduled", "families · LineLeader", True), ("tc", "Tours Completed", "families · LineLeader", True),
        ("of", "Offered", "families · LineLeader", True), ("pe", "Pending", "Owna form in", True),
        ("ec", "Enrolment complete", "pulled into Owna · $50 charged", False), ("st", "Started", "spots a week · first day in Owna", False),
        ("lo", "Lost spots", "spots a week · leaving Owna, not school leavers", False)]
def n0(v): return f"{v:g}"
def arrow(y, avg):
    if abs(y - avg) < 0.5: return '<span class="pd-ar lvl">● level</span>'
    return '<span class="pd-ar up">▲ up</span>' if y > avg else '<span class="pd-ar dn">▼ down</span>'
DEF = {
 "enq": "New enquiry records in LineLeader, counted as families. Rejected records and records made after care began are left out.",
 "fc": "The share of new enquiries a person contacted (call, email, SMS or task; never LineLeader's automatic reply) within one work hour. Work hours are taken as 8:30am to 5:30pm, Monday to Friday: an assumption, to review. An enquiry outside work hours starts its clock at the next 8:30am. Enquiries nobody has contacted count as misses. Target 80%.",
 "ts": "Families who booked a tour (moved to Tour Scheduled in LineLeader): the day the booking was made, not the tour itself. A family counts once in a week. Tours ticked off after the fact are left out.",
 "tc": "Families whose tour ran, on the dashboard's Tours rule. A family counts once in a week. Tours ticked off after the fact, with no tour entry, are left out.",
 "of": "Families moved to Offered in LineLeader.",
 "pe": "Owna enrolment forms received, not yet pulled through.",
 "ec": "Children pulled into Owna, where the $50 is charged.",
 "st": "Booked days a week of the children whose first day in Owna fell in the period.",
 "lo": "Booked days a week of the children who left Owna, school leavers apart. The one measure that is better when lower: amber bars are above target."}
def det(rows):
    body = "".join(f"<p><b>{a}</b> {b}</p>" for a, b in rows if b)
    return f'<details class="pd-d"><summary>Details</summary>{body}</details>'
def y_row(c, k, label, unit, arr):
    days = [Y] + EXTRA
    if k == "fc":
        s = fc_set(c, days); got = [r for r in s if r[2]]
        big = f"{len(got)}<small>of {len(s)}</small>" if s else "–"
        sub = "contacted so far" if got else ("no new enquiries" if not s else "none contacted yet")
        lw = fc_set(c, LW); lg = [r for r in lw if r[2]]
        d = det([("Yesterday:", f"{sum(1 for r in got if r[5] <= FAST)} of {len(s)} within 1 work hour." if s else ""),
                 ("Last week:", f"{sum(1 for r in lg if r[5] <= FAST)} of {len(lw)} within 1 work hour."), ("Measure:", f"{unit}. {DEF[k]}")])
        return f'<li class="pd-r"><div class="pd-t"><b>{label}</b></div><div class="pd-b"><div class="pd-n">{big}</div><div class="pd-s">{sub}</div></div>{d}</li>'
    y = ev(c, days, k); wk = ev(c, WK, k); lw = ev(c, LW, k); avg = lw / LW_OPEN
    kids = ev(c, days, k, 1)
    a = arrow(y, avg) if arr else ""
    d = det([("Children:", f"{kids:g}." if k in ("st", "lo") and y else ""), ("Last week:", f"{n0(lw)}, or {avg:.1f} a day over {LW_OPEN} open days (week ending {fd(LW[-1])})."),
             ("Arrow:", "the day against last week's average a day; level when within half." if arr else "none: too small to read day by day."), ("Measure:", f"{unit}. {DEF[k]}")])
    return f'<li class="pd-r"><div class="pd-t"><b>{label}</b></div><div class="pd-b"><div class="pd-n">{n0(y)}</div><div class="pd-s">{n0(wk)} so far this week</div>{a}</div>{d}</li>'
def about(txt): return f'<details class="pd-d pd-about"><summary>About this view</summary><p>{txt}</p></details>'
KEY = '<p class="pd-key">Dashed = forecast (3-month average) · Green = target · ▲ = off the scale · * = closed day</p>'
def yesterday(c):
    w, out, inh = waiting(c)
    wl = (f'<div class="pd-wait{" on" if w else ""}"><b>Waiting for first contact: {w}</b>'
          + (f'<span>{out} overnight or weekend · {inh} in work hours</span>' if w else '') + '</div>')
    rows = "".join(y_row(c, *r) for r in ROWS)
    note = about(f'What happened on {YLAB}, as recorded by this morning. ▲ ▼ ● compares the day with last week\'s average a day '
                 f'(week ending {fd(LW[-1])}, its total over {LW_OPEN} open days). No arrow on the rows that are too small to read day by day. '
                 f'Waiting for first contact counts enquiries of the last 30 days still at New Enquiry with no contact by a person; when it is 0, every new enquiry has been contacted or moved on. '
                 f'Work hours for answering enquiries are taken as 8:30am to 5:30pm, Monday to Friday: an assumption, to review.')
    return f'<div class="pd">{wl}<ul class="pd-l">{rows}</ul>{note}</div>'
# ---- Month ----
MS = {}
for c, p, k, n, x in P.M: MS[(c, p, k)] = (n, x)
LASTM = (TODAY.replace(day=1) - dt.timedelta(days=1)); LM = LASTM.strftime("%Y-%m")
MONTHS = sorted({p for (c, p, k) in MS if "2026-03" <= p <= LM})
MLAB = f"{LASTM.day} {LASTM:%b %y}"
GREEN = "#4d6a3a"
TGT_W = {"South Morang": dict(enq=(7,"7"), fc=(80,"80%"), ts=(5.5,"5–6"), tc=(5.5,"5–6"), of=(5.5,"5–6"), pe=(2.5,"2–3"), ec=(2.5,"2–3"), st=(7,"7"), lo=(2.1,"2.1")),
         "Craigieburn":  dict(enq=(35,"35"), fc=(80,"80%"), ts=(23,"23"), tc=(23,"23"), of=(23,"23"), pe=(11,"11"), ec=(11,"11"), st=(33,"33"), lo=(2.1,"2.1"))}
TGT_M = {"South Morang": dict(enq=(31,"31"), fc=(80,"80%"), ts=(24,"24"), tc=(24,"24"), of=(24,"24"), pe=(11,"11"), ec=(11,"11"), st=(30,"30"), lo=(9,"9")),
         "Craigieburn":  dict(enq=(150,"150"), fc=(80,"80%"), ts=(100,"100"), tc=(100,"100"), of=(100,"100"), pe=(48,"48"), ec=(48,"48"), st=(143,"143"), lo=(9,"9"))}
LOWER = {"lo"}
FAST = 60   # work minutes: the cut-off for a fast first contact (Cameron, 13 Nov 26); target 80%
def fc_stats(s):
    n = len(s); got = [r for r in s if r[2]]
    if not n: return None, ""
    w60 = sum(1 for r in got if r[5] <= FAST); w10 = sum(1 for r in got if r[5] <= 10)
    med = f" · median {plain(st.median(r[5] for r in got))}" if got else ""
    return 100 * w60 / n, f"{w60} of {n} enquiries · within 10 min {100*w10/n:.0f}%{med}"
def bars(labels, vals, avg, tgt, tlab, fmtv=lambda v: f"{v:g}", lower=False, marks=(), groups=None, avgname="3-mth average", pct=False, fname="Forecast", zoom=False, ghost=0, fill=None, refs=None):
    fill = fill or {}; refs = refs or {}
    W, H, L, R, T, B = 340, (124 if groups else 112), 4, 84, 22, (28 if groups else 16)
    vv = sorted(v for v in vals if v is not None)
    med = vv[len(vv) // 2] if vv else 0
    cap = max(3 * med, med + 4) if not (lower and tgt is not None) else max(3 * med, med + 4, 3 * tgt)   # a bar above this is unusual: it runs off the top
    spike = lambda v: (not pct) and v is not None and len(vv) >= 5 and v > cap
    top = max([v for v in vv if not spike(v)] + [avg or 0, 0.0001])
    pinned = tgt is not None and (not lower) and (not pct) and tgt > 2.2 * top
    hi = 104 if pct else max(top, 0 if (pinned or tgt is None) else tgt) * 1.12; n = len(vals); bw = (W - L - R) / n
    base = 0
    if zoom and vv:
        lowv = min([v for v in vv] + [x for x in (avg, None if pinned else tgt) if x is not None]); base = lowv - (hi - lowv) * 0.6
        if base < 0: base = 0
    ys = lambda v: T + (H - T - B) * (1 - (min(v, hi) - base) / (hi - base)); g = ""
    SOFT, SOFTG = "#8a8178", "#7d8f70"
    yt = None if tgt is None else (T - 12 if pinned else ys(tgt)); ya = ys(avg) if avg is not None else None
    if yt is not None: g += f'<line x1="{L}" y1="{yt:.1f}" x2="{W-R+2}" y2="{yt:.1f}" stroke="{SOFTG}" stroke-width="1.2" opacity=".8"/>'
    if ya is not None: g += f'<line x1="{L}" y1="{ya:.1f}" x2="{W-R+2}" y2="{ya:.1f}" stroke="{SOFT}" stroke-width="1.2" stroke-dasharray="5 3" opacity=".9"/>'
    for i, v in enumerate(vals):
        x = L + i * bw; last = i == n - 1 - ghost; gh = i >= n - ghost
        g += f'<text x="{x+bw/2:.1f}" y="{H-B+10}" text-anchor="middle" font-size="8" font-weight="{800 if last else 600}" fill="{INK}" opacity="{.9 if last else .55}">{labels[i]}</text>'
        if v is None: continue
        col = AMBER if (lower and tgt is not None and v > tgt) else EARTH; sp = spike(v); y0 = T - 6 if sp else ys(v)
        if gh:
            g += f'<rect x="{x+2:.1f}" y="{y0:.1f}" width="{bw-4:.1f}" height="{max(H-B-y0,1):.1f}" rx="2.5" fill="none" stroke="{EARTH}" stroke-width="1.3" stroke-dasharray="3 2.5" opacity=".8"/>'
            if i in fill and fill[i]:
                yf = max(ys(fill[i]), y0); g += f'<rect x="{x+2:.1f}" y="{yf:.1f}" width="{bw-4:.1f}" height="{max(H-B-yf,1):.1f}" rx="2" fill="{EARTH}" opacity=".5"/>'
            if i in refs:
                yr = ys(refs[i]); g += f'<line x1="{x+1:.1f}" y1="{yr:.1f}" x2="{x+bw-1:.1f}" y2="{yr:.1f}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="1.5 2.5" opacity=".75"/>'
            g += f'<text x="{x+bw/2:.1f}" y="{y0-3:.1f}" text-anchor="middle" font-size="8" font-weight="800" fill="{INK}" opacity=".8" stroke="#FBF6EE" stroke-width="2.5" paint-order="stroke">{fmtv(v)}{"*" if i in marks else ""}</text>'
            continue
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
    if ya is not None and yt is not None and abs(la - lt) < 21:
        mid = (ya + yt) / 2; up_a = ya <= yt
        la = mid - 10.5 if up_a else mid + 10.5; lt = mid + 10.5 if up_a else mid - 10.5
    if yt is not None: g += f'<text x="{W-R+5}" y="{lt+3:.1f}" font-size="8.5" font-weight="700" fill="{SOFTG}">{"▲ " if pinned else ""}Target {tlab}</text>'
    if ya is not None:
        g += f'<text x="{W-R+5}" y="{la+1:.1f}" font-size="8.5" font-weight="700" fill="{SOFT}">{fname} {fmtv(avg)}</text>'
        g += f'<text x="{W-R+5}" y="{la+9.5:.1f}" font-size="6.8" font-weight="600" fill="{SOFT}">= {avgname}</text>'
    return f'<svg class="pm-ch" viewBox="0 0 {W} {H}">{g}</svg>'
def fmt1(v): return f"{v:.1f}".rstrip("0").rstrip(".")
def fhrs(v): return f"{v*60:.0f}m" if v < 1 else f"{v:.0f}h"
def chart_row(c, k, label, unit, labels, vals, tg, kids=None, marks=(), groups=None, n_avg=None, note="", avg_over=None):
    tv, tl = tg[c][k]; use = [v for v in (vals[-n_avg:] if n_avg else vals) if v is not None]
    avg = avg_over if avg_over is not None else (sum(use) / len(use) if use else None); v = vals[-1]
    if k == "fc":
        f = lambda x: f"{x:.0f}%"; big = f"{v:.0f}<small>%</small>" if v is not None else "–"; fc_txt = f(avg) if avg is not None else "–"
    else:
        big = n0(v) if v is not None else "–"; f = fmt1; fc_txt = fmt1(avg) if avg is not None else "–"
    sub = f"Forecast {fc_txt} · Target {tl}"
    ch = bars(labels, vals, avg, tv, tl, f, k in LOWER, marks, groups, "3-mth average", pct=(k == "fc"))
    d = det([("Children:", f"{kids:g}." if kids else ""), ("This period:", note + "." if note else ""), ("Measure:", f"{unit}. {DEF[k]}"),
             ("Forecast:", "the three-month average" + (", taken as the share over the whole window." if k == "fc" else "; an unusual bar still counts in it."))])
    return (f'<li class="pd-r"><div class="pd-t"><b>{label}</b></div>'
            f'<div class="pd-b"><div class="pd-n">{big}</div><div class="pd-s">{sub}</div></div>{ch}{d}</li>')
# ---- Against the industry average (LineLeader 2026 ECE Benchmark Report; its customers, not labelled by country; under review) ----
import tours_build as _tr
IND = [("Enquiries that book a tour", 60), ("Booked tours that happen", 75), ("Toured families who enrol", 40)]
def industry(c, e, ts, tc, window):
    ours = [100 * ts / e if e else None, 100 * tc / ts if ts else None, float(_tr.CENTRE_PCT[c])]
    rows = ""
    for (lab, ind), o in zip(IND, ours):
        col = "#8a8178" if o is None else (SAGE if o >= ind else EARTH)
        txt = "–" if o is None else ("100%" if o > 100 else f"{o:.0f}%")
        rows += f'<tr><td>{lab}</td><td style="color:{col}"><b>{txt}</b></td><td>{ind}%</td></tr>'
    d = det([("Ours:", f"the first two rows cover {window}: {ts:g} tours booked from {e:g} enquiries, and {tc:g} tours completed against {ts:g} booked" + (" (walk-in tours are completed without a booking, so this can pass 100%)" if tc > ts else "") + ". The third row is the Tours screen's figure for the last 12 months."),
             ("Industry average:", "LineLeader's 2026 ECE Benchmark Report: about 60% of enquiries book a tour, 75% of booked tours happen, and enrolment after a tour is trending toward 40%. These are LineLeader's own customers (over 5,700 operators), mostly in the United States; the report does not give Australian figures."),
             ("Status:", "under review. We are checking for Australian figures before treating these as our benchmark.")])
    return (f'<div class="pd-ind"><div class="pd-indh">Against the industry average <span>under review</span></div>'
            f'<table><tr><th></th><th>Ours</th><th>Industry</th></tr>{rows}</table>{d}</div>')
# ---- Week: 13 complete Sat-Fri weeks ----
WE = TODAY - dt.timedelta(days=1)
while WE.weekday() != 4: WE -= dt.timedelta(days=1)
WEEKS = [[WE - dt.timedelta(days=7 * (12 - i) + 6 - j) for j in range(7)] for i in range(13)]   # Sat..Fri
WLAB = f"Fri {fd(WE)}"
def week(c):
    labels = [str(w[-1].day) for w in WEEKS]; groups = [f"{w[-1]:%b}" for w in WEEKS]; marks = {i for i, w in enumerate(WEEKS) if any(d in CLOSED for d in w)}
    rows = ""
    for k, label, unit, _ in ROWS:
        note = ""
        avg_over = None
        if k == "fc":
            vals = [fc_stats(fc_set(c, w))[0] for w in WEEKS]; note = fc_stats(fc_set(c, WEEKS[-1]))[1] or "no new enquiries this week"; kids = None
            avg_over = fc_stats(fc_set(c, [d for w in WEEKS for d in w]))[0]
        else:
            vals = [ev(c, w, k) for w in WEEKS]; kids = ev(c, WEEKS[-1], k, 1) if k in ("st", "lo") else None
        rows += chart_row(c, k, label, unit, labels, vals, TGT_W, kids, marks, groups, note=note, avg_over=avg_over)
    m3 = lambda k: sum(MS.get((c, m, k), (0, 0))[0] for m in MONTHS[-3:])
    note = industry(c, m3("enq"), m3("ts"), m3("tc"), "the last three complete months") + KEY + about(f'The 13 complete weeks to {WLAB}. A week runs Saturday to Friday, so weekend enquiries count in the week the team deals with them. '
                       f'The number under each bar is the Friday the week ended, with the month beneath. Dark bar = the week just closed. '
                       f'Dashed line = the average of the 13 weeks, the three-month rule: this is the forecast. Grey-green line = the target; ▲ beside it means the target is above the top of the chart. '
                       f'A bar that runs off the top with ▲ and its number is an unusual week, kept off the scale so the other weeks stay readable. * = a week with a closed day.')
    return f'<div class="pd"><ul class="pd-l">{rows}</ul>{note}</div>'
def month(c):
    labels = [f"{dt.date.fromisoformat(m+'-01'):%b}" for m in MONTHS]; rows = ""
    for k, label, unit, _ in ROWS:
        note = ""; kids = None
        avg_over = None
        if k == "fc":
            vals = [fc_stats(fc_set(c, month=m))[0] for m in MONTHS]; note = fc_stats(fc_set(c, month=LM))[1]
            avg_over = fc_stats([r for m in MONTHS[-3:] for r in fc_set(c, month=m)])[0]
        else:
            vals = [MS[(c, m, k)][0] if (c, m, k) in MS else (sum(v[0] for (cc, d, kk), v in EV.items() if cc == c and kk == k and d.strftime("%Y-%m") == m) if k == "ec" and m >= "2026-04" else (None if k == "ec" else 0)) for m in MONTHS]
            kids = MS.get((c, LM, k), (0, 0))[1] if k in ("st", "lo") else None
        rows += chart_row(c, k, label, unit.replace("spots a week", "spots"), labels, vals, TGT_M, kids, n_avg=3, note=note, avg_over=avg_over)
    m3 = lambda k: sum(MS.get((c, m, k), (0, 0))[0] for m in MONTHS[-3:])
    note = industry(c, m3("enq"), m3("ts"), m3("tc"), "the last three complete months") + KEY + about(f'Complete months only, {dt.date.fromisoformat(MONTHS[0]+"-01"):%B} to {LASTM:%B %Y}; LineLeader history starts after the February import. '
                       f'Dark bar = the month just closed. Dashed line = the average of the last three months, the three-month rule: this is the forecast. '
                       f'Grey-green line = the target; ▲ beside it means the target is above the top of the chart. A bar that runs off the top with ▲ and its number is an unusual month, kept off the scale. '
                       f'Lost spots here are children who left (school leavers apart).')
    return f'<div class="pd"><ul class="pd-l">{rows}</ul>{note}</div>'

# ---- Forecast: the next months on the three-month rule (draft) ----
FM = []   # forecast months: the month we are in, then on to February
_d = TODAY.replace(day=1)
while True:
    FM.append(_d)
    if _d.month == 2: break
    _d = (_d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
FLAB = f"{FM[0]:%b} to {FM[-1]:%b %y}"
FKEY = '<p class="pd-key">Solid = actual · Outlined = forecast · Green = target</p>'
def fmonths(): return [f"{dt.date.fromisoformat(m+'-01'):%b}" for m in MONTHS[-3:]] + [f"{d:%b}" for d in FM]
def forecast(c):
    labels = fmonths(); grp = ["Actual"] * 3 + ["Forecast"] * len(FM); rows = ""
    mtd_days = [TODAY.replace(day=1) + dt.timedelta(days=i) for i in range((TODAY - TODAY.replace(day=1)).days)]
    for k, label, unit, _ in ROWS:
        if k not in ("enq", "tc", "ec"): continue
        act = [MS.get((c, m, k), (0, 0))[0] for m in MONTHS[-3:]]; avg = sum(act) / 3; mtd = ev(c, mtd_days, k)
        tv, tl = TGT_M[c][k]
        ch = bars(labels, act + [avg] * len(FM), None, tv, tl, fmt1, False, (), grp, ghost=len(FM), fill={3: mtd})
        d = det([(f"{FM[0]:%B} so far:", f"{mtd:g} to {fd(TODAY - dt.timedelta(days=1))}, shown as the filled part of the {FM[0]:%b} bar."),
                 ("Forecast:", f"the average of the last three complete months ({', '.join(labels[:3])}), held for each month ahead. This is the forecast model's three-month rule; no growth and no seasonal dip is added."),
                 ("Target:", f"{tl} a month."), ("Measure:", f"{unit}. {DEF[k]}")])
        rows += (f'<li class="pd-r"><div class="pd-t"><b>{label}</b></div><div class="pd-b"><div class="pd-n">{fmt1(avg)}<small> a month</small></div>'
                 f'<div class="pd-s">Forecast · Target {tl} · {FM[0]:%b} so far {mtd:g}</div></div>{ch}{d}</li>')
    note = FKEY + about(f'{FLAB}, by month. The forecast is the three-month rule: what the last three complete months averaged, carried forward. '
                        f'The forecast model starts families who enquire in October, November and December in February, so these enquiries show up in February occupancy, not before. '
                        f'December and January are usually quieter; the rule does not allow for that.')
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
.pd-key{font-size:11px;font-weight:700;color:rgba(43,35,32,.55);margin:12px 0 2px;text-align:center}
.pd-d{margin-top:4px}.pd-d summary{font-size:11.5px;font-weight:800;color:rgba(43,35,32,.5);cursor:pointer;list-style:none;display:inline-block;padding:3px 0}
.pd-d summary::-webkit-details-marker{display:none}.pd-d summary::before{content:"▸ "}.pd-d[open] summary::before{content:"▾ "}
.pd-d p{font-size:12px;line-height:1.45;color:rgba(43,35,32,.72);margin:4px 0 0}.pd-d p b{color:#2b2622}
.pd-about{margin-top:10px}
.pd-ind{margin:14px 0 4px;padding:12px 14px;border-radius:14px;background:rgba(43,35,32,.045)}
.pd-indh{font-family:"Fredoka","Nunito",sans-serif;font-weight:600;font-size:16px;margin-bottom:4px}
.pd-indh span{font-family:"Nunito",sans-serif;font-size:10px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#7a3f17;border:1.5px solid #7a3f17;border-radius:6px;padding:1px 6px;margin-left:6px;position:relative;top:-2px}
.pd-ind table{width:100%;border-collapse:collapse;font-size:13px}.pd-ind th{font-size:10.5px;font-weight:800;color:rgba(43,35,32,.5);text-align:right;padding:2px 0}
.pd-ind td{padding:5px 0;border-top:1px solid rgba(43,35,32,.08);font-weight:700}.pd-ind td:nth-child(n+2){text-align:right;width:70px;font-size:15px}.pd-ind td:nth-child(3){color:rgba(43,35,32,.6)}
.pm-ch{display:block;width:100%;height:auto;margin-top:6px}
"""
js = """
  (function(){ var c='sm', p='w';
    function show(){ ['sm','cb'].forEach(function(a){ ['d','w','m','f'].forEach(function(b){ var e=document.getElementById('pf-'+a+'-'+b); if(e) e.hidden=!(a===c&&b===p); }); });
      var s=document.getElementById('pf-sub'); if(s) s.textContent=s.getAttribute('data-'+p);
      window.scrollTo(0,0); }
    Array.prototype.slice.call(document.querySelectorAll('.toggle.pf button')).forEach(function(t){ t.addEventListener('click', function(){ c=t.dataset.pf==='pf-cb'?'cb':'sm'; show(); }); });
    var pt=Array.prototype.slice.call(document.querySelectorAll('.pdtabs button'));
    pt.forEach(function(t){ t.addEventListener('click', function(){ pt.forEach(function(x){ x.setAttribute('aria-selected', x===t?'true':'false'); }); p=t.dataset.pd; show(); }); });
  })();
"""
if __name__ == "__main__":
    print("Y", Y, "extra", EXTRA, "wk", WK[0], WK[-1], "lw", LW[0], LW[-1], LW_OPEN, "weeks", WEEKS[0][0], WEEKS[-1][-1], "months", MONTHS)
    for c in CENTRES:
        print(c, "waiting", waiting(c))
        for k, lab, u, a in ROWS:
            if k != "fc": print("  ", k, ev(c, [Y] + EXTRA, k), "wk", ev(c, WK, k), "lw", ev(c, LW, k), "| Oct", MS.get((c, LM, k)))
        for wd, nm in ((LW, "lw"), (WK, "wk")):
            s = fc_set(c, wd); g = [r for r in s if r[2]]
            print("  fc", nm, len(g), len(s), "fair", round(st.median(r[5] for r in g)) if g else None, "raw", round(st.median(r[4] for r in g)) if g else None)
