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

RANGE = {"South Morang": (45, 72), "Craigieburn": (50, 85)}
# roster cost ÷ booked fees (Owna, dashboard roster_week_economics), monthly average of weeks starting in month; Nov = weeks to 9 Nov
EW = {"South Morang": dict(vals=[44.2,42.2,37.6,39.3,44.7], guide=38, why="the level that has gone with about 55% in Xero (2025, Sep–Oct 26)"),
      "Craigieburn": dict(vals=[55.0,54.0,49.7,45.4,44.5], guide=44, why="the level that matches the forecast's ~69% (Xero ÷ roster in October, 1.56)")}
# under-3 share of booked spots: today's children aged forward (leavers out from Jan); and with new starters at the last six months' mix
AGE = {"South Morang": dict(now=[34,32,38,38,35,33,33,32], new=[34,32,38,42,41,40,40,40], mix=72, starters="+44 in Feb, then +11 a month, plus committed starts"),
       "Craigieburn": dict(now=[38,37,46,46,43,39,39,36], new=[38,37,46,50,48,46,46,44], mix=57, starters="+65 in Feb, then +16 a month, plus committed starts")}
AM = ["Nov","Dec","Jan","Feb","Mar","Apr","May","Jun"]

def axis_chart(labels, series, lo, hi, guide=None, glabel="", bands=None, unit="%", H=150, under=None):
    W, L, R, T, B = 340, 34, 62, 12, 34 if under else 22
    n = len(labels)
    xs = lambda i: L + (W - L - R) * i / (n - 1); ys = lambda v: T + (H - T - B) * (1 - (min(max(v, lo), hi) - lo) / (hi - lo))
    s = ""
    if bands:
        for (y0, y1, cc) in bands:
            s += f'<rect x="{L}" y="{ys(y1):.1f}" width="{W-L-R}" height="{ys(y0)-ys(y1):.1f}" fill="{cc}" opacity=".10"/>'
    step = 5 if hi - lo <= 30 else 10
    t = (lo // step + 1) * step
    while t < hi:
        s += f'<line x1="{L}" y1="{ys(t):.1f}" x2="{W-R}" y2="{ys(t):.1f}" stroke="{INK}" opacity=".06"/><text x="{L-4}" y="{ys(t)+3:.1f}" text-anchor="end" font-size="8.5" fill="{INK}" opacity=".45">{t}{unit}</text>'
        t += step
    for (gv, gl, gc) in (guide or []):
        s += f'<line x1="{L}" y1="{ys(gv):.1f}" x2="{W-R}" y2="{ys(gv):.1f}" stroke="{gc}" stroke-width="1.2" stroke-dasharray="5 3" opacity=".8"/>'
        s += f'<text x="{W-R+4}" y="{ys(gv)+3:.1f}" font-size="9" font-weight="800" fill="{gc}">{gl}</text>'
    for (vals, colf, style) in series:
        pts = [(i, v) for i, v in enumerate(vals) if v is not None]
        for (i0, v0), (i1, v1) in zip(pts, pts[1:]):
            dash = ' stroke-dasharray="4 4"' if style.get("dash_from") is not None and i1 > style["dash_from"] else (' stroke-dasharray="4 4"' if style.get("dash") else "")
            op = style.get("op", 1) if not (style.get("dash_from") is not None and i1 > style["dash_from"]) else .6
            s += f'<line x1="{xs(i0):.1f}" y1="{ys(v0):.1f}" x2="{xs(i1):.1f}" y2="{ys(v1):.1f}" stroke="{colf(v1)}" stroke-width="2.5" opacity="{op}"{dash}/>'
        for i, v in pts:
            hol = style.get("hollow") == i
            if hol: s += f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="4.6" fill="#FBF6EE" stroke="{colf(v)}" stroke-width="2.4"/>'
            else: s += f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="{3.2 if not style.get("small") else 2.6}" fill="{colf(v)}" opacity="{.6 if style.get("dash_from") is not None and i > style["dash_from"] else 1}"/>'
        if style.get("end"):
            i, v = pts[-1]; s += f'<text x="{xs(i)+6:.1f}" y="{ys(v)+3:.1f}" font-size="9" font-weight="800" fill="{colf(v)}">{style["end"]}</text>'
    for i, lab in enumerate(labels):
        s += f'<text x="{xs(i):.1f}" y="{H-(19 if under else 6)}" text-anchor="middle" font-size="9" fill="{INK}" opacity=".45">{lab}</text>'
        if under:
            v, cc, pre = under[i]
            if v is not None: s += f'<text x="{xs(i):.1f}" y="{H-5}" text-anchor="middle" font-size="8.5" font-weight="800" fill="{cc}">{pre}{v:.0f}</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} {H}">{s}</svg>'

def flag(txt, on=True):
    return f'<div class="wg-flag{"" if on else " off"}">{"⚑ Check: " if on else "✓ "}{txt}</div>'

def panel(c):
    f = F[c]; h = HOW[c]; e = EW[c]; ag = AGE[c]
    est, tot, allowed_tot = w2r_est(c)
    lo, hi = RANGE[c]
    wcf = lambda v: SAGE if v < 55 else (AMBER if v <= 60 else EARTH)
    vals = f["w2r"][:4] + [est] + f["w2r"][5:]
    # 1 Wage to revenue
    b1 = trend("Wage to revenue", f"~{est:.0f}% Nov · forecast {f['w2r'][4]:.0f}%", wcf(est),
               axis_chart([m[0] for m in FY], [(vals, wcf, dict(dash_from=4, hollow=4))], lo, hi,
                          guide=[(55, "Target 55%", INK), (60, "Act 60%", EARTH)],
                          bands=[(lo, 55, SAGE), (55, 60, AMBER), (60, hi, EARTH)], H=165,
                          under=[(v, wcf(v), "~" if i == 4 else "") for i, v in enumerate(vals)]),
               f"Jul–Oct actual · Nov estimate · Dec–Jun forecast · year {100*sum(f['wages'])/sum(f['inc']):.0f}%",
               how([("Jul–Oct", "Xero: wages net of the grant ÷ income, as in the cash flow model; reconciles to the Panel reports within about a point"),
                    ("Nov estimate (~)", f"forecast {f['w2r'][4]}% × hours rostered {tot} ÷ hours the forecast's wages pay for {allowed_tot} = <b>{est}%</b>. An estimate only; Xero replaces it at close"),
                    ("Dec–Jun", "the cash flow model's wages ÷ income (Financial Model v2.0, 9 Nov)"),
                    ("Year", f"model wages ${sum(f['wages'])/1e6:.2f}m ÷ income ${sum(f['inc'])/1e6:.2f}m")]))
    # 2 Early warning
    ecf = lambda v: SAGE if v <= e["guide"] + 1 else AMBER
    ev = e["vals"][-1]; on = ev > e["guide"] + 1
    b2 = trend("Early warning: roster cost", f"{ev:.0f}% · check above {e['guide']}%", AMBER if on else SAGE,
               axis_chart(["J", "A", "S", "O", "N"], [(e["vals"], ecf, dict(hollow=4))], e["guide"] - 10, e["guide"] + 15,
                          guide=[(e["guide"], f"Check {e['guide']}%", AMBER)], H=110),
               flag(f"roster cost is {ev - e['guide']:.0f} points above the check line; Xero has followed about 6 weeks later before." if on else f"at the check line ({ev:.0f}% against {e['guide']}%).", on),
               how([("What it is", "Owna rostered hours × each person's Owna pay rate ÷ booked fees incl. CCS, each week (dashboard). Leaves out super, payroll tax, leave and unrostered staff, so it reads lower than Xero"),
                    ("Check line", f"{e['guide']}%: {e['why']}"),
                    ("Track record", "Feb 26 at South Morang: roster cost jumped 37% → 47% in the first week; Xero showed the step (53% → 58–60%) only after February closed, 6–7 weeks later"),
                    ("Limits", "direction, not precision: month to month it moves with Xero only loosely (correlation about 0.4–0.5), and it can't tell extra hours from a younger age mix")],
                   "A flag for checking with Robyn, not a hard limit."))
    # 3 Age mix
    acf = lambda v: SAGE if v <= ag["now"][0] else AMBER
    pk = max(ag["new"]); on3 = pk > ag["now"][0] + 2
    b3 = trend("Age mix ahead", f"under-3s {ag['now'][0]}% now → {ag['new'][3]}% Feb", AMBER if on3 else SAGE,
               axis_chart(AM, [(ag["now"], lambda v: SKY, dict(small=True, end="today's")), (ag["new"], acf, dict(dash=True, end="with starters"))],
                          25, 55, H=120),
               flag(f"more under-3s from January (1 educator to 4, against 1 to 11 for 3+, same fee): more staff time per place, about +{2 if c=='South Morang' else 4}–{3 if c=='South Morang' else 6} points of wage to revenue not in the forecast." if on3 else "no change in mix ahead.", on3),
               how([("Today's children", "each child's age in months from Owna, aged forward a month at a time; 2027 school leavers out from January"),
                    ("New starters", f"at the last six months' mix: {ag['mix']}% under 3 at start (May–Nov 26); forecast spots {ag['starters']}"),
                    ("Why it matters", "Victorian ratios: under 3s 1:4, 3 and over 1:11 — an under-3 place needs nearly three times the educator time, at the same daily fee"),
                    ("Effect", f"educator time per booked place vs today: Feb about +{8 if c=='South Morang' else 12}%, Jun about +7%")],
                   "A flag for checking: the starter mix counts only children still enrolled; ages are whole months."))
    soon = '<div class="wg-soon">Being validated before they appear: hours against the ratios · rostered against worked · fixed wages</div>'
    return f'<li class="kp wg-main"><div class="wg-flaghead">Flags are for checking, not hard limits.</div>{b1}{b2}{b3}{soon}</li>'

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
    <p>Three views, each with its workings under "How it's worked out". Flags are prompts to check with Robyn, not hard limits.</p>
    <p><b>Wage to revenue</b> is on the cash flow model's definition throughout (wages net of the Worker Retention Grant ÷ income), so the actual months, the November estimate and the forecast line up.</p>
    <p><b>Early warning</b> uses the dashboard's weekly roster cost against booked fees from Owna. It moves before Xero does, but only as a direction.</p>
    <p><b>Age mix ahead</b> uses each child's age in months from Owna; no names or birth dates are held.</p>
    <p>Measures still being validated (hours against the ratios, rostered against worked, fixed wages) will appear once they explain the June–September results.</p>
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
.wg-flag { font-size:11.5px; font-weight:800; color:#8a5a10; background:rgba(227,155,45,.14); border-radius:8px; padding:6px 9px; margin-top:4px; line-height:1.35; }
.wg-flag.off { color:#4d6a3a; background:rgba(110,139,87,.14); }
.wg-flaghead { font-size:11px; font-weight:800; color:var(--ink-50); padding-bottom:2px; }
.wg-soon { font-size:11px; font-weight:700; color:var(--ink-50); padding:12px 0 0; }
.wg-soonh { font-size:10.5px; font-weight:800; color:var(--ink-50); text-transform:uppercase; letter-spacing:.04em; padding-bottom:4px; }
.wg-soonrow { opacity:.5; padding:6px 0; } .wg-soonrow b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:14px; } .wg-soonrow span { font-size:11px; font-weight:700; }
"""
