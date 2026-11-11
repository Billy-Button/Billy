# Wages — Billy screen (mock-up 12 Nov 26). Updated daily. Educator hours against what the ratios need, by centre.
# Sources: dashboard snapshot 11 Nov 26 03:08 (owna_child ages + booked days, staff_roster_week, room_ratio_day,
# current_owna_occupancy_day); Xero (read-only) for wage to revenue and agency.
import kpis_build as kp
SAGE, AMBER, EARTH, INK, SKY = kp.SAGE, kp.AMBER, kp.EARTH, kp.INK, kp.SKY
ASAT = "11 Nov 26"
FIXED = 130      # hours a week assumed for fixed roles (management, admin, kitchen) until Robyn codes them in Owna
RATE = 48        # $ an educator hour incl. on-costs, for the dollar view only

HOW = {
 "South Morang": dict(hpc=7.83, u3=146, o3=278, u3j=120, o3j=196, total=851, rc=43.4, x_hr=197152, x_ag=1617, x_wp=10130, x_wi=10410, x_rev=325230, sep=1.25, oct=1.34),
 "Craigieburn": dict(hpc=7.45, u3=117, o3=194, u3j=110, o3j=127, total=660, rc=42.4, x_hr=179238, x_ag=3820, x_wp=8632, x_wi=8633, x_rev=234086, sep=None, oct=None),
}
C = {
 "South Morang": dict(k=1.30, rost=851, need_ratio=484, wk="9 Nov",
   path=[("Nov",629),("Dec",592),("Jan",486),("Feb",486)], feb="Feb before new starters: about +80–100 hrs if they are mostly under 3.",
   mult={"2026-07":1.17,"2026-08":1.30,"2026-09":1.25,"2026-10":1.34,"2026-11":1.49},
   lessons=["Feb–May 26, ~90 hrs a week, ≈ $100k."],
   agency={"2025-11":0.3,"2025-12":0.0,"2026-01":0.0,"2026-02":0.0,"2026-03":0.0,"2026-04":0.0,"2026-05":0.0,"2026-06":0.0,"2026-07":1.0,"2026-08":0.2,"2026-09":0.2,"2026-10":0.8}),
 "Craigieburn": dict(k=1.45, rost=660, need_ratio=349, wk="9 Nov",
   path=[("Nov",506),("Dec",500),("Jan",422),("Feb",422)], feb="Feb before committed starts and February's new enrolments.",
   mult={"2026-07":1.37,"2026-08":1.63,"2026-09":1.74,"2026-10":1.56,"2026-11":1.52},
   lessons=["Aug–Sep 26, ~80 hrs a week, ≈ $30k."],
   agency={"2026-02":0.0,"2026-03":0.0,"2026-04":0.0,"2026-05":0.0,"2026-06":0.5,"2026-07":0.8,"2026-08":6.1,"2026-09":0.3,"2026-10":2.1}),
}
def band(p): return SAGE if p <= 0 else (AMBER if p <= 5 else EARTH)

def head(label, sub, big, small, col=INK, grey=False):
    g = ' kp-grey' if grey else ''
    return (f'<li class="kp{g}"><div class="kp-h"><div class="kp-l"><b>{label}</b><span>{sub}</span></div>'
            f'<div class="kp-v"><b style="color:{col}">{big}</b><span>{small}</span></div></div>')
def note(t): return f'<div class="wg-note">{t}</div>'

def roster_bar(rost, need, col):
    W, L, R = 330, 10, 10
    hi = max(rost, need) * 1.18; x = lambda v: L + (W - L - R) * v / hi
    g = f'<rect x="{L}" y="18" width="{W-L-R}" height="8" rx="4" fill="{INK}" opacity=".08"/>'
    g += f'<rect x="{L}" y="18" width="{x(min(rost,need))-L:.1f}" height="8" rx="4" fill="{SAGE}" opacity=".55"/>'
    if rost > need: g += f'<rect x="{x(need):.1f}" y="18" width="{x(rost)-x(need):.1f}" height="8" rx="2" fill="{col}"/>'
    g += f'<line x1="{x(need):.1f}" y1="12" x2="{x(need):.1f}" y2="32" stroke="{INK}" stroke-width="2"/>'
    g += f'<text x="{x(need):.1f}" y="9" text-anchor="middle" font-size="9" font-weight="800" fill="{INK}">needed {need}</text>'
    g += f'<circle cx="{x(rost):.1f}" cy="22" r="6" fill="{col}"/>'
    g += f'<text x="{x(rost):.1f}" y="45" text-anchor="middle" font-size="9" font-weight="800" fill="{col}">rostered {rost}</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} 50">{g}</svg>'

