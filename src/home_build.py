"""New home screen (architecture v0.4). Run after billy_build.py: python3 home_build.py <built.html> <out.html>.
Replaces the home tiles with Yesterday, Enquiries, Pipeline, Occupancy, Wages and To fix; the detail screens stay as built."""
import sys, re, json, datetime as dt, pathlib
from collections import defaultdict
SRC = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(SRC)); sys.path.insert(0, str(SRC/'kpi'))
import pipe as P, enrolled as EN, pending_followup as PFm
FEED = json.load(open(SRC/'kpi/model_feed.json'))
built = open(sys.argv[1]).read()
CSS = re.search(r'<style[^>]*>(.*?)</style>', built, re.S).group(1)
INK, EARTH, SAGE, YEL, SKY, GREY = "#2b2622", "#A45823", "#6E8B57", "#FDC546", "#5E80A0", "#9b948c"
CEN = [("sm", "South Morang", 108), ("cb", "Craigieburn", 174)]
# ---------- events
EV = defaultdict(lambda: [0.0, 0.0])
for c, d, k, n, x in P.D:
    e = EV[(c, dt.date.fromisoformat(d), k)]; e[0] += n; e[1] += x
DAY = max(dt.date.fromisoformat(d) for _, d, *r in P.D)
while DAY.weekday() > 4: DAY -= dt.timedelta(1)
WK = [DAY - dt.timedelta(DAY.weekday()) + dt.timedelta(i) for i in range(DAY.weekday() + 1)]
def ev(c, days, k, j=0): return sum(EV[(c, d, k)][j] for d in days)
# ---------- yesterday
def yday(c):
    pe_f, pe_s = ev(c, [DAY], 'pe'), ev(c, [DAY], 'pe', 1)
    st_s, st_c = ev(c, [DAY], 'st'), ev(c, [DAY], 'st', 1)
    lo_s, lo_c = ev(c, [DAY], 'lo'), ev(c, [DAY], 'lo', 1)
    wk = ev(c, WK, 'pe', 1) + ev(c, WK, 'st') - ev(c, WK, 'lo')
    return dict(pe=(pe_f, pe_s), st=(st_c, st_s), lo=(lo_c, lo_s), net=pe_s + st_s - lo_s, wk=wk,
                enq=ev(c, [DAY], 'enq'), tc=ev(c, [DAY], 'tc'), ts=ev(c, [DAY], 'ts'), of=ev(c, [DAY], 'of'))
Yd = {k: yday(n) for k, n, _ in CEN}
def verdict(net, gains, losses):
    if gains == 0 and losses == 0: return "Quiet day", "#8a837b"
    if net > 0 and losses == 0: return "Good day", SAGE
    if net >= 0: return "Mixed day", "#b07d10"
    return "Tough day", "#a33a2a"
def yd_card():
    tot = sum(v['net'] for v in Yd.values()); gains = sum(v['pe'][1] + v['st'][1] for v in Yd.values()); loss = sum(v['lo'][1] for v in Yd.values())
    def block(scope, vals, label):
        net = sum(v['net'] for v in vals); g = sum(v['pe'][1] + v['st'][1] for v in vals); l = sum(v['lo'][1] for v in vals)
        vt, col = verdict(net, g, l)
        pe_f = sum(v['pe'][0] for v in vals); pe_s = sum(v['pe'][1] for v in vals)
        st_c = sum(v['st'][0] for v in vals); st_s = sum(v['st'][1] for v in vals)
        lo_c = sum(v['lo'][0] for v in vals); lo_s = sum(v['lo'][1] for v in vals)
        wk = sum(v['wk'] for v in vals); enq = sum(v['enq'] for v in vals); ts = sum(v['ts'] for v in vals); tc = sum(v['tc'] for v in vals)
        split = "" if scope != "both" else f' <span class="mk-sub">(SM {Yd["sm"]["net"]:+g}, CB {Yd["cb"]["net"]:+g})</span>'
        rows = (f'<tr><td>{'✅' if enq else '◦'} New enquiries</td><td>{enq:g}</td><td></td></tr>'
                f'<tr><td>{'✅' if tc else '◦'} Tours completed</td><td>{tc:g}</td><td></td></tr>'
                f'<tr><td>{'✅' if pe_s else '◦'} New pending <small>forms in</small></td><td>{pe_f:g}</td><td class="{"pos" if pe_s else ""}">{("+%g" % pe_s) if pe_s else "0"}</td></tr>'
                f'<tr><td>{'✅' if st_s else '◦'} Pending → enrolled <small>started</small></td><td>{st_c:g}</td><td class="{"pos" if st_s else ""}">{("+%g" % st_s) if st_s else "0"}</td></tr>'
                f'<tr><td>{'⚠️' if lo_s else '◦'} Left</td><td>{lo_c:g}</td><td class="{"neg" if lo_s else ""}">{("−%g" % lo_s) if lo_s else "0"}</td></tr>'
                f'<tr class="tot"><td>Net for the day{split}</td><td></td><td>{("%+g" % net) if net else "0"}</td></tr>')
        qn = ('<p class="mk-tag">Nothing recorded. The admin team works only part of the week (days to confirm with Robyn), '
              'and offers, forms moved into Owna and leaver notices are recorded on the days they work, so a quiet day may be a day off rather than no activity.</p>') if vt == "Quiet day" else ""
        return (f'<div class="mk-c {scope}"><div class="mk-status"><b style="color:{col}">{vt}:</b> {("%+g" % net) if net else "0"} spot{'' if abs(net)==1 else 's'}.</div>'
                f'<table class="mk-t"><tr><th></th><th>Families</th><th>Spots</th></tr>{rows}</table>'
                + qn + f'<p class="mk-foot">This week so far: <b>{("%+g" % wk) if wk else "0"} spots</b> · Also: {ts:g} tour{'' if ts==1 else 's'} booked.</p></div>')
    body = "".join(block(k, [Yd[k]], n) for k, n, _ in CEN)
    LAB = [("enq", "Enquiries", 0, "✅"), ("tc", "Tours completed", 0, "✅"), ("ts", "Tours booked", 0, "✅"), ("of", "Offers made", 0, "✅"),
           ("pe", "Enrolment forms in", 1, "✅"), ("ec", "Moved into Owna", 0, "✅"), ("st", "Started", 1, "✅"), ("lo", "Left", 1, "⚠️")]
    ex = ""
    for k, name, _ in CEN:
        wins, watch = [], []
        for code, lab, sp, ic in LAB:
            n = ev(name, [DAY], code); x = ev(name, [DAY], code, 1) if sp else 0
            if code == "st": n, x = ev(name, [DAY], code, 1), ev(name, [DAY], code)
            if not n: continue
            lab2 = lab
            line = f'{ic} {lab2}: <b>{n:g}</b>' + (f' · {x:g} spot{"" if x == 1 else "s"}' if x else "")
            (watch if code == "lo" else wins).append(line)
        pf = PFm.PF[name]; past = pf.get("past", (0, 0))[0]
        if past: watch.append(f"⚠️ Pending past their start date: <b>{past}</b>")
        ex += (f'<div class="mk-c {k}"><div class="mk-sublbl">Wins</div><ul class="mk-ul">{"".join("<li>"+w+"</li>" for w in wins) or "<li>None recorded.</li>"}</ul>'
               f'<div class="mk-sublbl">Watch</div><ul class="mk-ul">{"".join("<li>"+w+"</li>" for w in watch) or "<li>Nothing to watch.</li>"}</ul>'
               f'<p class="mk-foot">Leaver reasons and families by code are not in the data yet (requested from Dima).</p></div>')
    return card("Yesterday", f"{DAY:%a} {DAY.day} {DAY:%b}", body, expand=ex)
