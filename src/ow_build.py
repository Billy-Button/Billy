"""Occupancy and Wages in the Pipeline pattern: Yesterday · Week · Month."""
import sys, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "kpi"))
import occ as O
import pipeline_build as pl
import wages_build as wg
PLACES = {"South Morang": 108, "Craigieburn": 174}
import kpi.enrolled as EN, datetime as _dt
OCC_T = {"South Morang": 85, "Craigieburn": 70}
DAY = {}
for c, d, b, a, k, h in O.D: DAY[(c, dt.date.fromisoformat(d))] = (b or 0, a or 0, k or 0, h or 0)
def tot(c, days, j): return sum(DAY.get((c, d), (0, 0, 0, 0))[j] for d in days)
def wdays(days): return [d for d in days if d.weekday() < 5]
def odays(days): return [d for d in days if pl.workday(d)]
def month_days(m):
    y, mo = int(m[:4]), int(m[5:]); d = dt.date(y, mo, 1); out = []
    while d.month == mo: out.append(d); d += dt.timedelta(days=1)
    return out
WLABS = [str(w[-1].day) for w in pl.WEEKS]; WGRP = [f"{w[-1]:%b}" for w in pl.WEEKS]
WMARK = {i for i, w in enumerate(pl.WEEKS) if any(d in pl.CLOSED for d in w)}
MLABS = [f"{dt.date.fromisoformat(m+'-01'):%b}" for m in pl.MONTHS]
pc = lambda v: f"{v:.0f}%"
def crow(label, big, sub, vals, tgt, tlab, fmtv, labels, groups=None, marks=(), n_avg=None, details=(), fname="Forecast", avgname="3-mth average", lower=False, zoom=False, ghost=0, compact=False, **kw):
    use = [v for v in (vals[-n_avg:] if n_avg else vals) if v is not None]; avg = sum(use) / len(use) if use else None
    if ghost: avg = None
    line = sub(avg) if callable(sub) else sub
    ch = pl.bars(labels, vals, avg, tgt, tlab, fmtv, lower, marks, groups, avgname, fname=fname, zoom=zoom, ghost=ghost, compact=compact, **kw)
    return (f'<li class="pd-r"><div class="pd-t"><b>{label}</b></div><div class="pd-b"><div class="pd-n">{big}</div><div class="pd-s">{line}</div></div>{ch}{pl.det(list(details))}</li>')
def yrow(label, big, sub, arrow="", details=()):
    return f'<li class="pd-r"><div class="pd-t"><b>{label}</b></div><div class="pd-b"><div class="pd-n">{big}</div><div class="pd-s">{sub}</div>{arrow}</div>{pl.det(list(details))}</li>'
def narrow(y, avg, tol):
    if abs(y - avg) < tol: return '<span class="pd-ar lvl">● level</span>'
    return '<span class="pd-ar lvl">▲ up</span>' if y > avg else '<span class="pd-ar lvl">▼ down</span>'
# ================= Occupancy =================
def occ_pct(c, days):
    wd = wdays(days); return 100 * tot(c, wd, 0) / (PLACES[c] * len(wd)) if wd else None
OD = {"occ": "All Owna booked child-days, casual days included, ÷ licensed places × weekdays. A closed weekday still counts its bookings.",
      "came": "Children signed in to Owna ÷ children booked, on open days.",
      "cas": "Casual days booked in Owna. They are inside the occupancy figure.",
      "net": "Spots gained from children starting, less spots lost from children leaving (school leavers apart). The detail is on the Pipeline screen."}
def first_chart(c, now, nxt):
    lv = [fo(c, k) for k in LAYERS]; cols = [("Enrolled", None)] + [(FM_[i], i) for i in nxt]
    W, H, L, R, T, B = 340, 150, 4, 4, 22, 18; bw = (W - L - R) / len(cols); hi = max([now] + [lv[2][i] for i in nxt]) * 1.1
    ys = lambda p: T + (H - T - B) * (1 - p / hi); y0 = H - B; g = ""
    for j, (lab, i) in enumerate(cols):
        x = L + j * bw + 6; w = bw - 28
        if i is None:
            g += f'<rect x="{x:.1f}" y="{ys(now):.1f}" width="{w:.1f}" height="{y0-ys(now):.1f}" rx="2.5" fill="{pl.INK}" opacity=".78"/><text x="{x+w/2:.1f}" y="{ys(now)-4:.1f}" text-anchor="middle" font-size="10" font-weight="800" fill="{pl.INK}">{now:.0f}</text>'
        else:
            b_, f_, t_ = (lv[k][i] for k in range(3))
            g += f'<rect x="{x:.1f}" y="{ys(b_):.1f}" width="{w:.1f}" height="{y0-ys(b_):.1f}" fill="{C_BASE}"/><text x="{x+w/2:.1f}" y="{ys(b_)+12:.1f}" text-anchor="middle" font-size="10" font-weight="800" fill="#FBF6EE">{b_:.0f}</text>'
            for lo_, hi_, col, op in ((b_, f_, C_FC, 1), (f_, t_, C_TG, .6)):
                if hi_ - lo_ > 0.05: g += f'<rect x="{x:.1f}" y="{ys(hi_):.1f}" width="{w:.1f}" height="{max(ys(lo_)-ys(hi_)-1,1.5):.1f}" fill="{col}" opacity="{op}"/>'
            tx = x + w + 3; ly = y0; prev = round(b_)
            for v, col in ((f_, "#9a7300"), (t_, "#4d6b3c")):
                d = round(v) - prev; prev = round(v)
                if d > 0:
                    yy = min(ys(v) + 3.5, ly - 9.5); ly = yy
                    g += f'<text x="{tx:.1f}" y="{yy:.1f}" font-size="9" font-weight="800" fill="{col}">+{d}</text>'
        g += f'<text x="{x+w/2:.1f}" y="{H-5}" text-anchor="middle" font-size="9.5" font-weight="{800 if i is None else 600}" fill="{pl.INK}" opacity=".8">{lab}</text>'
    g += f'<line x1="{L}" y1="{y0}" x2="{W-R}" y2="{y0}" stroke="{pl.INK}" opacity=".25"/>'
    return f'<svg class="pm-ch" viewBox="0 0 {W} {H}">{g}</svg>'