def path_svg(edu, path):
    W, L, R, rowh = 330, 40, 50, 24
    hi = max(edu, max(v for _, v in path)) * 1.08; x = lambda v: L + (W - L - R) * v / hi
    H = rowh * len(path) + 22
    g = f'<line x1="{x(edu):.1f}" y1="4" x2="{x(edu):.1f}" y2="{H-14}" stroke="{EARTH}" stroke-width="1.6" stroke-dasharray="4 3"/>'
    g += f'<text x="{x(edu):.1f}" y="{H-3}" text-anchor="middle" font-size="9" font-weight="800" fill="{EARTH}">educators rostered now {edu}</text>'
    for i, (m, v) in enumerate(path):
        y = 6 + i * rowh; gap = edu - v
        g += f'<text x="{L-6}" y="{y+13}" text-anchor="end" font-size="11" font-weight="800" fill="{INK}">{m}</text>'
        g += f'<rect x="{L}" y="{y+2}" width="{x(v)-L:.1f}" height="15" rx="3" fill="{SAGE}" opacity=".85"/>'
        g += f'<text x="{L+5}" y="{y+13}" font-size="9.5" font-weight="800" fill="#fff">{v}</text>'
        if gap > 0:
            g += f'<rect x="{x(v):.1f}" y="{y+2}" width="{x(edu)-x(v):.1f}" height="15" rx="3" fill="{EARTH}" opacity=".18"/>'
            g += f'<text x="{x(edu)+4:.1f}" y="{y+13}" font-size="9.5" font-weight="800" fill="{EARTH}">−{gap}</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} {H}">{g}</svg>'

WEEKS = ["2026-09-07","2026-09-14","2026-09-21","2026-09-28","2026-10-05","2026-10-12","2026-10-19","2026-10-26","2026-11-02","2026-11-09",
         "2026-11-16","2026-11-23","2026-11-30","2026-12-07","2026-12-14","2026-12-21","2026-12-28","2027-01-04","2027-01-11","2027-01-18","2027-01-25",
         "2027-02-01","2027-02-08","2027-02-15","2027-02-22"]
TODAY = "2026-11-09"
G = {
 "South Morang": dict(rost=[624,596,619,611,630,618,646,729,685,721],
   need={"2026-09":636,"2026-10":638,"2026-11":629,"2026-12":592,"2027-01":486,"2027-02":486}, feb_hi=576),
 "Craigieburn": dict(rost=[574,555,581,533,519,524,499,518,498,530],
   need={"2026-09":467,"2026-10":480,"2026-11":506,"2026-12":500,"2027-01":422,"2027-02":422}, feb_hi=530),
}
MLAB = {"09":"Sep","10":"Oct","11":"Nov","12":"Dec","01":"Jan","02":"Feb"}