# ---------- occupancy
CL = {"sm": [76.8, 75.8, 79.1, 79.4], "cb": [33.4, 32.7, 33.3, 34.7]}   # closing week Jul–Oct 26, certified
def occ_svg(k, name, places, big):
    fc = FEED["centres"][name]["monthly_closing"]; bc = fc["occupancy_pct"]["base_case"]
    f_ = fc["occupancy_incl_sessional_pct"]["forecast"]; t_ = fc["occupancy_incl_sessional_pct"]["target"]
    now = 100 * (EN.E[name][1] + EN.CAS[name]) / (places * 5)
    labs = ["Jul", "Aug", "Sep", "Oct", "Today"] + FEED["months"][1:]
    act = CL[k] + [now]; n = len(labs)
    W, H, L, R, T, B = 340, (170 if big else 120), 26, 30, 14, 18
    allv = act + bc + f_ + t_; lo = max(0, min(allv) - 8); hi = max(allv) + 6
    X = lambda i: L + (W - L - R) * i / (n - 1); Yv = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    def path(pts, col, w=2.2, dash=""):
        d = " ".join(f"{'M' if j==0 else 'L'}{X(i):.1f},{Yv(v):.1f}" for j, (i, v) in enumerate(pts))
        return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" {dash} stroke-linejoin="round"/>'
    i0 = 4
    g = f'<rect x="{X(i0):.1f}" y="{T}" width="{W-R-X(i0):.1f}" height="{H-T-B}" fill="{INK}" opacity=".035"/>'
    for v in range(int(lo // 10 * 10 + 10), int(hi), 10):
        g += f'<line x1="{L}" x2="{W-R}" y1="{Yv(v):.1f}" y2="{Yv(v):.1f}" stroke="{INK}" opacity=".08"/><text x="{L-4}" y="{Yv(v)+3:.1f}" font-size="8" text-anchor="end" fill="{INK}" opacity=".5">{v}%</text>'
    fut = list(range(i0 + 1, n))
    g += path([(i0, now)] + [(i, t_[i - i0]) for i in fut], SAGE, 2, 'stroke-dasharray="4 3"')
    g += path([(i0, now)] + [(i, f_[i - i0]) for i in fut], "#d9a400", 2, 'stroke-dasharray="4 3"')
    g += path([(i0, now)] + [(i, bc[i - i0]) for i in fut], EARTH, 2.2)
    g += path([(i, v) for i, v in enumerate(act)], INK, 2.6)
    g += f'<circle cx="{X(i0):.1f}" cy="{Yv(now):.1f}" r="3.5" fill="{INK}"/><text x="{X(i0):.1f}" y="{Yv(now)-7:.1f}" font-size="10" font-weight="800" text-anchor="middle" fill="{INK}">{now:.1f}</text>'
    for v, col in ((t_[-1], "#4d6b3c"), (f_[-1], "#9a7300"), (bc[-1], EARTH)):
        g += f'<text x="{X(n-1)+3:.1f}" y="{Yv(v)+3:.1f}" font-size="9" font-weight="800" fill="{col}">{v:.0f}</text>'
    jan = labs.index("Jan"); g += f'<text x="{X(jan):.1f}" y="{Yv(bc[jan-i0])+12:.1f}" font-size="8.5" text-anchor="middle" fill="{EARTH}">{bc[jan-i0]:.0f}</text>'
    for i, lab in enumerate(labs):
        if big or lab in ("Jul", "Today", "Jan", "Jun"):
            g += f'<text x="{X(i):.1f}" y="{H-4}" font-size="8.5" text-anchor="middle" fill="{INK}" opacity=".7" font-weight="{800 if lab=="Today" else 500}">{lab}</text>'
    return f'<svg viewBox="0 0 {W} {H}" class="mk-svg">{g}</svg>', now, bc, f_, t_
def occ_card():
    body = ""
    for scope in ("sm", "cb"):
        items = CEN if scope == "both" else [c for c in CEN if c[0] == scope]
        inner = ""
        for k, name, pl_ in items:
            svg, now, bc, f_, t_ = occ_svg(k, name, pl_, scope != "both")
            jan = bc[2]
            inner += (f'<div class="mk-row"><div class="mk-status">{"<b>"+name+"</b> · " if scope=="both" else ""}Up from {CL[k][0]:.1f}% in July to <b>{now:.1f}%</b> today. '
                      f'Dips to {jan:.0f}% in January (school leavers). June: Forecast {f_[-1]:.0f}%, Target {t_[-1]:.0f}%.</div>{svg}</div>')
        body += f'<div class="mk-c {scope}">{inner}</div>'
    leg = (f'<div class="mk-leg"><span><i style="background:{INK}"></i>Actual</span><span><i style="background:{EARTH}"></i>Base Case</span>'
           f'<span><i style="background:#d9a400"></i>Forecast (12-week trend)</span><span><i style="background:{SAGE}"></i>Target</span></div>')
    ex = ""
    for k, name, places in CEN:
        en, es, nn, ns = EN.E[name]; ca = EN.CAS[name]; cap = places * 5
        fc = FEED["centres"][name]["monthly_closing"]; fl = FEED["centres"][name]["flows_monthly"]
        bc = fc["occupancy_pct"]["base_case"]; f_ = fc["occupancy_incl_sessional_pct"]["forecast"]; t_ = fc["occupancy_incl_sessional_pct"]["target"]
        bce = bc[0] * cap / 100; started = es - ns
        br = (f'<tr><td>Enrolled today, incl. starting soon and casuals</td><td>{es+ca:.0f}</td><td><b>{100*(es+ca)/cap:.1f}%</b></td></tr>'
              f'<tr><td>less casual days last week ({EN.CAS_WEEK})</td><td>−{ca:.0f}</td><td></td></tr>'
              f'<tr><td>less enrolled, not yet started ({nn} children)</td><td>−{ns:.0f}</td><td></td></tr>'
              f'<tr class="tot"><td>Enrolled and started, today</td><td>{started:.0f}</td><td>{100*started/cap:.1f}%</td></tr>'
              f'<tr><td>rest of {FEED["months"][0]} in the model (starts, leavers, extra days, casual)</td><td>{bce-started:+.0f}</td><td></td></tr>'
              f'<tr class="tot"><td>Base Case, end of {FEED["months"][0]}</td><td>{bce:.0f}</td><td>{bc[0]:.1f}%</td></tr>')
        mr = ""
        for i, mo in enumerate(FEED["months"]):
            ps = fl["pending_starts"][i]; sl = fl["school_leavers"][i]
            mr += f'<tr><td>{mo}</td><td>{bc[i]:.0f}%</td><td>{f_[i]:.0f}%</td><td>{t_[i]:.0f}%</td><td>{("+%g" % ps) if ps else "–"}</td><td>{("−%g" % sl) if sl else "–"}</td></tr>'
        ex += (f'<div class="mk-c {k}"><div class="mk-sublbl">From today to the model (provisional)</div>'
               f'<table class="mk-t"><tr><th></th><th>Spots</th><th>%</th></tr>{br}</table>'
               f'<p class="mk-foot">Spots a week out of {cap} ({places} places × 5). Today from Owna (Dashboard {EN.SNAP[:10]}); Base Case from Financial Model {FEED["version"]}.</p>'
               f'<div class="mk-sublbl">Month by month to June</div>'
               f'<table class="mk-t mk-src"><tr><th>End of</th><th>Base</th><th>Fcst</th><th>Target</th><th>Starting</th><th>School leavers</th></tr>{mr}</table>'
               f'<p class="mk-foot"><b>Base Case</b>: this week’s permanent spots, less leavers and fewer days at the last 12 weeks’ rate, plus extra days, less school leavers, plus casual, plus pending families on their Owna start date. '
               f'<b>Forecast (12-week trend)</b>: Base Case plus new enrolments from enquiries at the last 12 weeks’ rate, plus sessional kinder from February. '
               f'<b>Target</b>: Forecast plus the extra spots to reach South Morang 85% and Craigieburn 70% (incl. sessional kinder) by June. Starting and school leavers are Base Case spots in that month.</p></div>')
    return card("Occupancy", "As Owna shows it, with the model to June", body + leg + '<p class="mk-tag">Financial Model v3.2 · working draft · Target incl. sessional kinder</p>', expand=ex)
# ---------- pipeline
def wk_tot(c, k, monday, j=0): return sum(ev(c, [monday + dt.timedelta(i)], k, j) for i in range(7))
LASTMON = DAY - dt.timedelta(DAY.weekday() + 7)
ROWS = [("enq", "Enquiries", 0), ("ts", "Tours booked", 0), ("pe", "Pending (forms in)", 0), ("st", "Started (spots)", 0), ("lo", "Left (spots)", 0)]
def word(v, avg, lower=False):
    if avg == 0: return "steady", "lvl"
    r = v / avg
    up = r >= 1.15; dn = r <= 0.85
    if lower: return ("fewer than usual", "up") if dn else ("more than usual", "dn") if up else ("about usual", "lvl")
    return ("building", "up") if up else ("declining", "dn") if dn else ("steady", "lvl")
def pipe_card():
    body = ""
    for scope in ("sm", "cb"):
        items = CEN if scope == "both" else [c for c in CEN if c[0] == scope]
        inner = ""
        for k, name, _ in items:
            rows = ""; key = None
            for code, lab, j in ROWS:
                v = wk_tot(name, code, LASTMON, j); prior = [wk_tot(name, code, LASTMON - dt.timedelta(7 * i), j) for i in range(1, 13)]
                avg = sum(prior) / 12; w, cls = word(v, avg, code == "lo")
                if code == "pe": key = (w, v, avg)
                if code == "enq": continue
                sp = wsvg(name, code, j, H=40, col=(SAGE if code != "lo" else "#a33a2a"), labels=False, W=160)[0]
                rows += f'<tr><td>{lab}<div class="mk-spark">{sp}</div></td><td><b>{v:g}</b></td><td>{avg:.1f}</td><td class="mk-tr {cls}">{("▼" if cls=="up" else "▲" if cls=="dn" else "●") if code=="lo" else ("▲" if cls=="up" else "▼" if cls=="dn" else "●")}</td></tr>'
            w, v, avg = key
            inner += (f'<div class="mk-row"><div class="mk-status">{"<b>"+name+"</b> · " if scope=="both" else ""}Pending <b>{w}</b>: {v:g} form{'' if v==1 else 's'} in last week against {avg:.1f} a week (12-week average).</div>'
                      + (f'<table class="mk-t"><tr><th>Week to {(LASTMON+dt.timedelta(6)).day} {(LASTMON+dt.timedelta(6)):%b}</th><th>Week</th><th>Avg</th><th></th></tr>{rows}</table>' if scope != "both" else "") + '</div>')
        body += f'<div class="mk-c {scope}">{inner}</div>'
    FJ = json.load(open(SRC / "kpi/funnel.json"))
    ex = ""
    for k, name, _ in CEN:
        rows = [r for r in FJ["rows"] if r[0] == name][-7:]
        tr = ""
        for _, m, enq, tb, tou, fp, ec, st, conv in rows:
            mo = dt.date.fromisoformat(m + "-01")
            pct = f"{100*ec/enq:.0f}%" if enq and not conv else "…"
            tr += f'<tr><td>{mo:%b}{"*" if conv else ""}</td><td>{enq}</td><td>{tou}</td><td>{fp}</td><td>{ec}</td><td>{st}</td><td><b>{pct}</b></td></tr>'
        ex += (f'<div class="mk-c {k}"><div class="mk-sublbl">What each month\'s enquiries became</div>'
               f'<table class="mk-t mk-src"><tr><th>Enquired</th><th>Enq</th><th>Toured</th><th>Form</th><th>Enrolled</th><th>Started</th><th>Conv</th></tr>{tr}</table>'
               f'<p class="mk-foot">Follows each month\'s enquiring families through to enrolment (LineLeader, Dashboard {FJ["snap"][:10]}). Conv = enrolled ÷ enquiries. *Under 8 weeks old and still converting, so no rate yet.</p></div>')
    return card("Pipeline", "13 weeks · dashed line is the 12-week average", body, expand=ex)

# ---------- weekly bars with 12-week rolling line
def wseries(c, code, j=0, n=13):
    lastmon = LASTMON
    weeks = [lastmon - dt.timedelta(7 * i) for i in range(n + 11)][::-1]
    v = [wk_tot(c, code, w, j) for w in weeks]
    roll = [sum(v[i - 11:i + 1]) / 12 for i in range(11, len(v))]
    return weeks[11:], v[11:], roll
def wsvg(c, code, j=0, H=110, col=EARTH, lower=False, labels=True, W=340):
    weeks, v, roll = wseries(c, code, j)
    L, R, T, B = 4, 4, (14 if labels else 3), (16 if labels else 2)
    hi = max(max(v), max(roll), 1) * 1.15; n = len(v); bw = (W - L - R) / n
    Y = lambda x: T + (H - T - B) * (1 - x / hi)
    g = ""
    for i, x in enumerate(v):
        last = i == n - 1
        g += f'<rect x="{L+i*bw+bw*.15:.1f}" y="{Y(x):.1f}" width="{bw*.7:.1f}" height="{(H-B)-Y(x):.1f}" rx="2" fill="{col}" opacity="{1 if last else .55}"/>'
        if x and labels: g += f'<text x="{L+i*bw+bw/2:.1f}" y="{Y(x)-3:.1f}" font-size="8.5" text-anchor="middle" fill="{INK}" opacity="{1 if last else .6}" font-weight="{800 if last else 500}">{x:g}</text>'
    d = " ".join(f"{'M' if i==0 else 'L'}{L+i*bw+bw/2:.1f},{Y(r):.1f}" for i, r in enumerate(roll))
    g += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="3 2.5" opacity=".75"/>'
    if labels:
        for i, w in enumerate(weeks):
            if i % 3 == 0 or i == n - 1:
                e = w + dt.timedelta(6); g += f'<text x="{L+i*bw+bw/2:.1f}" y="{H-3}" font-size="8" text-anchor="middle" fill="{INK}" opacity=".55">{e.day} {e:%b}</text>'
    return f'<svg viewBox="0 0 {W} {H}" class="mk-svg">{g}</svg>', v[-1], roll[-1], roll[-2] if len(roll) > 1 else roll[-1]
SRCJ = json.load(open(SRC/'kpi/enq_source.json'))
SRC_ORDER = [("Walk-in", "#A45823"), ("Web", "#5E80A0"), ("Phone", "#6E8B57"), ("Link", "#E2A23B"), ("Other", "#cfc8bf"), ("Not recorded", "#e6e1da")]
SRC_DESC = {"Walk-in": "came to the centre", "Web": "website enquiry form", "Phone": "rang the centre",
            "Link": "came through a link (exact meaning to confirm)", "Other": "recorded as other", "Not recorded": "no contact type entered"}
def src_svg(c):
    months = sorted({r[1] for r in SRCJ["rows"]})[-6:]
    M = {m: {} for m in months}
    for cc, m, s_, n in SRCJ["rows"]:
        if cc == c and m in M: M[m][s_] = M[m].get(s_, 0) + n
    used = [(s_, col) for s_, col in SRC_ORDER if any(M[m].get(s_, 0) for m in months)]
    hd = "".join(f'<th>{dt.date.fromisoformat(m + "-01"):%b}{"*" if m == months[-1] else ""}</th>' for m in months)
    rows = ""
    for s_, col in used:
        cells = "".join(f'<td>{M[m].get(s_, 0) or "–"}</td>' for m in months)
        rows += f'<tr><td><i class="mk-dot" style="background:{col}"></i>{s_}</td>{cells}</tr>'
    tot = [sum(M[m].values()) for m in months]
    rows += '<tr class="tot"><td>Total</td>' + "".join(f"<td>{t}</td>" for t in tot) + "</tr>"
    other = sum(M[m].get("Other", 0) + M[m].get("Not recorded", 0) for m in months[-3:]); all3 = sum(tot[-3:])
    desc = " · ".join(f"<b>{s_}</b> {SRC_DESC[s_]}" for s_, _ in used)
    return (f'<table class="mk-t mk-src"><tr><th></th>{hd}</tr>{rows}</table><p class="mk-foot">{desc}.</p>'), other, all3
def enq_card():
    body = ""; ex_parts = []
    for k, name, _ in CEN:
        svg, last, avg, avg_prev = wsvg(name, "enq")
        w, cls = word(last, avg)
        ssvg, oth, all3 = src_svg(name)
        trend = "rising" if avg > avg_prev * 1.03 else "falling" if avg < avg_prev * 0.97 else "flat"
        body += (f'<div class="mk-c {k}"><div class="mk-status">Enquiries <b>{w}</b>: {last:g} last week against {avg:.1f} a week (12-week average, {trend}).</div>{svg}'
                 f'<div class="mk-leg"><span><i style="background:{EARTH}"></i>Enquiries a week</span><span><i class="dash"></i>12-week average</span></div>'
                 '</div>')
        ex_parts.append(f'<div class="mk-c {k}"><div class="mk-sublbl">How families made contact, by month</div>{ssvg}'
                 f'<p class="mk-foot">As recorded in LineLeader: contact type only, not the marketing source. Other or not recorded: {oth} of {all3} in the last three months. Recording discipline and source detail: for Judi Carr to review. *Month to date.</p></div>')
    return card("Enquiries", "The start of every enrolment in the Forecast", body, expand="".join(ex_parts))


# ---------- Wages screen (no tabs)
import w2r_xero as XW
WD = json.load(open(SRC / "kpi/wage_drivers.json"))
BANDS = {"South Morang": [(85, 1.75, "85%+"), (75, 1.85, "75–85%"), (65, 1.95, "65–75%"), (0, 2.05, "below 65%")],
         "Craigieburn": [(70, 1.85, "70%+"), (60, 1.90, "60–70%"), (50, 2.00, "50–60%"), (40, 2.15, "40–50%"), (0, 2.30, "below 40%")]}
OUTLIER = {("South Morang", "2026-07"): "1 July rate change, back pay and pay-run timing (provisional)",
           ("Craigieburn", "2026-08"): "back pay and agency staff $12,067 (Aman, Sep 26 Panel report)"}
def wrows(name, places):
    X = XW.SM if name == "South Morang" else XW.MR; out = []
    for m, h in WD["months"][name].items():
        if m not in X: continue
        x = X[m]; wages = x["hr"] + x["ag"] - x["wrgp"] - x["wrgi"]; ph = h["worked"] + h["leave"]
        occ = 100 * h["bcd"] / (places * h["open_days"])
        band = next(b for b in BANDS[name] if occ >= b[0])
        out.append(dict(m=m, hpc=ph / h["bcd"], cph=wages / ph, rpd=x["rev"] / h["bcd"], w2r=100 * wages / x["rev"], occ=occ, band=band))
    return out
def w2r_svg(R):
    W, H, L, B, T = 340, 150, 26, 18, 14; n = len(R); bw = (W - L - 4) / n; hi = max(80, max(r["w2r"] for r in R) + 5); lo = 40
    Y = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo)); g = ""
    for v, lab in ((55, "55%"), (60, "60%")):
        g += f'<line x1="{L}" x2="{W-4}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{"#b07d10" if v==55 else "#a33a2a"}" stroke-dasharray="4 3" opacity=".8"/><text x="{L-3}" y="{Y(v)+3:.1f}" font-size="8" text-anchor="end" fill="{INK}" opacity=".6">{lab}</text>'
    for i, r in enumerate(R):
        v = r["w2r"]; col = SAGE if v <= 55 else "#d9a400" if v <= 60 else "#a33a2a"
        g += f'<rect x="{L+i*bw+bw*.15:.1f}" y="{Y(min(v,hi)):.1f}" width="{bw*.7:.1f}" height="{H-B-Y(min(v,hi)):.1f}" rx="2" fill="{col}" opacity="{1 if i==n-1 else .75}"/>'
        g += f'<text x="{L+i*bw+bw/2:.1f}" y="{Y(min(v,hi))-3:.1f}" font-size="8" text-anchor="middle" fill="{INK}">{v:.0f}</text>'
        mo = dt.date.fromisoformat(r["m"] + "-01"); g += f'<text x="{L+i*bw+bw/2:.1f}" y="{H-4}" font-size="8" text-anchor="middle" fill="{INK}" opacity=".6">{mo:%b}</text>'
    return f'<svg viewBox="0 0 {W} {H}" class="mk-svg">{g}</svg>'