def occ_yesterday(c):
    y = pl.Y; b, a, k, h = DAY.get((c, y), (0, 0, 0, 0)); lw = odays(pl.LW); n = len(lw) or 1
    lb = tot(c, lw, 0) / n; la = tot(c, lw, 1) / n
    wk = odays(pl.WK)
    rows = (yrow("Children booked", f"{b}", f"{100*b/PLACES[c]:.0f}% of {PLACES[c]} places", pl.arrow(b, lb) if False else ('<span class="pd-ar up">▲ up</span>' if b - lb >= 2 else '<span class="pd-ar dn">▼ down</span>' if lb - b >= 2 else '<span class="pd-ar lvl">● level</span>'),
                 [("Last week:", f"{lb:.0f} booked a day on average ({len(lw)} open days, week ending {pl.fd(pl.LW[-1])})."), ("Arrow:", "the day against last week's average a day; level when within 2 children. Days of the week differ: Fridays and Mondays are lighter."), ("Measure:", OD["occ"])])
            + yrow("Children who came", f"{a}", f"{100*a/b:.0f}% of those booked" if b else "–", "", [("Last week:", f"{la:.0f} a day on average, {100*tot(c, lw, 1)/max(tot(c, lw, 0),1):.0f}% of those booked."), ("Measure:", OD["came"])])
            + yrow("Casual days", f"{k}", f"{tot(c, wk, 2)} so far this week", "", [("Last week:", f"{tot(c, lw, 2)} casual days."), ("Measure:", OD["cas"])]))
    return f'<div class="pd"><ul class="pd-l">{rows}</ul>' + pl.about(f"What happened on {pl.YLAB}, from Owna as at this morning's dashboard build.") + '</div>'
def occ_summary(c):
    if not REG_OK: return pending_note()
    nxt = list(range(NOWI + 1, NOWI + 4)); bc = fo(c, "base_case"); now = occ_pct(c, pl.WEEKS[-1])
    ch = f'<div class="fc-leg"><span><i style="background:{pl.INK};opacity:.78"></i>Enrolled</span>{LEG3}</div>' + first_chart(c, 100 * (EN.E[c][1] + EN.CAS[c]) / (PLACES[c] * 5), nxt)
    en, es, nn, ns = EN.E[c]; ca = EN.CAS[c]; ep = 100 * (es + ca) / (PLACES[c] * 5); ad = _dt.date.fromisoformat(EN.AS_AT)
    top = (f'<li class="pd-r oc-first"><div class="pd-t"><b>Occupancy</b></div>'
           f'<div class="fc-hd"><div><span>Enrolled</span><b>{ep:.1f}%</b><em>{es+ca:.0f} of {PLACES[c]*5} spots, as at {ad:%a} {ad.day} {ad:%b}</em></div><div class="ar">→</div>'
           f'<div class="k"><span>Base Case, end {FM_[nxt[-1]]}</span><b>{bc[nxt[-1]]:.0f}%</b><em>end {FM_[nxt[0]]} {bc[nxt[0]]:.0f}% · {FM_[nxt[1]]} {bc[nxt[1]]:.0f}%</em></div></div>{ch}'
           f'<p class="oc-def"><b>Enrolled occupancy</b> is the booked days a week of every child enrolled in Owna, including {nn} not yet started ({ns:.0f} spots), plus last week\'s {ca} casual days ({EN.CAS_WEEK}), ÷ {PLACES[c]} licensed places × 5. Without casuals: {100*es/(PLACES[c]*5):.1f}%.</p>'
           + f'<p class="oc-def">{DEF_BASE}</p><p class="oc-def">{DEF_REST}</p><p class="mtag">{MODEL_TAG}</p>'
           + pl.det([("Enrolled:", f"{en} children enrolled in Owna, {es:.0f} booked days a week, including {nn} children not yet started, plus {ca} casual days last week ({EN.CAS_WEEK}). Dashboard snapshot {EN.SNAP[:10]}."),
                     ("Last week:", f"booked child-days, casual days included, over {PLACES[c]} places × open days: {now:.1f}%. From Owna."),
                     ("Basis:", "long day care spots a week, casual included, over licensed places × 5. Each month is the position at the end of that month."),
                     ("Columns:", f"each of the next three months, from the Financial Model. The white number is the Base Case; the +numbers are the points the {FCL} and the Target add. The levels are from the model; each +number is the difference between one level and the next."),
                     ("More:", "every month to June is on the Forecast screen.")]) + '</li>')
    return f'<div class="pd"><ul class="pd-l">{top}</ul>' + pl.about("Enrolled and last week are from Owna. The three months ahead are from the Financial Model; the app calculates none of them.") + '</div>'