def glide(c):
    g = G[c]; n = len(WEEKS); ti = WEEKS.index(TODAY)
    W, H, L, R, T, B = 340, 190, 8, 64, 14, 22
    need = [g["need"][w[:7]] for w in WEEKS]
    rost_now = g["rost"][-1]
    rost = g["rost"] + [rost_now] * (n - len(g["rost"]))
    lo = min(need + rost) * 0.82; hi = max(need + rost + [g["feb_hi"]]) * 1.04
    xs = lambda i: L + (W - L - R) * i / (n - 1); ys = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    s = ""
    # month bands + labels
    prev = None
    for i, w in enumerate(WEEKS):
        if w[5:7] != prev:
            if i: s += f'<line x1="{xs(i)-3:.1f}" y1="{T}" x2="{xs(i)-3:.1f}" y2="{H-B}" stroke="{INK}" opacity=".06"/>'
            s += f'<text x="{xs(i)+2:.1f}" y="{H-6}" font-size="10" font-weight="700" fill="{INK}" opacity=".45">{MLAB[w[5:7]]}</text>'
            prev = w[5:7]
    # gap shading (over = earth, under = sage)
    for i in range(n - 1):
        for (a1, a2, b1, b2) in ((rost[i], rost[i+1], need[i], need[i]),):
            over = (a1 + a2) / 2 > (b1 + b2) / 2
            col = EARTH if over else SAGE
            s += (f'<path d="M{xs(i):.1f},{ys(a1):.1f} L{xs(i+1):.1f},{ys(a2):.1f} L{xs(i+1):.1f},{ys(b2):.1f} L{xs(i):.1f},{ys(b1):.1f} Z" '
                  f'fill="{col}" opacity="{.22 if over else .12}"/>')
    # Feb new-starter band on need
    fi = next(i for i, w in enumerate(WEEKS) if w.startswith("2027-02"))
    s += f'<rect x="{xs(fi):.1f}" y="{ys(g["feb_hi"]):.1f}" width="{xs(n-1)-xs(fi):.1f}" height="{ys(need[fi])-ys(g["feb_hi"]):.1f}" fill="{SAGE}" opacity=".18"/>'
    s += f'<text x="{(xs(fi)+xs(n-1))/2:.1f}" y="{ys(g["feb_hi"])-4:.1f}" text-anchor="middle" font-size="9" font-weight="800" fill="{SAGE}">+ new starters</text>'
    # need step line
    d = f'M{xs(0):.1f},{ys(need[0]):.1f}'
    for i in range(1, n):
        d += f' L{xs(i):.1f},{ys(need[i-1]):.1f} L{xs(i):.1f},{ys(need[i]):.1f}' if need[i] != need[i-1] else f' L{xs(i):.1f},{ys(need[i]):.1f}'
    s += f'<path d="{d}" fill="none" stroke="{SAGE}" stroke-width="3"/>'
    # roster: actual solid, ahead dashed
    da = " ".join(f'{"M" if i==0 else "L"}{xs(i):.1f},{ys(rost[i]):.1f}' for i in range(ti + 1))
    s += f'<path d="{da}" fill="none" stroke="{EARTH}" stroke-width="3" stroke-linejoin="round"/>'
    s += f'<path d="M{xs(ti):.1f},{ys(rost_now):.1f} L{xs(n-1):.1f},{ys(rost_now):.1f}" stroke="{EARTH}" stroke-width="2.4" stroke-dasharray="5 4" opacity=".75"/>'
    s += f'<circle cx="{xs(ti):.1f}" cy="{ys(rost_now):.1f}" r="5" fill="{EARTH}"/>'
    # today
    s += f'<line x1="{xs(ti):.1f}" y1="{T-6}" x2="{xs(ti):.1f}" y2="{H-B}" stroke="{INK}" stroke-width="1" stroke-dasharray="2 3" opacity=".5"/>'
    s += f'<text x="{xs(ti):.1f}" y="{T-6}" text-anchor="middle" font-size="9.5" font-weight="800" fill="{INK}" opacity=".6">today</text>'
    # end labels
    s += f'<text x="{W-R+6}" y="{ys(rost_now)+4:.1f}" font-size="11" font-weight="800" fill="{EARTH}">Rostered</text>'
    s += f'<text x="{W-R+6}" y="{ys(rost_now)+16:.1f}" font-size="11" font-weight="800" fill="{EARTH}">{rost_now}</text>'
    s += f'<text x="{W-R+6}" y="{ys(need[-1])+4:.1f}" font-size="11" font-weight="800" fill="{SAGE}">Needed</text>'
    s += f'<text x="{W-R+6}" y="{ys(need[-1])+16:.1f}" font-size="11" font-weight="800" fill="{SAGE}">{need[-1]}</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} {H}">{s}</svg>'

def how(rows, assume=""):
    body = "".join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in rows)
    return (f'<details class="wg-how"><summary>How it\'s worked out</summary><table>{body}</table>'
            + (f'<p>{assume}</p>' if assume else '') + '</details>')

def trend(title, big, col, svg, line="", howhtml=""):
    return (f'<div class="wg-tr"><div class="wg-trh"><b>{title}</b><span style="color:{col}">{big}</span></div>{svg}'
            + (f'<div class="wg-l">{line}</div>' if line else '') + howhtml + '</div>')

FY = ["Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun"]
F = {
 "South Morang": dict(w2r=[69.4,57.9,61.8,51.2,54.8,63.8,64.9,56.5,56.2,52.0,54.7,54.9], rate=55.0, oct_hrs=786,
   wages=[228848,177137,212543,187023,179362,185694,163858,155784,158244,158238,158224,159483],
   inc=[329736,306106,343908,365480,327384,291034,252503,275938,281443,304260,289204,290648],
   allow={"2026-11":624,"2026-12":650,"2027-01":559,"2027-02":525}),
 "Craigieburn": dict(w2r=[69.7,81.3,68.6,70.3,68.5,69.9,70.0,75.7,72.7,63.7,70.2,70.2], rate=61.1, oct_hrs=645,
   wages=[169120,177058,166499,170606,161758,144818,133172,184115,188551,191488,194424,197227],
   inc=[242753,217650,242719,242718,236163,207278,190152,243182,259186,300717,276801,281119],
   allow={"2026-11":482,"2026-12":418,"2027-01":373,"2027-02":566}),
}
def w2r_est(c):
    f = F[c]; tot = G[c]["rost"][-1] + FIXED; allowed_tot = f["allow"]["2026-11"] + FIXED
    return round(f["w2r"][4] * tot / allowed_tot, 1), tot, allowed_tot