def wages_detail(k, name, places):
    R = wrows(name, places)
    a, b = R[:3], R[-2:]
    avg = lambda rs, key: sum(r[key] for r in rs) / len(rs)
    story = (f'Hours per child {avg(a,"hpc"):.2f} → {avg(b,"hpc"):.2f}; cost per paid hour ${avg(a,"cph"):.0f} → ${avg(b,"cph"):.0f}; '
             f'revenue per child-day ${avg(a,"rpd"):.0f} → ${avg(b,"rpd"):.0f} (first three months shown against the last two).')
    trs = ""
    for r in R:
        m2 = dt.date.fromisoformat(r["m"] + "-01"); okr = r["hpc"] <= r["band"][1] + 0.005
        flag = ' <span class="mk-fl">!</span>' if (name, r["m"]) in OUTLIER else ""
        trs += (f'<tr><td>{m2:%b %y}{flag}</td><td>{r["hpc"]:.2f}</td><td>${r["cph"]:.0f}</td><td>${r["rpd"]:.0f}</td>'
                f'<td><b>{r["w2r"]:.1f}%</b></td><td class="{"pos" if okr else "neg"}">{r["band"][1]:.2f}</td></tr>')
    notes = "".join(f'<li><span class="mk-fl">!</span> <b>{dt.date.fromisoformat(m+"-01"):%b %y}</b>: {t}</li>' for (c, m), t in OUTLIER.items() if c == name)
    wp = FEED["centres"][name]["wage_plan_forecast"]["wage_to_revenue_pct"]
    fwd = "".join(f'<td>{v:.0f}%</td>' for v in wp); fh = "".join(f'<th>{mm}</th>' for mm in FEED["months"][:len(wp)])
    bands = " · ".join(f'{lab} → {h:.2f}' for _, h, lab in BANDS[name])
    return (f'<div class="mk-c {k}">'
            f'<div class="mk-sublbl">Wage to revenue by month</div>{w2r_svg(R)}'
            f'<div class="mk-sublbl">The three drivers, month by month</div>'
            f'<table class="mk-t mk-src"><tr><th>Month</th><th>Hrs</th><th>$/hr</th><th>Rev/day</th><th>W2R</th><th>Band</th></tr>{trs}</table>'
            f'<p class="mk-status" style="margin-top:8px">{story}</p>'
            + (f'<ul class="mk-ul">{notes}</ul>' if notes else "") +
            f'<p class="mk-foot">Hrs = paid hours per booked child · $/hr = cost per paid hour · Rev/day = revenue per booked child-day. Band = the proposed paid-hours standard for that month’s occupancy (green if hours were at or under it): {bands}. Not yet adopted by the Panel.</p>'
            f'<div class="mk-sublbl">Model months ahead</div>'
            f'<table class="mk-t mk-src"><tr>{fh}</tr><tr>{fwd}</tr></table>'
            f'<p class="mk-foot">Wage to revenue in the Financial Model {FEED["version"]} wage plan.</p>'
            f'<div class="mk-sublbl">How these are measured</div><p class="mk-foot">'
            f'<b>Wages</b>: Xero HR service fee + agency − grant paid − grant income (the Panel report definition). <b>Revenue</b>: Xero fee revenue. '
            f'<b>Paid hours</b>: Owna sign-in hours less unpaid breaks, plus paid leave, whole pay run. <b>Booked child-days</b>: Owna bookings incl. casuals, open days only (Mon–Fri less Victorian public holidays). '
            f'Cost per hour is not yet spread by pay-run dates, so months with three pay runs, back pay or grant catch-ups read high or low (provisional). '
            f'Still to come: the next two weeks from the roster (roster, not paid) and rooms by day.</p></div>')