def occ_charts(c, periods, labels, groups, marks, n_avg, word):
    occ = [occ_pct(c, p) for p in periods]
    came = [100 * tot(c, odays(p), 1) / tot(c, odays(p), 0) if tot(c, odays(p), 0) else None for p in periods]
    cas = [tot(c, p, 2) for p in periods]
    st = [pl.ev(c, p, "st") for p in periods] if word == "week" else [pl.MS.get((c, m, "st"), (0, 0))[0] for m in pl.MONTHS]
    lo = [pl.ev(c, p, "lo") for p in periods] if word == "week" else [pl.MS.get((c, m, "lo"), (0, 0))[0] for m in pl.MONTHS]
    net = [a - b for a, b in zip(st, lo)]; t = fo(c, "target")[NOWI]; mf = fo(c, "forecast")[NOWI]; mn = FM_[NOWI]
    f0 = lambda v: f"{v:.0f}"
    sgn = lambda v: f"{'+' if v > 0 else '−' if v < 0 else ''}{abs(v):g}"
    rows = (crow("Occupancy", f"{occ[-1]:.0f}<small>%</small>", lambda a: f"{mn} forecast {mf:.0f}% · target {t:.0f}%", occ, t, f"{t:.0f}%", f0, labels, groups, marks, n_avg,
                 [("Spots:", f"{tot(c, wdays(periods[-1]), 0)} booked child-days in the {word}."), ("Measure:", OD["occ"]), ("Dashed line:", "the average of the bars shown. It is not the forecast."),
                  ("Forecast and target:", f"{mn}'s figures from the {MODEL_TAG}."), ("Industry:", "LineLeader's benchmark reports put the level a centre needs to be sustainable at 70 to 75% occupancy (its customers, mostly US; under review)."), ("Chart:", "the scale starts above zero so the weeks can be told apart; the numbers on the bars are the percentages.")], zoom=True, compact=True, fname="Average")
            + crow("Children who came", f"{came[-1]:.0f}<small>%</small>", lambda a: f"of booked · average {a:.0f}%", came, None, "", f0, labels, groups, marks, n_avg,
                   [("Measure:", OD["came"]), ("Why it matters:", "booked days are charged whether or not the child comes; a low share means more absences, which is spare room on the day."), ("Chart:", "the scale starts above zero; the numbers on the bars are the percentages.")], fname="Average", zoom=True, compact=True)
            + crow("Casual days", f"{cas[-1]:g}", lambda a: f"average {a:.1f} a {word}", cas, None, "", pl.fmt1, labels, groups, marks, n_avg, [("Measure:", OD["cas"])], fname="Average", compact=True)
            + yrow("Net spots", sgn(net[-1]), f"started {st[-1]:g} · lost {lo[-1]:g}", "", [(f"Over the {'13 weeks' if word == 'week' else 'last three months'}:", f"{sgn(sum(net[-(n_avg or len(net)):]))} spots (started {sum(st[-(n_avg or len(st)):]):g}, lost {sum(lo[-(n_avg or len(lo)):]):g})."), ("Measure:", OD["net"])]))
    return rows
def occ_week(c):
    return (f'<div class="pd oc-c"><ul class="pd-l">{occ_charts(c, pl.WEEKS, WLABS, WGRP, WMARK, None, "week")}</ul><p class="pd-key">Dashed = average · Green = target for this month, from the model</p>{tag()}'
            + pl.about(f"The 13 complete weeks to {pl.WLAB}. Occupancy counts Monday to Friday. The number under each bar is the Friday the week ended. * = a week with a closed day.") + '</div>')
def occ_month(c):
    return (f'<div class="pd oc-c"><ul class="pd-l">{occ_charts(c, [month_days(m) for m in pl.MONTHS], MLABS, None, (), 3, "month")}</ul><p class="pd-key">Dashed = average · Green = target for this month, from the model</p>{tag()}'
            + pl.about(f"Complete months, {MLABS[0]} to {MLABS[-1]} 2026. Dashed line = the average of the last three months.") + '</div>')
# ================= Forecast tab: every figure from the Financial Model feed =================
# kpi/model_feed.json is a copy of the project doc claude/model/billy-feed.json. Nothing here is calculated: figures are shown as the feed gives them (rounded for display).
import json as _json
_KP = pathlib.Path(__file__).resolve().parent / "kpi"
FEED = _json.load(open(_KP / "model_feed.json"))
REG = _json.load(open(_KP / "model_register.json"))          # copy of the version named in claude/model/model-register.md
REG_OK = REG["version"] == FEED["version"]
FM_ = FEED["months"]; NOWI = FM_.index(f"{pl.TODAY:%b}")          # the month we are in
MODEL_TAG = (f'Financial Model {FEED["version"]} · working draft · wages conditional on the roster review' if REG_OK
             else f'Model update pending: the register names {REG["version"]}; the app still holds {FEED["version"]}')
FCL = "Forecast (12-week trend)"
def tag(): return f'<p class="mtag">{MODEL_TAG}</p>'
def pending_note(): return f'<div class="pd"><p class="mtag">{MODEL_TAG}. Model figures are hidden until the app is updated.</p></div>'
C_BASE, C_FC, C_TG = pl.EARTH, "#FDC546", pl.SAGE
LAYERS = ("base_case", "forecast", "target")
def fo(c, k): return FEED["centres"][c]["monthly_closing"]["occupancy_pct"][k]
DEF_BASE = ("<b>Base Case</b> means this week's enrolments carried forward. Leavers and fewer days run at the last 12 weeks' rate, extra days are added, "
            "and children starting school come out. Pending families are counted on their Owna start date: pulled through in full, forms in at the last 12 weeks' pull rate. "
            "No new enrolments from enquiries are added.")
DEF_REST = (f"<b>{FCL}</b>: {FEED['definitions']['forecast_plain']} It adds new enrolments from enquiries at the last 12 weeks' rate, starting in February. "
            "<b>Target</b> is what each month needs to be to reach 85% at South Morang and 70% at Craigieburn by 30 June 2027.")
LEG3 = (f'<span><i style="background:{C_BASE}"></i>Base Case</span><span><i style="background:{C_FC}"></i>{FCL}</span>'
        f'<span><i style="background:rgba(110,139,87,.6)"></i>Target</span>')
def plus(c, i):
    r = [round(fo(c, k)[i]) for k in LAYERS]; f = lambda d: f"+{d}" if d > 0 else "–"
    return r[0], f(r[1] - r[0]), f(r[2] - r[1]), r[2]