def w2r_chart(c):
    f = F[c]; est, _, _ = w2r_est(c)
    W, H, L, R, T, B = 340, 170, 34, 60, 10, 34
    lo, hi = 45, 85
    xs = lambda i: L + (W - L - R) * i / 11; ys = lambda v: T + (H - T - B) * (1 - (min(max(v, lo), hi) - lo) / (hi - lo))
    col = lambda v: SAGE if v < 55 else (AMBER if v <= 60 else EARTH)
    s = ""
    for (y0, y1, cc) in ((lo, 55, SAGE), (55, 60, AMBER), (60, hi, EARTH)):
        s += f'<rect x="{L}" y="{ys(y1):.1f}" width="{W-L-R}" height="{ys(y0)-ys(y1):.1f}" fill="{cc}" opacity=".10"/>'
    for t in (50, 70, 80):
        s += f'<text x="{L-4}" y="{ys(t)+3:.1f}" text-anchor="end" font-size="8.5" fill="{INK}" opacity=".45">{t}%</text>'
    for v, lab, cc in ((55, "Target 55%", INK), (60, "Act 60%", EARTH)):
        s += f'<line x1="{L}" y1="{ys(v):.1f}" x2="{W-R}" y2="{ys(v):.1f}" stroke="{cc}" stroke-width="1.2" stroke-dasharray="5 3" opacity=".75"/>'
        s += f'<text x="{W-R+4}" y="{ys(v)+(10 if v==55 else -2):.1f}" font-size="9" font-weight="800" fill="{cc}">{lab}</text>'
    # forecast region shading
    s += f'<rect x="{(xs(4)+xs(5))/2:.1f}" y="{T}" width="{W-R-(xs(4)+xs(5))/2:.1f}" height="{H-T-B}" fill="{INK}" opacity=".035"/>'
    s += f'<text x="{(xs(5)+xs(11))/2:.1f}" y="{T+10}" text-anchor="middle" font-size="9" font-weight="800" fill="{INK}" opacity=".45">forecast</text>'
    vals = f["w2r"][:4] + [est] + f["w2r"][5:]
    for i in range(11):
        dash = '' if i < 3 else ' stroke-dasharray="4 4"'
        op = 1 if i < 4 else .6
        s += f'<line x1="{xs(i):.1f}" y1="{ys(vals[i]):.1f}" x2="{xs(i+1):.1f}" y2="{ys(vals[i+1]):.1f}" stroke="{col(vals[i+1])}" stroke-width="2.5" opacity="{op}"{dash}/>'
    # forecast Nov point too (model) for comparison
    s += f'<circle cx="{xs(4):.1f}" cy="{ys(f["w2r"][4]):.1f}" r="3" fill="none" stroke="{INK}" stroke-width="1.2" opacity=".5"/>'
    for i, v in enumerate(vals):
        if i < 4: s += f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="3.4" fill="{col(v)}"/>'
        elif i == 4: s += f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="4.6" fill="#FBF6EE" stroke="{col(v)}" stroke-width="2.4"/>'
        else: s += f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="2.8" fill="{col(v)}" opacity=".6"/>'
        s += f'<text x="{xs(i):.1f}" y="{H-19}" text-anchor="middle" font-size="9" fill="{INK}" opacity=".45">{FY[i][0]}</text>'
        s += f'<text x="{xs(i):.1f}" y="{H-5}" text-anchor="middle" font-size="8.5" font-weight="800" fill="{col(v)}" opacity="{1 if i<=4 else .7}">{"~" if i==4 else ""}{v:.0f}</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} {H}">{s}</svg>'