# ---------- wages
WG = {"sm": dict(oct=54.8, hrs=1.83, band=(1.85, "75–85%"), occ=79.4), "cb": dict(oct=70.8, hrs=2.30, band=(2.30, "below 40%"), occ=34.7)}
def wages_card():
    body = ""
    for scope in ("sm", "cb"):
        items = CEN if scope == "both" else [c for c in CEN if c[0] == scope]
        inner = ""
        for k, name, _ in items:
            w = WG[k]; wp = FEED["centres"][name]["wage_plan_forecast"]["wage_to_revenue_pct"]; ok = w["hrs"] <= w["band"][0] + 0.005
            icon = "✅" if w["oct"] <= 55 else "⚠️" if w["oct"] <= 60 else "⛔"
            inner += (f'<div class="mk-row"><div class="mk-status">{"<b>"+name+"</b> · " if scope=="both" else ""}{icon} October <b>{w["oct"]}%</b> against 55%. '
                      f'Paid hours {w["hrs"]:.2f} per child, {"on track" if ok else "off track"} for the {w["band"][1]} band ({w["band"][0]:.2f}). '
                      f'Model: Nov {wp[0]:.0f}%, Dec {wp[1]:.0f}%.</div></div>')
        body += f'<div class="mk-c {scope}">{inner}</div>'
    ex = "".join(wages_detail(k, name, pl_) for k, name, pl_ in CEN)
    return card("Wages", "Last full month · provisional", body + '<p class="mk-tag">Hours bands proposed, not yet adopted. Actual vs model first checkable when November closes.</p>', expand=ex)