def stack_chart(c):
    lv = [fo(c, k) for k in LAYERS]
    oct_ = occ_pct(c, month_days("2026-10")); mtd = occ_pct(c, [d for d in month_days(f"{pl.TODAY:%Y-%m}") if d <= pl.Y])
    cols = [("Oct", oct_, "fin"), (FM_[NOWI], mtd, "mtd")] + [(FM_[i], i, "m") for i in range(NOWI + 1, len(FM_))]; n = len(cols)
    W, H, L, R, T, B = 340, 176, 4, 4, 16, 30; bw = (W - L - R) / n; hi = max([oct_, mtd] + [lv[2][i] for i in range(NOWI + 1, len(FM_))]) * 1.14
    ys = lambda p: T + (H - T - B) * (1 - p / hi); y0 = H - B; g = ""
    for j, (lab, v, kind) in enumerate(cols):
        x = L + j * bw + 3; w = bw - 6
        if kind != "m":
            col = pl.INK if kind == "fin" else "#9b948c"
            g += f'<rect x="{x:.1f}" y="{ys(v):.1f}" width="{w:.1f}" height="{y0-ys(v):.1f}" fill="{col}" opacity="{.78 if kind == "fin" else 1}"/>'
            g += f'<text x="{x+w/2:.1f}" y="{ys(v)+10:.1f}" text-anchor="middle" font-size="8" font-weight="800" fill="#FBF6EE">{v:.0f}</text>'
        else:
            i = v; b_, f_, t_ = (lv[k][i] for k in range(3))
            g += f'<rect x="{x:.1f}" y="{ys(b_):.1f}" width="{w:.1f}" height="{y0-ys(b_):.1f}" fill="{C_BASE}" opacity=".9"/>'
            for lo_, hi_, col, op in ((b_, f_, C_FC, 1), (f_, t_, C_TG, .6)):
                if hi_ - lo_ > 0.05: g += f'<rect x="{x:.1f}" y="{ys(hi_):.1f}" width="{w:.1f}" height="{max(ys(lo_)-ys(hi_)-1,1):.1f}" fill="{col}" opacity="{op}"/>'
            prev = round(b_)
            for lo_, hv, col in ((b_, f_, "#5a4300"), (f_, t_, "#2f4a22")):
                d = round(hv) - prev; prev = round(hv)
                if d > 0 and ys(lo_) - ys(hv) >= 9: g += f'<text x="{x+w/2:.1f}" y="{(ys(lo_)+ys(hv))/2+3:.1f}" text-anchor="middle" font-size="8" font-weight="800" fill="{col}">+{d}</text>'
            if t_ - b_ > 0.05: g += f'<text x="{x+w/2:.1f}" y="{ys(t_)-3:.1f}" text-anchor="middle" font-size="8.5" font-weight="800" fill="{pl.INK}" stroke="#FBF6EE" stroke-width="2.5" paint-order="stroke">{t_:.0f}</text>'
            g += f'<text x="{x+w/2:.1f}" y="{ys(b_)+10:.1f}" text-anchor="middle" font-size="8" font-weight="800" fill="#FBF6EE">{b_:.0f}</text>'
        g += f'<text x="{x+w/2:.1f}" y="{y0+11}" text-anchor="middle" font-size="8" font-weight="{800 if lab == "Feb" else 600}" fill="{pl.INK}" opacity="{.9 if lab == "Feb" else .6}">{lab}</text>'
    for xa, xb, lab in ((L + 2, L + 2 * bw - 2, "Actual"), (L + 2 * bw + 2, W - R - 2, "From the model")):
        g += f'<line x1="{xa:.1f}" y1="{H-13}" x2="{xb:.1f}" y2="{H-13}" stroke="{pl.INK}" opacity=".25"/><text x="{(xa+xb)/2:.1f}" y="{H-3}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{pl.INK}" opacity=".6">{lab}</text>'
    return f'<svg class="pm-ch" viewBox="0 0 {W} {H}">{g}</svg>'
def bridge(c):
    M = FEED["centres"][c]["monthly_closing"]; fl = FEED["centres"][c]["flows_monthly"]; pe = FEED["centres"][c]["pending"]; cap = FEED["centres"][c]["capacity_spots_a_week"]
    bs = M["spots"]["base_case"]; cols = list(range(NOWI + 1, min(NOWI + 4, len(FM_)))); n0 = lambda v: f"{v:,.0f}"
    sg = lambda v, s: "–" if round(v) == 0 else f"{s}{v:,.0f}"
    hd = "".join(f"<th>{FM_[i]}</th>" for i in cols)
    row = lambda lab, vals, cls="": f'<tr class="{cls}"><td>{lab}</td>' + "".join(f"<td>{v}</td>" for v in vals) + "</tr>"
    body = (row("Base Case at start", [n0(bs[i - 1]) for i in cols], "br-o")
            + row("Less leavers and fewer days", [sg(fl["leavers_and_fewer_days"][i], "−") for i in cols])
            + row("Plus extra days", [sg(fl["extra_days"][i], "+") for i in cols])
            + row("Less school leavers", [sg(fl["school_leavers"][i], "−") for i in cols])
            + row("Plus pending families starting", [sg(fl["pending_starts"][i], "+") for i in cols])
            + row("Base Case at month end", [n0(bs[i]) for i in cols], "br-c")
            + row("Occupancy", [f"{fo(c, 'base_case')[i]:.0f}%" for i in cols], "br-p"))
    ex = pe["excluded_for_follow_up"]
    memo = (f'Pending: {pe["pulled_through_spots"]} spots pulled through, counted in full; {pe["form_in_spots_before_conversion"]} spots with a form in, counted at the last 12 weeks\' pull rate of {pe["pull_rate_last_12_weeks"]*100:.0f}%. '
            f'{ex["records"]} pending record{"s" if ex["records"] != 1 else ""} count as nil until updated in Owna (see Pipeline).')
    return (f'<div class="pd-ind br"><div class="pd-indh">How the Base Case is built <span>spots a week</span></div>'
            f'<table class="br-t"><tr><th></th>{hd}</tr>{body}</table><p class="br-m">{memo}</p>'
            + pl.det([("Source:", "every figure is from the Financial Model feed. Spots are rounded, so a column can be out by one."),
                      ("Spots:", f"one child booked for one day a week. Capacity is {cap} spots a week."),
                      ("Casual:", "casual spots are held at the current level inside the starting figure; the feed does not show them as a separate line."),
                      ("Leavers:", "leavers and fewer days run at the last 12 weeks' rate. Children starting school come out in the month Owna says they finish.")]) + '</div>')