def glide3(c):
    g = G[c]; f = F[c]; n = len(WEEKS); ti = WEEKS.index(TODAY)
    W, H, L, R, T, B = 340, 200, 8, 72, 14, 22
    need = [g["need"][w[:7]] for w in WEEKS]
    allow = [f["allow"].get(w[:7]) for w in WEEKS]
    rost_now = g["rost"][-1]; rost = g["rost"] + [rost_now] * (n - len(g["rost"]))
    vals = need + rost + [a for a in allow if a] + [g["feb_hi"]]
    lo = min(vals) * 0.82; hi = max(vals) * 1.04
    xs = lambda i: L + (W - L - R) * i / (n - 1); ys = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
    s = ""; prev = None
    for i, w in enumerate(WEEKS):
        if w[5:7] != prev:
            if i: s += f'<line x1="{xs(i)-3:.1f}" y1="{T}" x2="{xs(i)-3:.1f}" y2="{H-B}" stroke="{INK}" opacity=".06"/>'
            s += f'<text x="{xs(i)+2:.1f}" y="{H-6}" font-size="10" font-weight="700" fill="{INK}" opacity=".45">{MLAB[w[5:7]]}</text>'
            prev = w[5:7]
    # gap roster vs forecast allowance (from Nov) shaded
    for i in range(n - 1):
        ref = allow[i] if allow[i] else need[i]
        over = (rost[i] + rost[i+1]) / 2 > ref
        s += (f'<path d="M{xs(i):.1f},{ys(rost[i]):.1f} L{xs(i+1):.1f},{ys(rost[i+1]):.1f} L{xs(i+1):.1f},{ys(ref):.1f} L{xs(i):.1f},{ys(ref):.1f} Z" '
              f'fill="{EARTH if over else SAGE}" opacity="{.2 if over else .12}"/>')
    fi = next(i for i, w in enumerate(WEEKS) if w.startswith("2027-02"))
    s += f'<rect x="{xs(fi):.1f}" y="{ys(g["feb_hi"]):.1f}" width="{xs(n-1)-xs(fi):.1f}" height="{ys(need[fi])-ys(g["feb_hi"]):.1f}" fill="{SAGE}" opacity=".18"/>'
    def step(series, col, width, dash=""):
        pts = [(i, v) for i, v in enumerate(series) if v]
        d = f'M{xs(pts[0][0]):.1f},{ys(pts[0][1]):.1f}'
        for (i0, v0), (i1, v1) in zip(pts, pts[1:]):
            d += f' L{xs(i1):.1f},{ys(v0):.1f} L{xs(i1):.1f},{ys(v1):.1f}'
        return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{width}"{dash}/>'
    s += step(need, SAGE, 3)
    s += step(allow, SKY, 2.6, ' stroke-dasharray="6 3"')
    da = " ".join(f'{"M" if i==0 else "L"}{xs(i):.1f},{ys(rost[i]):.1f}' for i in range(ti + 1))
    s += f'<path d="{da}" fill="none" stroke="{EARTH}" stroke-width="3" stroke-linejoin="round"/>'
    s += f'<path d="M{xs(ti):.1f},{ys(rost_now):.1f} L{xs(n-1):.1f},{ys(rost_now):.1f}" stroke="{EARTH}" stroke-width="2.4" stroke-dasharray="5 4" opacity=".75"/>'
    s += f'<circle cx="{xs(ti):.1f}" cy="{ys(rost_now):.1f}" r="5" fill="{EARTH}"/>'
    s += f'<line x1="{xs(ti):.1f}" y1="{T-6}" x2="{xs(ti):.1f}" y2="{H-B}" stroke="{INK}" stroke-dasharray="2 3" opacity=".5"/>'
    s += f'<text x="{xs(ti):.1f}" y="{T-6}" text-anchor="middle" font-size="9.5" font-weight="800" fill="{INK}" opacity=".6">today</text>'
    labs = sorted([(ys(rost_now), "Rostered", rost_now, EARTH), (ys(allow[-1]), "Forecast", allow[-1], SKY), (ys(need[-1]), "Ratios", need[-1], SAGE)])
    last = -99
    for y, t, v, cc in labs:
        y = max(y, last + 24); last = y
        s += f'<text x="{W-R+6}" y="{y+2:.1f}" font-size="10.5" font-weight="800" fill="{cc}">{t}</text><text x="{W-R+6}" y="{y+14:.1f}" font-size="10.5" font-weight="800" fill="{cc}">{v}</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} {H}">{s}</svg>'

def guide_check(c):
    d = C[c]; k = d["k"]; m, now = kp.latest(d["mult"])
    rows = [("From the rules", 1.24, SKY), ("Our efficient months", k, SAGE), ("Now", now, EARTH if now > k*1.05 else (AMBER if now > k else SAGE))]
    W, L = 330, 132; x = lambda v: L + (W - L - 30) * (v - 1.0) / 0.6
    s = ""
    for i, (t, v, cc) in enumerate(rows):
        y = 6 + i * 24
        s += f'<text x="{L-6}" y="{y+12}" text-anchor="end" font-size="10.5" font-weight="800" fill="{INK}" opacity=".75">{t}</text>'
        s += f'<rect x="{L}" y="{y+2}" width="{x(v)-L:.1f}" height="14" rx="3" fill="{cc}" opacity=".85"/>'
        s += f'<text x="{x(v)+4:.1f}" y="{y+13}" font-size="10.5" font-weight="800" fill="{cc}">{v:.2f}×</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} 80">{s}</svg>'