# ---------- funding
def fund_card():
    fl = FEED["funding"]; cl = FEED["caae_line"]["monthly"]["forecast"]["cumulative_principal"]
    over = next(FEED["months"][i] for i, v in enumerate(cl) if v > FEED["caae_line"]["loan_limit_principal"])
    body = (f'<div class="mk-status">Loan passes the $1.9m limit in <b>{"December" if over=="Dec" else over}</b>. '
            f'Peak funding need <b>${fl["forecast"]["peak_unfunded_capital_need"]:,.0f}</b> w/e {fl["forecast"]["peak_week_ending"]} (Forecast); '
            f'${fl["target"]["peak_unfunded_capital_need"]:,.0f} w/e {fl["target"]["peak_week_ending"]} (Target).</div>'
            '<p class="mk-tag">Model update pending: the register names v3.3; Billy still holds the v3.2 feed. Figures change when the v3.3 feed is loaded.</p>')
    return card("Funding", "group · owner only", body, "Drawdown by month: to come", owner=True)
# ---------- to fix
def fix_card():
    PF = PFm.PF
    def n(c): return sum(v[0] for v in PF[c].values())
    body = "".join(f'<div class="mk-c {k}"><div class="mk-status"><b>{n(name)}</b> pending record{"" if n(name)==1 else "s"} to correct in Owna.</div>'
                   f'<p class="mk-foot">Tours not followed up: count to come from the Follow Up list.</p></div>' for k, name, _ in CEN)
    ex = ""
    LBL = {"past": "Start date has passed, child not started", "no date": "No start date recorded", "no days": "No booked days recorded"}
    for k, name, _ in CEN:
        rows = "".join(f'<tr><td>{LBL.get(t, t)}</td><td><b>{v[0]}</b></td></tr>' for t, v in PFm.PF[name].items())
        ex += f'<div class="mk-c {k}"><table class="mk-t">{rows}</table><p class="mk-foot">Pending families to correct in Owna (as at {PFm.SNAP}). Record numbers by family code are requested from Dima.</p></div>'
    return card("To fix", "", body, expand=ex)