def occ_forecast(c):
    F_ = FEED["centres"][c]["monthly_closing"]; fi = FM_.index("Feb"); ji = FM_.index("Jun"); now = occ_pct(c, pl.WEEKS[-1])
    fc = fo(c, "forecast"); ses = F_["occupancy_incl_sessional_pct"]
    tr = "".join('<tr><td>{}</td><td>{}%</td><td>{}</td><td>{}</td><td><b>{}%</b></td></tr>'.format(FM_[i], *plus(c, i)) for i in range(NOWI, len(FM_)))
    table = (f'<div class="pd-ind"><div class="pd-indh">Month by month, at month end <span>from the model</span></div>'
             f'<table class="fc-t"><tr><th></th><th>Base Case</th><th>Forecast</th><th>Target</th><th>Reaches</th></tr>{tr}</table>'
             + pl.det([("Forecast column:", f"the points the {FCL} adds on top of the Base Case."), ("Target column:", "the points the Target adds on top of the Forecast."),
                       ("Reaches:", "where that month's Target lands."), ("Added points:", "the levels are from the model; each +number is the difference between one level and the next."),
                       ("Sessional kinder:", f"the 85% and 70% targets count sessional kinder children (2 days each). On that basis June reads Forecast {ses['forecast'][ji]:.0f}% and Target {ses['target'][ji]:.0f}%; February reads Forecast {ses['forecast'][fi]:.0f}% and Target {ses['target'][fi]:.0f}%. The table and chart are long day care only.")]) + '</div>')
    row = (f'<li class="pd-r"><div class="pd-t"><b>Occupancy at the end of February</b></div>'
           f'<div class="fc-hd"><div><span>Last week</span><b>{now:.0f}%</b><em>Owna, to {pl.WEEKS[-1][-1]:%a} {pl.WEEKS[-1][-1].day} {pl.WEEKS[-1][-1]:%b}</em></div><div class="ar">→</div>'
           f'<div class="k"><span>Forecast, end Feb</span><b>{fc[fi]:.0f}%</b><em>12-week trend</em></div></div>'
           f'<table class="fc-3"><tr><th>End of February</th><th>Base Case</th><th>Forecast</th><th>Target</th></tr>'
           + '<tr><td></td><td>{}%</td><td>{}</td><td>{}</td></tr></table>'.format(*plus(c, fi)[:3])
           + f'<div class="fc-leg"><span><i style="background:{pl.INK};opacity:.78"></i>Finished month</span><span><i style="background:#9b948c"></i>{FM_[NOWI]} to date</span>{LEG3}</div>{stack_chart(c)}'
           + pl.det([("Actual:", f"October is a finished month. {FM_[NOWI]} shows the month so far, to {pl.YLAB}, from Owna. The model's own {FM_[NOWI]} figure is in the table below."),
                     ("Reading it:", "from the next month on, each column is the model. The white number is the Base Case, the +numbers are the points the Forecast and the Target add, and the number on top is where the Target reaches."),
                     ("Source:", "every model figure is from the Financial Model feed. The app calculates none of them.")]) + '</li>')
    return (f'<div class="pd"><h2 class="fc-h">Occupancy</h2>{bridge(c)}<ul class="pd-l">{row}</ul>{table}'
            + pl.about(f"{FM_[NOWI]} 2026 to June 2027, by month, long day care. The model is a working draft and its wages are conditional on the roster review with the Managing Director.") + '</div>')
def wg_forecast(c):
    w = FEED["centres"][c]["wage_plan_forecast"]; inc = FEED["centres"][c]["income_total_forecast"]; A = wg.F[c]
    labels = ["Aug", "Sep", "Oct"] + FM_[NOWI:]; grp = ["Actual"] * 3 + ["Model"] * (len(FM_) - NOWI); gh = len(FM_) - NOWI
    f0 = lambda v: f"{v:.0f}"; nx = range(NOWI + 1, NOWI + 4); st = w["educator_steps_from_base_roster"]
    w2r = A["w2r"][1:4] + w["wage_to_revenue_pct"][NOWI:]; wk = [v / 1e3 for v in A["wages"][1:4]] + [v / 1e3 for v in w["total_wages"][NOWI:]]
    sgn = lambda v: "0" if v == 0 else (f"+{v}" if v > 0 else f"−{abs(v)}")
    rows = (crow("Wage to revenue", f"{w['wage_to_revenue_pct'][NOWI]:.0f}<small>% {FM_[NOWI]}</small>", " · ".join(f"{FM_[i]} {w['wage_to_revenue_pct'][i]:.0f}%" for i in nx), w2r, None, "", f0, labels, grp, (), None,
                 [("Measure:", "total wages as a share of total income, as the model gives it."), ("Solid bars:", "Xero actuals."), ("Outlined bars:", "the model."), ("Chart:", "the scale starts above zero.")], zoom=True, ghost=gh)
            + crow("Wages", f"${w['total_wages'][NOWI]/1e3:.0f}k<small> {FM_[NOWI]}</small>", " · ".join(f"{FM_[i]} ${w['total_wages'][i]/1e3:.0f}k" for i in nx), wk, None, "", lambda v: f"{v:.0f}k", labels, grp, (), None,
                   [("Measure:", "total wages, $000 a month. Solid = Xero; outlined = the model."), ("Chart:", "the scale starts above zero.")], zoom=True, ghost=gh)
            + yrow("Educators against the base roster", sgn(st[NOWI]) + f"<small> {FM_[NOWI]}</small>", " · ".join(f"{FM_[i]} {sgn(st[i])}" for i in range(NOWI + 1, len(FM_))),
                   details=[("Measure:", "educator steps on or off the base roster, by month, under the roster step rule in the model."), ("Conditional:", "settled at the roster review with the Managing Director.")]))
    return (f'<div class="pd"><h2 class="fc-h">Wages</h2><ul class="pd-l">{rows}</ul><p class="pd-key">Solid = actual · Outlined = model</p>'
            + pl.about(f"{FM_[NOWI]} 2026 to June 2027, by month. Every model figure is from the Financial Model feed. How the roster is set to meet these months is a question for Robyn.") + '</div>')