def panel(c):
    d = C[c]; g = G[c]; f = F[c]; h = HOW[c]; k = d["k"]
    now = g["rost"][-1]; jan_need = g["need"]["2027-01"]; jan_allow = f["allow"]["2027-01"]
    nov_allow = f["allow"]["2026-11"]; nov_need = g["need"]["2026-11"]
    est, tot, allowed_tot = w2r_est(c)
    over_f = now - nov_allow; col_f = band(round(100 * over_f / nov_allow))
    r_now = h["u3"]*h["hpc"]/4 + h["o3"]*h["hpc"]/11
    # 1 Wage to revenue
    wcol = SAGE if est < 55 else (AMBER if est <= 60 else EARTH)
    b1 = trend("Wage to revenue", f"~{est:.0f}% Nov · forecast {f['w2r'][4]:.0f}%", wcol, w2r_chart(c),
               f"FY27: Jul–Oct actual · Nov estimate · Dec–Jun forecast · year {100*sum(f['wages'])/sum(f['inc']):.0f}%",
               how([("Jul–Oct", "Xero: wages net of the grant ÷ income, as in the cash flow model"),
                    ("Nov estimate", f"forecast {f['w2r'][4]}% × rostered {tot} hrs ÷ hours the forecast allows {allowed_tot} = <b>{est}%</b>"),
                    ("Dec–Jun", "the cash flow model's wages ÷ income, month by month (Financial Model v2.0, 9 Nov)"),
                    ("Year", f"model wages ${sum(f['wages'])/1e6:.2f}m ÷ income ${sum(f['inc'])/1e6:.2f}m")],
                   "Same definition throughout as the model. Xero replaces the estimate when November closes."))
    # 2 Tracking to forecast on hours
    b2 = (f'<div class="wg-tr"><div class="wg-trh"><b>On track for the forecast?</b><span style="color:{col_f}">{"+" if over_f>0 else ""}{over_f} hrs this week</span></div>'
          f'<div class="wg-week" style="border-color:{col_f}"><span>Educator hours a week · week of {d["wk"]}</span>'
          f'<b style="color:{col_f}">{now}</b><i>rostered · forecast allows {nov_allow} · ratios need {nov_need}</i></div>'
          + glide3(c)
          + f'<div class="wg-l">January: forecast allows {jan_allow} · ratios need {jan_need} · to forecast −{now-jan_allow} hrs a week (≈ ${round((now-jan_allow)*RATE*4.33/1000)}k a month)'
          + (" · <b>forecast is below the ratio need</b>" if jan_allow < jan_need else "") + '</div>'
          + how([("Forecast allows", f"model wages ÷ (4.33 weeks × ${f['rate']} an hour) − {FIXED} fixed hrs. Nov: ${f['wages'][4]:,} → <b>{nov_allow} hrs</b>; Jan: ${f['wages'][6]:,} → <b>{jan_allow} hrs</b>"),
                 ("$ an hour", f"October's actual wages ${f['wages'][3]:,} ÷ ({f['oct_hrs']} hrs × 4.33) = ${f['rate']} (all staff, all-in)"),
                 ("Ratios need", f"({h['u3']}×{h['hpc']}÷4 + {h['o3']}×{h['hpc']}÷11) = {r_now:.0f} ratio hrs × {k:.2f} = <b>{nov_need} hrs</b>"),
                 ("January need", f"({h['u3j']}×{h['hpc']}÷4 + {h['o3j']}×{h['hpc']}÷11) × {k:.2f} = <b>{jan_need} hrs</b> (leavers out, children aged forward)"),
                 ("Rostered", f"{h['total']} hrs all staff − {FIXED} fixed = <b>{now} educator hrs</b>, held flat ahead"),
                 ("Dollars", f"hours × ${RATE} an educator hour × 4.33 weeks")],
                f"Booked children (absences are the buffer), Victorian ratios by age on the day, {h['hpc']} hrs a child a day from Owna. Pale band in February: extra need if new starters are mostly under 3. Fixed roles {FIXED} hrs a week until coded in Owna.")
          + '</div>')
    # 3 Roster ÷ ratios history
    m, v = kp.latest(d["mult"])
    mcf = lambda x: SAGE if x <= k else (AMBER if x <= k * 1.05 else EARTH)
    b3 = trend("Roster ÷ ratios", f"{v:.2f}× · guide {k:.2f}", mcf(v),
               kp.chart(kp.ser(d["mult"]), mcf, k, f"{k:.2f}", lo=1.0, hi=1.9, ticks=[(1.2, "1.2"), (1.5, "1.5"), (1.8, "1.8")], vfmt=lambda x: f"{x:.2f}", tprefix="Guide"),
               "Past overruns: " + " ".join(d["lessons"]),
               how([("This month", f"{now} educator hrs ÷ {r_now:.0f} ratio hrs = <b>{now/r_now:.2f}×</b>"),
                    ("Colour", f"green ≤ {k:.2f} · amber to {k*1.05:.2f} · brown above")],
                   "Monthly points use the age mix of the children booked each month (Owna room data, July on)."))
    # 4 Guide check
    b4 = trend("Guide check", f"guide {k:.2f}× · bottom-up 1.24×", SKY, guide_check(c),
               "Validated in full once sign-in times arrive",
               how([("Breaks", "30-min unpaid meal break per 7.6-hr shift needs cover: × 1.07"),
                    ("Rest pauses", "two paid 10-min rests per shift: × 1.04"),
                    ("Programming", "2 hrs a week non-contact (4 for the Educational Leader): × 1.03"),
                    ("Whole educators", "rooms staffed in whole people by age group: × 1.08 (estimate)"),
                    ("Bottom-up", "1.07 × 1.04 × 1.03 × 1.08 = <b>1.24×</b>"),
                    ("Our efficient months", f"South Morang Sep 1.25×, Oct 1.34× (wage to revenue near target) → guide {C['South Morang']['k']:.2f}×"),
                    ("Craigieburn", "guide 1.45× while rooms are part-full; steps down as they fill")],
                   "Victoria has no short-break allowance, so breaks need relief cover. The whole-educator factor is the one to firm up: half-hourly sign-ins will show it directly."))
    # 5 Agency
    am, agv = kp.latest(d["agency"]); acf = lambda x: SAGE if x <= 1 else (AMBER if x <= 3 else EARTH)
    b5 = trend("Agency", f"{agv:g}% {kp.mon(am)} · guide 1%", acf(agv),
               kp.chart(kp.ser(d["agency"]), acf, 1, "1%", lo=0, hi=7, unit="%", ticks=[(3,"3%"),(6,"6%")], vfmt=lambda x: f"{x:g}%", tprefix="Guide"),
               "% of total wages",
               how([("October", f"agency ${h['x_ag']:,} ÷ (HR recharge ${h['x_hr']:,} + agency ${h['x_ag']:,}) = <b>{100*h['x_ag']/(h['x_hr']+h['x_ag']):.1f}%</b>"),
                    ("Guide", "1% · amber to 3% · brown above")]))
    soon = "".join(f'<div class="wg-soonrow"><b>{a}</b><span>{b}</span></div>' for a, b in (
        ("Through the day", "children by age against staff signed in, each half hour"),
        ("Rostered against worked", "roster against staff sign-in hours")))
    return (f'<li class="kp wg-main">{b1}{b2}{b3}{b4}{b5}</li>'
            f'<li class="kp wg-main"><div class="wg-soonh">Coming</div>{soon}</li>')