def card(title, sub, body, more="", owner=False, go=None, expand=None):
    x = (f'<div class="mk-x" hidden>{expand}</div><button class="mk-tog" type="button">More <span>▾</span></button>') if expand else ""
    m = f'<button class="mk-more" data-go="{go}">{more}</button>' if go else ""
    return (f'<div class="mk-card{" own" if owner else ""}"><button class="mk-hb" type="button"><h2>{title}</h2><i>▾</i></button>'
            f'<div class="mk-b" hidden>{"<div class=mk-subt>"+sub+"</div>" if sub else ""}{body}{x}{m}</div></div>')
EXTRA_CSS = f"""
.mk{{padding:0 16px 24px;color:{INK}}}
.mk-top{{display:flex;justify-content:space-between;align-items:baseline;margin:4px 2px 10px}} .mk-top h1{{font-size:26px;margin:0}} .mk-top span{{font-size:13px;opacity:.7}}
.mk-sw{{display:flex;gap:8px;margin:14px 0 16px}} .mk-sw button{{flex:1;border:2px solid {EARTH};background:transparent;color:{EARTH};border-radius:999px;padding:8px 4px;font-weight:800;font-size:14px;font-family:inherit}}
.mk-sw button.on{{background:{EARTH};color:#FBF6EE}}
.mk-card{{background:#fff;border-radius:16px;padding:16px 16px 10px;margin:0 0 14px;box-shadow:0 1px 3px rgba(0,0,0,.06)}} .mk-card.own{{border:1.5px dashed {SKY}}}
.mk-h{{margin:0 0 8px}} .mk-h h2{{font-size:20px;margin:0;color:{EARTH};line-height:1.15}} .mk-h span{{display:block;font-size:12px;opacity:.6;margin-top:2px}}
.mk-status{{font-size:14.5px;line-height:1.4;margin:2px 0 8px}} .mk-sub{{font-weight:400;opacity:.65;font-size:12px}}
.mk-row{{padding:4px 0 6px;border-top:1px solid rgba(0,0,0,.06)}} .mk-row:first-child{{border-top:0}}
.mk-t{{width:100%;border-collapse:collapse;font-size:13px;margin:2px 0 6px}} .mk-t th{{font-size:11px;font-weight:600;opacity:.6;text-align:right;padding:2px 4px}} .mk-t th:first-child{{text-align:left}}
.mk-t td{{padding:5px 4px;text-align:right;border-top:1px solid rgba(0,0,0,.06)}} .mk-t td:first-child{{text-align:left}} .mk-t small{{opacity:.55}}
.mk-t tr.tot td{{font-weight:800;border-top:1.5px solid rgba(0,0,0,.25)}} .mk-t .pos{{color:{SAGE};font-weight:800}} .mk-t .neg{{color:#a33a2a;font-weight:800}}
.mk-foot{{font-size:12.5px;opacity:.8;margin:2px 0 4px}} .mk-tag{{font-size:11px;background:#FDF0C8;border-radius:8px;padding:5px 8px;margin:6px 0 2px;color:#7a3f17;font-weight:700}}
.mk-more{{display:block;width:100%;background:none;border:0;font-family:inherit;cursor:pointer;text-align:right;font-size:13px;font-weight:800;color:{EARTH};padding:6px 0 2px}}
.mk-leg{{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:11px;margin:2px 0 6px;opacity:.85}} .mk-leg i{{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:4px}}
.mk-svg{{width:100%;height:auto;display:block}} .pd-ar.up{{color:{SAGE}}} .pd-ar.dn{{color:#a33a2a}} .pd-ar.lvl{{opacity:.6}}
.mk .mk-c{{display:none}} .mk[data-c=both] .mk-c.both, .mk[data-c=sm] .mk-c.sm, .mk[data-c=cb] .mk-c.cb{{display:block}}
.mk-note{{font-size:11.5px;opacity:.6;text-align:center;margin-top:8px}}
"""