def occ_section(logo, back, sm_ahead, cb_ahead, legend, foot, week_label):
    def centre(c, ahead):
        if not REG_OK: return pending_note()
        return (f'<div data-pane="s">{occ_summary(c)}</div><div data-pane="d" hidden>{occ_yesterday(c)}</div><div data-pane="w" hidden>{occ_week(c)}</div><div data-pane="m" hidden>{occ_month(c)}</div>')
    return f'''
<section id="report" class="scr" hidden>
  <header class="topbar">{back}
    <div class="ttl"><h1>Occupancy</h1><div class="sub" data-s="Last week and the next three months" data-d="Yesterday · {pl.YLAB}" data-w="Week ending {pl.WLAB}" data-m="Month ending {pl.MLAB}">Last week and the next three months</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <div class="pfbar">
  <nav class="toggle" role="tablist" aria-label="Centre">
    <button type="button" role="tab" id="tab-sm" aria-controls="south-morang" aria-selected="true" data-target="south-morang">South Morang</button>
    <button type="button" role="tab" id="tab-cb" aria-controls="craigieburn" aria-selected="false" data-target="craigieburn">Craigieburn</button>
  </nav>{PTABS}
  </div>
  <div class="screens">
    <div id="south-morang" class="screen" role="tabpanel" aria-labelledby="tab-sm">{centre("South Morang", sm_ahead)}</div>
    <div id="craigieburn" class="screen" role="tabpanel" aria-labelledby="tab-cb" hidden>{centre("Craigieburn", cb_ahead)}</div>
  </div>
  <details class="foot">{foot}</details>
</section>'''

# ================= Forecast screen =================
DEFS = [("Base Case", C_BASE, "This week's enrolments carried forward: leavers at the last 12 weeks' rate, children starting school out, pending families in on their start date. No new enrolments from enquiries."),
        (FCL, "#c99700", FEED["definitions"]["forecast_plain"] + " New enrolments from enquiries start in February."),
        ("Target", C_TG, "What each month needs to be to reach 85% at South Morang and 70% at Craigieburn by 30 June 2027.")]
def forecast_section(logo, back, sm_ahead, cb_ahead, legend, week_label):
    defs = "".join(f'<li><i style="background:{col}"></i><b>{n}</b><span>{t}</span></li>' for n, col, t in DEFS)
    def centre(c, ahead):
        return (occ_forecast(c) + wg_forecast(c)
                + f'<details class="oc-ahead"><summary>What Owna holds today: school leavers, enrolled, forms in</summary><div class="pd-indh">Owna counts</div><p class="pd-key" style="text-align:left;margin:0 0 6px">As at {week_label}. Counts from Owna. They are not the base case or pending figures of the model.</p><div class="legend">{legend}</div>{ahead}</details>')
    return f"""
<section id="forecast" class="scr" hidden>
  <header class="topbar">{back}
    <div class="ttl"><h1>Forecast</h1><div class="sub">{FM_[NOWI]} 2026 to June 2027</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <div class="pfbar">
  <nav class="toggle fc" role="tablist" aria-label="Centre">
    <button type="button" role="tab" aria-selected="true" data-fc="fc-sm">South Morang</button>
    <button type="button" role="tab" aria-selected="false" data-fc="fc-cb">Craigieburn</button>
  </nav>
  </div>
  <div class="fc-top">{tag()}<ul class="fc-defs">{defs}</ul></div>
  <div class="screens">
    <div id="fc-sm" class="screen">{centre("South Morang", sm_ahead)}</div>
    <div id="fc-cb" class="screen" hidden>{centre("Craigieburn", cb_ahead)}</div>
  </div>
  <details class="foot"><summary>About this screen</summary><div class="foot-body">
    <p>Everything on this screen looks ahead. Every base case, pending, forecast and target figure comes from the Financial Model; the app does not calculate any of them. The model's version and status are shown at the top.</p>
    <p>What has already happened is on the Occupancy, Wages, Pipeline and Tours screens, from the Billy Button dashboard.</p>
    <p>Still to come here: cash, profit and loss, and a summary balance sheet.</p></div></details>
</section>"""
PTABS = '''
  <nav class="pdtabs ptabs" role="tablist" aria-label="Period">
    <button type="button" role="tab" aria-selected="true" data-p="s">Summary</button>
    <button type="button" role="tab" aria-selected="false" data-p="d">Yesterday</button>
    <button type="button" role="tab" aria-selected="false" data-p="w">Week</button>
    <button type="button" role="tab" aria-selected="false" data-p="m">Month</button>
  </nav>'''
# ================= Wages =================
WD = {"hrs": "Owna rostered hours for all staff (paid minutes), from the dashboard's overnight build.",
      "hpc": "Rostered hours ÷ children booked, on open days. All staff, not educators only; it does not adjust for the age mix."}
def wg_yesterday(c, parts):
    y = pl.Y; b, a, k, h = DAY.get((c, y), (0, 0, 0, 0)); lw = odays(pl.LW); n = len(lw) or 1
    lh = tot(c, lw, 3) / n; lhc = tot(c, lw, 3) / max(tot(c, lw, 0), 1); m = wg.month_dollars(c)
    rows = (yrow("Rostered hours", f"{h:.0f}", f"for {b} children booked", narrow(h, lh, 5),
                 [("Last week:", f"{lh:.0f} hours a day on average ({len(lw)} open days)."), ("Arrow:", "the day against last week's average; level when within 5 hours. Grey because more hours is neither good nor bad on its own."), ("Measure:", WD["hrs"])])
            + yrow("Hours per booked child", f"{h/b:.2f}" if b else "–", f"last week {lhc:.2f}", "", [("Measure:", WD["hpc"])])
            + yrow("To land November on forecast", f"{m['land']:.0f}<small>hrs a day</small>", f"for the {m['left']} days left", "",
                   [("How:", f"forecast wages ${m['fw']/1e3:.0f}k ÷ ${m['rate']:.0f} an hour = {m['allow_h']:,.0f} hours for the month; less {m['used']:,.0f} used, ÷ {m['left']} days left."), ("Forecast:", "the cash flow model, which is a draft in its final build."), ("Note:", "the full working is under This month on the Month tab.")]))
    return f'<div class="pd"><ul class="pd-l">{rows}</ul></div><div class="centre"><ul class="measures kpl"><li class="kp wg-main">{parts["dd"]}</li></ul></div>'