def section(logo):
    return f'''
<section id="wages" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>Wages</h1><div class="sub">Daily · as at {ASAT}</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <nav class="toggle wg" role="tablist" aria-label="Centre">
    <button type="button" role="tab" aria-selected="true" data-wg="wg-sm">South Morang</button>
    <button type="button" role="tab" aria-selected="false" data-wg="wg-cb">Craigieburn</button>
  </nav>
  <div class="screens">
    <div id="wg-sm" class="screen"><div class="centre"><ul class="measures kpl">{panel("South Morang")}</ul></div></div>
    <div id="wg-cb" class="screen" hidden><div class="centre"><ul class="measures kpl">{panel("Craigieburn")}</ul></div></div>
  </div>
  <details class="foot"><summary>About the numbers</summary>
    <p><b>Updated daily</b> from the dashboard's overnight build of Owna; wage to revenue and agency take Xero once a month closes.</p>
    <p><b>Hours needed</b> is a guide for setting the roster, not a compliance test. It starts from the children booked (enrolled plus casuals), not those who came: the roster is set before anyone knows who will be away, and every booked child may arrive, so absences are the buffer. Each child counts by age on the day (Victoria: under 36 months, 1 educator to 4 children; 36 months to preschool age, 1 to 11; school-age, 1 to 15). Ratio hours = children booked × the average hours a child is at the centre (Owna sign-ins: about 7.8 at South Morang, 7.5 at Craigieburn) ÷ the ratio. Educator hours needed = ratio hours × South Morang 1.30, Craigieburn 1.45. The multiplier covers break relief (Victoria has no short-break allowance, so every break is covered), programming time (2 hours a week; 4 for the Educational Leader), whole educators by room and age, and the absence buffer. South Morang's 1.30 is its own September–October roster, when wage to revenue ran near target; Craigieburn's is higher while rooms are part-full and steps down as they fill.</p>
    <p><b>Educator hours</b> are total rostered hours less {FIXED} a week for fixed roles (management, admin, kitchen) until Robyn codes those roles in Owna.</p>
    <p><b>The chart</b>: brown is educator hours rostered each week (solid to today, then held flat); green is the educator hours the ratios need for the children booked, by age. It ages each child forward a month at a time (1:4 becomes 1:11 when a child turns 3), takes out the 2027 school leavers from January, and rises as new enrolments are booked. The pale band in February is the extra need if most new starters are under 3. Shading shows the gap: brown over, green under.</p><p><b>The headline</b> is today's roster less January's need, in hours a week, full-time educators (38 hours) and dollars a month.</p>
    <p><b>Roster against ratio rules</b>: educator hours ÷ ratio hours for the children booked, by month (age mix from Owna's room data, July on; earlier months once the age history is in). Lessons are past periods above the guide, with their cost.</p>
    <p><b>Wage to revenue</b>: Xero, net of the grant, incl. agency. November is a roster estimate (Owna roster × 1.37, the 12-month relationship to Xero), within about 6 points when tested back; Xero replaces it at month close.</p>
    <p>Dollar figures use about ${RATE} an educator hour including on-costs. No one is named on this screen.</p>
  </details>
</section>'''