EXTRA_CSS += ".mk-more.off{opacity:.45} .mk-other{display:flex;gap:8px;justify-content:center;font-size:12.5px;margin:4px 0 0} .mk-other button{background:none;border:1px solid rgba(0,0,0,.15);border-radius:999px;padding:5px 10px;font-family:inherit;color:inherit}"
EXTRA_CSS += " .mk-tr{text-align:center!important;width:28px;font-size:12px} .mk-tr.up{color:#6E8B57} .mk-tr.dn{color:#a33a2a} .mk-tr.lvl{opacity:.4}"
EXTRA_CSS += " #home .hero{padding-top:18px;padding-bottom:18px;min-height:0} #home .hero .logo{height:84px;width:auto} #home .hello{font-size:26px}"
EXTRA_CSS += " .mk-leg i.dash{background:none;border-top:2px dashed #2b2622;height:0;opacity:.75} .mk-leg.sq i{width:9px;height:9px;border-radius:2px} .mk-sublbl{font-size:12.5px;font-weight:800;margin:12px 0 2px;opacity:.8} .mk-spark{width:160px;margin-top:4px} .mk-src td,.mk-src th{padding:5px 3px;font-variant-numeric:tabular-nums} .mk-src td:first-child{white-space:nowrap} .mk-dot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:0} .mk-t td{vertical-align:middle}"
EXTRA_CSS += " .mk-tog{display:block;width:100%;background:#f6efe4;border:0;border-radius:10px;padding:8px;margin:8px 0 2px;font-family:inherit;font-weight:800;color:#A45823;font-size:13.5px} .mk-tog.open span{display:inline-block;transform:rotate(180deg)} .mk-x{padding-top:4px} .mk-ul{margin:2px 0 6px;padding-left:4px;list-style:none;font-size:14px;line-height:1.6} body[data-c=sm] .wc.cb, body[data-c=cb] .wc.sm{display:none} .mk-fl{display:inline-block;background:#a33a2a;color:#fff;border-radius:999px;font-size:9px;width:13px;height:13px;line-height:13px;text-align:center;font-weight:800} .mk.wg{padding-top:4px}"
EXTRA_CSS += " .mk-hb{display:flex;width:100%;justify-content:space-between;align-items:center;background:none;border:0;padding:2px 0;font-family:inherit;cursor:pointer;text-align:left} .mk-hb h2{font-size:21px;margin:0;color:#A45823} .mk-hb i{font-style:normal;color:#A45823;font-size:16px;transition:transform .2s} .mk-hb.open i{transform:rotate(180deg)} .mk-b{padding-top:6px} .mk-subt{font-size:12px;opacity:.6;margin:0 0 8px} .mk-card{padding:14px 16px}"
HOME = (f'<div class="mk" id="mk" data-c="sm">'
        f'<div class="mk-sw"><button class="on" data-s="sm">South Morang</button><button data-s="cb">Craigieburn</button></div>'
        f'{yd_card()}{enq_card()}{pipe_card()}{occ_card()}{wages_card()}{fix_card()}'
        f'<div class="mk-other"><span style="opacity:.6;align-self:center">Being folded in:</span><button data-go="tours">Tours</button><button data-go="kpis">KPIs</button></div></div>')