def wg_week(c):
    hrs = [tot(c, odays(w), 3) / max(len(odays(w)), 1) for w in pl.WEEKS]
    hpc = [tot(c, odays(w), 3) / tot(c, odays(w), 0) if tot(c, odays(w), 0) else None for w in pl.WEEKS]
    f2 = lambda v: f"{v:.2f}"; f0 = lambda v: f"{v:.0f}"; occ = [occ_pct(c, w) for w in pl.WEEKS]
    rows = (crow("Rostered hours a day", f"{hrs[-1]:.0f}", lambda a: f"13-week average {a:.0f}", hrs, None, "", f0, WLABS, WGRP, WMARK, None, [("Measure:", WD["hrs"] + " Average over the open days in each week. The chart's scale starts above zero."), ("Blue line:", f"occupancy for the same weeks, {min(occ):.0f}% to {max(occ):.0f}%, on its own scale. It shows whether hours moved with the children booked; it does not share the bars' scale.")], fname="Average", avgname="13-week average", zoom=True, tall=True, line=occ, linename="Occupancy")
            + crow("Hours per booked child", f"{hpc[-1]:.2f}", lambda a: f"13-week average {a:.2f}", hpc, None, "", f2, WLABS, WGRP, WMARK, None,
                   [("Measure:", WD["hpc"]), ("Reading it:", "a rising bar means more staff time for each booked child. It can come from extra hours or from a younger mix of children; this chart cannot tell which. The chart's scale starts above zero.")], fname="Average", avgname="13-week average", zoom=True))
    return (f'<div class="pd"><ul class="pd-l">{rows}</ul><p class="pd-key">Blue line = occupancy · Dashed = 13-week average · ▲ = off the scale · * = closed day</p>'
            + pl.about(f"The 13 complete weeks to {pl.WLAB}. These are averages for reference, not forecasts: the wages forecast is on the Month tab.") + '</div>')
def wg_summary(c):
    if not REG_OK: return pending_note()
    w = FEED["centres"][c]["wage_plan_forecast"]; A = wg.F[c]; st = w["educator_steps_from_base_roster"]
    idx = list(range(NOWI, NOWI + 4)); labels = ["Oct"] + [FM_[i] for i in idx]; grp = ["Actual"] + ["Model"] * 4; f0 = lambda v: f"{v:.0f}"
    w2r = [A["w2r"][3]] + [w["wage_to_revenue_pct"][i] for i in idx]
    sgn = lambda v: "no change" if v == 0 else (f"{v} more" if v > 0 else f"{abs(v)} fewer"); sg = lambda v: "0" if v == 0 else (f"+{v}" if v > 0 else f"−{abs(v)}")
    rows = (crow("Wage to revenue", f"{A['w2r'][3]:.0f}<small>% Oct</small>", " · ".join(f"{FM_[i]} {w['wage_to_revenue_pct'][i]:.0f}%" for i in idx), w2r, None, "", f0, labels, grp, (), None,
                 [("Solid bar:", "October, the last complete month, from Xero."), ("Outlined bars:", "the Financial Model for this month and the next three."),
                  ("This month so far:", "the daily working for November is on the Month tab."), ("Chart:", "the scale starts above zero.")], zoom=True, ghost=4)
            + yrow("Educators against the base roster", sg(st[NOWI]) + f"<small> {FM_[NOWI]}</small>", " · ".join(f"{FM_[i]} {sg(st[i])}" for i in idx[1:]),
                   details=[("Measure:", "educator steps on or off the base roster under the roster step rule in the model: " + " · ".join(f"{FM_[i]} {sgn(st[i])}" for i in idx) + "."),
                            ("Hours:", "the model no longer gives rostered hours a week. Rostered hours to date are on the Week and Month tabs.")]))
    return (f'<div class="pd"><ul class="pd-l">{rows}</ul>'
            f'<p class="oc-def"><b>Wage to revenue</b> means total wages as a share of total income. <b>Educators against the base roster</b> follow the roster step rule: educators come off as children leave and go back on as children start.</p>'
            f'{tag()}' + pl.about("October is from Xero. This month and the next three are from the Financial Model; the app calculates none of them. How the roster is set to meet these months is a question for Robyn.") + '</div>')