wg_js = """
  var wgTabs = Array.prototype.slice.call(document.querySelectorAll('.toggle.wg button'));
  wgTabs.forEach(function(t){ t.addEventListener('click', function(){
    wgTabs.forEach(function(x){ x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
    ['wg-sm','wg-cb'].forEach(function(id){ document.getElementById(id).hidden = (id !== t.dataset.wg); });
  }); });
"""
wg_css = """
.wg-main { border-bottom:none !important; }
.wg-hero { padding:4px 0 6px; } .wg-hero span { display:block; font-size:12px; font-weight:800; color:var(--ink-70); text-transform:uppercase; letter-spacing:.04em; }
.wg-hero b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:44px; line-height:1.05; color:#A45823; } .wg-hero b small { font-size:17px; }
.wg-hero i { font-style:normal; font-size:13px; font-weight:800; color:var(--ink-70); }
.wg-chips { display:flex; gap:8px; margin-top:10px; } .wg-chip { flex:1 1 0; background:#fff; border-radius:14px; padding:9px 10px; box-shadow:0 1px 0 rgba(43,35,32,.06); }
.wg-chip span { display:block; font-size:10.5px; font-weight:800; color:var(--ink-70); } .wg-chip b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-size:22px; font-weight:600; line-height:1.1; } .wg-chip i { font-style:normal; font-size:10px; font-weight:700; color:var(--ink-50); }
.wg-week { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 10px; margin:8px 0 2px; padding:8px 12px; background:#fff; border-left:4px solid; border-radius:10px; }
.wg-week span { width:100%; font-size:10.5px; font-weight:800; color:var(--ink-70); text-transform:uppercase; letter-spacing:.04em; } .wg-week b { font-family:"Fredoka","Nunito",sans-serif; font-size:24px; font-weight:600; } .wg-week i { font-style:normal; font-size:12px; font-weight:800; color:var(--ink-70); }
.wg-tr { padding:10px 0 12px; border-bottom:1px solid rgba(43,35,32,.08); } .wg-tr:last-child { border-bottom:none; }
.wg-trh { display:flex; justify-content:space-between; align-items:baseline; gap:8px; } .wg-trh b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; } .wg-trh span { font-size:12.5px; font-weight:800; white-space:nowrap; }
.wg-l { font-size:11px; font-weight:700; color:var(--ink-50); line-height:1.35; }
.wg-how { margin-top:6px; } .wg-how summary { font-size:12px; font-weight:800; color:#A45823; cursor:pointer; list-style:none; padding:4px 0; }
.wg-how summary::before { content:"▸ "; } .wg-how[open] summary::before { content:"▾ "; } .wg-how summary::-webkit-details-marker { display:none; }
.wg-how table { width:100%; border-collapse:collapse; font-size:11.5px; margin:4px 0; } .wg-how td { padding:4px 0; border-bottom:1px solid rgba(43,35,32,.07); vertical-align:top; } .wg-how td:first-child { color:var(--ink-70); font-weight:700; width:38%; padding-right:8px; } .wg-how td:last-child { font-weight:700; }
.wg-how p { font-size:11px; color:var(--ink-70); font-weight:600; line-height:1.4; margin:6px 0 2px; }
.wg-soonh { font-size:10.5px; font-weight:800; color:var(--ink-50); text-transform:uppercase; letter-spacing:.04em; padding-bottom:4px; }
.wg-soonrow { opacity:.5; padding:6px 0; } .wg-soonrow b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:14px; } .wg-soonrow span { font-size:11px; font-weight:700; }
"""