i = built.find('<div class="tiles">'); depth = 0; j = i
for m in re.finditer(r'<div\b|</div>', built[i:]):
    depth += 1 if m.group() == '<div' else -1
    if depth == 0: j = i + m.end(); break
JS = """<script>(function(){var mk=document.getElementById('mk');var N={sm:'South Morang',cb:'Craigieburn'};
function set(k,sync){mk.dataset.c=k;document.body.dataset.c=k;document.querySelectorAll('.wsw button').forEach(function(b){b.classList.toggle('on',b.dataset.s===k)});mk.querySelectorAll('.mk-sw button').forEach(function(b){b.classList.toggle('on',b.dataset.s===k)});
try{localStorage.setItem('bbw-centre',k==='sm'?'south-morang':'craigieburn')}catch(e){}
if(sync)document.querySelectorAll('.toggle button').forEach(function(b){if(b.textContent.trim()===N[k]&&b.getAttribute('aria-selected')!=='true')b.click()});}
document.querySelectorAll('.mk-sw button').forEach(function(b){b.onclick=function(){set(b.dataset.s,true)}});document.querySelectorAll('.mk-hb').forEach(function(h){h.onclick=function(){var b=h.nextElementSibling;b.hidden=!b.hidden;h.classList.toggle('open',!b.hidden);}});document.querySelectorAll('.mk-tog').forEach(function(t){t.onclick=function(){var x=t.previousElementSibling;x.hidden=!x.hidden;t.classList.toggle('open',!x.hidden);t.firstChild.nodeValue=x.hidden?'More ':'Less ';}});
var c='sm';try{if(localStorage.getItem('bbw-centre')==='craigieburn')c='cb'}catch(e){}set(c,true);})();</script>"""
out = built[:i] + HOME + built[j:]

out = out.replace('</head>', f'<style>{EXTRA_CSS}</style></head>', 1).replace('</body>', JS + '</body>', 1)
open(sys.argv[2], 'w').write(out); print("ok", len(out), DAY, WK)