def wages_section(logo, back):
    def centre(c):
        p = wg.panel(c, parts=True)
        return (f'<div data-pane="s">{wg_summary(c)}</div><div data-pane="d" hidden>{wg_yesterday(c, p)}</div><div data-pane="w" hidden>{wg_week(c)}</div>'
                f'<div data-pane="m" hidden><div class="centre"><ul class="measures kpl"><li class="kp wg-main">{p["tm"]}{p["w2r"]}{p["ew"]}{p["age"]}{p["rooms"]}</li></ul></div></div>')
    foot = wg.section(logo); foot = foot[foot.index('<details class="foot">'):foot.index('</section>')]
    return f'''
<section id="wages" class="scr" hidden>
  <header class="topbar">{back}
    <div class="ttl"><h1>Wages</h1><div class="sub" data-s="Last month and the next three" data-d="Yesterday · {pl.YLAB}" data-w="Week ending {pl.WLAB}" data-m="November so far">Last month and the next three</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <div class="pfbar">
  <nav class="toggle wg" role="tablist" aria-label="Centre">
    <button type="button" role="tab" aria-selected="true" data-wg="wg-sm">South Morang</button>
    <button type="button" role="tab" aria-selected="false" data-wg="wg-cb">Craigieburn</button>
  </nav>{PTABS}
  </div>
  <div class="screens">
    <div id="wg-sm" class="screen">{centre("South Morang")}</div>
    <div id="wg-cb" class="screen" hidden>{centre("Craigieburn")}</div>
  </div>
  {foot}
</section>'''
css = """
.br{margin-top:10px}.br-t{width:100%;border-collapse:collapse;font-size:12.5px}.br-t th{font-size:10.5px;font-weight:800;color:rgba(43,35,32,.55);text-align:right;padding:2px 0}
.br-t td{padding:4px 0;border-top:1px solid rgba(43,35,32,.07);font-weight:700}.br-t td:nth-child(n+2){text-align:right;width:58px;font-variant-numeric:tabular-nums}
.pd-ind .br-t td:nth-child(3){color:inherit}.br-t tr.br-o td,.br-t tr.br-c td{font-weight:800}.br-t tr.br-c td{border-top:1.5px solid rgba(43,35,32,.35);color:#A45823}.br-t tr.br-p td{border-top:0;color:rgba(43,35,32,.6);font-size:11.5px;padding-top:0}
.br-m{font-size:11.5px;line-height:1.4;color:rgba(43,35,32,.7);margin:6px 0 2px}
.oc-def{font-size:12.5px;line-height:1.4;color:rgba(43,35,32,.85);margin:6px 0 6px;padding:8px 10px;border-left:3px solid #A45823;background:rgba(164,88,35,.06)}.oc-def b{font-weight:800}
.oc-first .mtag{margin:2px 0 4px}.oc-first .fc-hd .k b{font-size:44px}
.fc-top{padding:4px 18px 0}.fc-defs{list-style:none;margin:6px 0 4px;padding:0}.fc-defs li{display:grid;grid-template-columns:12px 92px 1fr;gap:7px;align-items:baseline;padding:5px 0;border-top:1px solid rgba(43,35,32,.08);font-size:12.5px;line-height:1.35}
.fc-defs li:first-child{border-top:0}.fc-defs i{width:11px;height:11px;border-radius:2px;display:inline-block;transform:translateY(1px)}.fc-defs b{font-weight:800}.fc-defs span{color:rgba(43,35,32,.75)}
.fc-h{font-family:"Fredoka","Nunito",sans-serif;font-weight:600;font-size:20px;margin:14px 0 0;padding-top:12px;border-top:2px solid rgba(43,35,32,.12)}
.mtag{font-size:10.5px;font-weight:800;color:#7a3f17;background:rgba(253,197,70,.28);border-radius:8px;padding:5px 8px;margin:8px 0 6px;line-height:1.3}
.fc-3{width:100%;border-collapse:collapse;margin:0 0 10px}.fc-3 th{font-size:10.5px;font-weight:800;color:rgba(43,35,32,.55);text-align:right;padding:2px 0}.fc-3 th:first-child{text-align:left}
.fc-3 td{font-family:"Fredoka","Nunito",sans-serif;font-weight:600;font-size:22px;text-align:right;border-top:1px solid rgba(43,35,32,.09);padding:2px 0}.fc-3 td:nth-child(2){color:#A45823}.fc-3 td:nth-child(3){color:#47647f}.fc-3 td:nth-child(4){color:#9a7300}.fc-3 td:nth-child(5){color:#4d6b3c}
.oc-c .pd-r{display:grid;grid-template-columns:minmax(0,1fr) 56px 146px;column-gap:6px;align-items:baseline;padding:6px 0 4px}
.oc-c .pd-t b{font-size:15px;white-space:nowrap}.oc-c .pd-b{display:contents}.oc-c .pd-n{font-size:24px;text-align:right}.oc-c .pd-n small{margin-left:1px}.oc-c .pd-s{font-size:11.5px;text-align:left}
.oc-c .pm-ch,.oc-c .pd-d{grid-column:1/-1}.oc-c .pm-ch{margin-top:0}.oc-c .pd-r>.pd-d{margin-top:-2px}.oc-c .pd-r>.pd-d summary{padding:0}
.oc-c{padding-top:0}.oc-c .pd-key{margin:6px 0 0}
.fc-hd{display:flex;align-items:flex-end;gap:14px;margin:6px 0 4px}.fc-hd div{display:flex;flex-direction:column}.fc-hd span{font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:rgba(43,35,32,.55)}
.fc-hd b{font-family:"Fredoka","Nunito",sans-serif;font-weight:600;font-size:40px;line-height:1}.fc-hd .k b{font-size:54px;color:#A45823}.fc-hd em{font-style:normal;font-size:12px;font-weight:700;color:rgba(43,35,32,.6)}.fc-hd .ar{font-size:26px;font-weight:800;color:rgba(43,35,32,.4);padding-bottom:18px}
.fc-leg{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:11px;font-weight:700;color:rgba(43,35,32,.7);margin:8px 0 2px}.fc-leg span{display:flex;align-items:center;gap:4px}
.fc-leg i{width:11px;height:11px;border-radius:2px;display:inline-block}.fc-leg i.hp{background:repeating-linear-gradient(45deg,#A45823 0 2px,#FBF6EE 2px 5px)}.fc-leg i.tg{border:1.2px dashed #6E8B57;background:rgba(110,139,87,.14);box-sizing:border-box}
.oc-ahead>summary{font-weight:800;font-size:13px;color:rgba(43,35,32,.6);cursor:pointer;margin-bottom:8px}
.pd-ind table.fc-t td:nth-child(n+2){width:auto;font-size:12px}
.fc-t{font-size:11.5px}.fc-t th{font-size:9.5px;line-height:1.15;vertical-align:bottom}.fc-t td,.fc-t th{padding-left:3px;padding-right:3px}
.pdtabs button{font-size:12.5px;padding-left:2px;padding-right:2px}
.oc-ahead{margin:6px 18px 10px;padding:12px 0 0;border-top:1px solid rgba(43,35,32,.12)}
.oc-ahead .legend{padding-left:0;padding-right:0}.oc-ahead .centre{padding-left:0;padding-right:0}
"""
js = """
  Array.prototype.slice.call(document.querySelectorAll('.toggle.fc button')).forEach(function(b){ b.addEventListener('click', function(){
    Array.prototype.slice.call(document.querySelectorAll('.toggle.fc button')).forEach(function(x){ x.setAttribute('aria-selected', x===b?'true':'false'); });
    ['fc-sm','fc-cb'].forEach(function(id){ document.getElementById(id).hidden = (id !== b.dataset.fc); }); window.scrollTo(0,0);
  }); });
  Array.prototype.slice.call(document.querySelectorAll('.ptabs button')).forEach(function(b){ b.addEventListener('click', function(){
    var sec=b.closest('section'), p=b.dataset.p;
    Array.prototype.slice.call(sec.querySelectorAll('.ptabs button')).forEach(function(x){ x.setAttribute('aria-selected', x.dataset.p===p?'true':'false'); });
    Array.prototype.slice.call(sec.querySelectorAll('[data-pane]')).forEach(function(e){ e.hidden=(e.dataset.pane!==p); });
    var s=sec.querySelector('.sub[data-'+p+']'); if(s) s.textContent=s.getAttribute('data-'+p); window.scrollTo(0,0);
  }); });
"""
