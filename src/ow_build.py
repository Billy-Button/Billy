"""Occupancy and Wages in the Pipeline pattern: Yesterday · Week · Month."""
import sys, pathlib, datetime as dt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "kpi"))
import occ as O
import pipeline_build as pl
import wages_build as wg
PLACES = {"South Morang": 108, "Craigieburn": 174}
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
def crow(label, big, sub, vals, tgt, tlab, fmtv, labels, groups=None, marks=(), n_avg=None, details=(), fname="Forecast", avgname="3-mth average", lower=False, zoom=False, ghost=0):
    use = [v for v in (vals[-n_avg:] if n_avg else vals) if v is not None]; avg = sum(use) / len(use) if use else None
    if ghost: avg = None
    line = sub(avg) if callable(sub) else sub
    ch = pl.bars(labels, vals, avg, tgt, tlab, fmtv, lower, marks, groups, avgname, fname=fname, zoom=zoom, ghost=ghost)
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
def occ_yesterday(c):
    y = pl.Y; b, a, k, h = DAY.get((c, y), (0, 0, 0, 0)); lw = odays(pl.LW); n = len(lw) or 1
    lb = tot(c, lw, 0) / n; la = tot(c, lw, 1) / n
    wk = odays(pl.WK)
    rows = (yrow("Children booked", f"{b}", f"{100*b/PLACES[c]:.0f}% of {PLACES[c]} places", pl.arrow(b, lb) if False else ('<span class="pd-ar up">▲ up</span>' if b - lb >= 2 else '<span class="pd-ar dn">▼ down</span>' if lb - b >= 2 else '<span class="pd-ar lvl">● level</span>'),
                 [("Last week:", f"{lb:.0f} booked a day on average ({len(lw)} open days, week ending {pl.fd(pl.LW[-1])})."), ("Arrow:", "the day against last week's average a day; level when within 2 children. Days of the week differ: Fridays and Mondays are lighter."), ("Measure:", OD["occ"])])
            + yrow("Children who came", f"{a}", f"{100*a/b:.0f}% of those booked" if b else "–", "", [("Last week:", f"{la:.0f} a day on average, {100*tot(c, lw, 1)/max(tot(c, lw, 0),1):.0f}% of those booked."), ("Measure:", OD["came"])])
            + yrow("Casual days", f"{k}", f"{tot(c, wk, 2)} so far this week", "", [("Last week:", f"{tot(c, lw, 2)} casual days."), ("Measure:", OD["cas"])]))
    return f'<div class="pd"><ul class="pd-l">{rows}</ul>' + pl.about(f"What happened on {pl.YLAB}, from Owna as at this morning's dashboard build.") + '</div>'
def occ_charts(c, periods, labels, groups, marks, n_avg, word):
    occ = [occ_pct(c, p) for p in periods]
    came = [100 * tot(c, odays(p), 1) / tot(c, odays(p), 0) if tot(c, odays(p), 0) else None for p in periods]
    cas = [tot(c, p, 2) for p in periods]
    st = [pl.ev(c, p, "st") for p in periods] if word == "week" else [pl.MS.get((c, m, "st"), (0, 0))[0] for m in pl.MONTHS]
    lo = [pl.ev(c, p, "lo") for p in periods] if word == "week" else [pl.MS.get((c, m, "lo"), (0, 0))[0] for m in pl.MONTHS]
    net = [a - b for a, b in zip(st, lo)]; t = OCC_T[c]
    f0 = lambda v: f"{v:.0f}"
    sgn = lambda v: f"{'+' if v > 0 else '−' if v < 0 else ''}{abs(v):g}"
    rows = (crow("Occupancy", f"{occ[-1]:.0f}<small>%</small>", lambda a: f"Forecast {a:.0f}% · Target {t}%", occ, t, f"{t}%", f0, labels, groups, marks, n_avg,
                 [("Spots:", f"{tot(c, wdays(periods[-1]), 0)} booked child-days in the {word}."), ("Measure:", OD["occ"]), ("Forecast:", "the three-month average of the bars shown."),
                  ("Target:", f"{t}% by 30 June 2027, from the forecast model."), ("Industry:", "LineLeader's benchmark reports put the level a centre needs to be sustainable at 70 to 75% occupancy (its customers, mostly US; under review)."), ("Chart:", "the scale starts above zero so the weeks can be told apart; the numbers on the bars are the percentages.")], zoom=True)
            + crow("Children who came", f"{came[-1]:.0f}<small>%</small>", lambda a: f"of those booked · average {a:.0f}%", came, None, "", f0, labels, groups, marks, n_avg,
                   [("Measure:", OD["came"]), ("Why it matters:", "booked days are charged whether or not the child comes; a low share means more absences, which is spare room on the day."), ("Chart:", "the scale starts above zero; the numbers on the bars are the percentages.")], fname="Average", zoom=True)
            + crow("Casual days", f"{cas[-1]:g}", lambda a: f"average {a:.1f} a {word}", cas, None, "", pl.fmt1, labels, groups, marks, n_avg, [("Measure:", OD["cas"])], fname="Average")
            + yrow("Net spots", sgn(net[-1]), f"started {st[-1]:g} · lost {lo[-1]:g}", "", [(f"Over the {'13 weeks' if word == 'week' else 'last three months'}:", f"{sgn(sum(net[-(n_avg or len(net)):]))} spots (started {sum(st[-(n_avg or len(st)):]):g}, lost {sum(lo[-(n_avg or len(lo)):]):g})."), ("Measure:", OD["net"])]))
    return rows
def occ_week(c):
    return (f'<div class="pd"><ul class="pd-l">{occ_charts(c, pl.WEEKS, WLABS, WGRP, WMARK, None, "week")}</ul>{pl.KEY}'
            + pl.about(f"The 13 complete weeks to {pl.WLAB}. Occupancy counts Monday to Friday. The number under each bar is the Friday the week ended. * = a week with a closed day.") + '</div>')
def occ_month(c):
    return (f'<div class="pd"><ul class="pd-l">{occ_charts(c, [month_days(m) for m in pl.MONTHS], MLABS, None, (), 3, "month")}</ul>{pl.KEY}'
            + pl.about(f"Complete months, {MLABS[0]} to {MLABS[-1]} 2026. Dashed line = the average of the last three months.") + '</div>')
# ================= Forecast tab (draft) =================
# Spots a week by month end. Owna facts as at the last Friday issue (fnr_build), by the month they fall in; school leavers with no date go at end January.
# intake = the forecast model's February intake from enquiry conversion (Financial Model, draft).
FC_AT = "Fri 6 Nov"
FC = {"South Morang": dict(now=433, intake=44, steps=[("Nov", -1, 1, 0), ("Dec", -9, 2, 0), ("Jan", -92, 2, 0), ("Feb", 0, 3, 2)], nodate=87),
      "Craigieburn": dict(now=309, intake=65, steps=[("Nov", -5, 1, 1), ("Dec", 0, 2, 8), ("Jan", -74, 0, 17), ("Feb", 0, 4, 2)], nodate=74)}
def occ_forecast(c):
    f = FC[c]; cap = PLACES[c] * 5; t = OCC_T[c]; s = f["now"]; base = []; fc = []
    for i, (m, lv, en, pe) in enumerate(f["steps"]):
        s += lv + en + pe; base.append(s); fc.append(s + (f["intake"] if m == "Feb" else 0))
    act = [occ_pct(c, month_days(m)) for m in pl.MONTHS[-3:]]; labels = pl.fmonths(); grp = ["Actual"] * 3 + ["Forecast"] * 4
    pcf = lambda v: 100 * v / cap; f0 = lambda v: f"{v:.0f}"
    ch = pl.bars(labels, act + [pcf(v) for v in fc], None, t, f"{t}%", f0, False, (), grp, zoom=True, ghost=4, refs={6: pcf(base[3])})
    sg = lambda v: "–" if not v else (f"+{v}" if v > 0 else f"−{abs(v)}")
    tr = "".join(f"<tr><td>{m}</td><td>{sg(lv)}</td><td>{sg(en)}</td><td>{sg(pe)}</td><td>{sg(f['intake']) if m == 'Feb' else '–'}</td><td><b>{fc[i]}</b></td><td><b>{pcf(fc[i]):.0f}%</b></td></tr>" for i, (m, lv, en, pe) in enumerate(f["steps"]))
    table = (f'<div class="pd-ind"><div class="pd-indh">How each month is built <span>spots a week</span></div>'
             f'<table class="fc-t"><tr><th></th><th>School leavers</th><th>Enrolled</th><th>Pending</th><th>New families</th><th>Spots</th><th>Occ.</th></tr>'
             f'<tr><td>Now</td><td></td><td></td><td></td><td></td><td><b>{f["now"]}</b></td><td><b>{pcf(f["now"]):.0f}%</b></td></tr>{tr}</table>'
             + pl.det([("Now:", f"{f['now']} spots a week booked in Owna as at {FC_AT}, of {cap} ({PLACES[c]} places × 5 days)."),
                       ("School leavers:", f"children starting school in 2027, in the month Owna says they finish. {f['nodate']} spots belong to children with no finish date in Owna; they are taken out at the end of January."),
                       ("Enrolled:", "children in Owna with a start date ahead, in the month they start."),
                       ("Pending:", "Owna forms in but not yet pulled through, in the month the family asked to start. Not all of these will start."),
                       ("New families:", f"the forecast model's February intake: families who enquire from October to December are assumed to start in February, about {f['intake']} spots at this centre. From the model, which is a draft in its final build."),
                       ("Not included:", "children who leave for other reasons, extra days, and casual days. The forecast model allows for these month by month; this table does not yet.")]) + '</div>')
    row = (f'<li class="pd-r"><div class="pd-t"><b>Occupancy at month end</b></div><div class="pd-b"><div class="pd-n">{pcf(fc[-1]):.0f}<small>% end Feb</small></div>'
           f'<div class="pd-s">Forecast · Base case {pcf(base[-1]):.0f}% · Target {t}%</div></div>{ch}'
           + pl.det([("Solid bars:", "actual occupancy for each complete month, from Owna."), ("Outlined bars:", "forecast occupancy at the end of each month, built in the table below."),
                     ("Dotted line in Feb:", f"the base case, {pcf(base[-1]):.0f}%: what Owna already holds, with no new families added."),
                     ("Target:", f"{t}% by 30 June 2027."), ("Chart:", "the scale starts above zero so the months can be told apart.")]) + '</li>')
    return (f'<div class="pd"><ul class="pd-l">{row}</ul>{table}<p class="pd-key">Solid = actual · Outlined = forecast · Dotted = base case · Green = target</p>'
            + pl.about(f"{pl.FLAB}, by month. Draft. The January fall is the school leavers; February is when new families are forecast to start. "
                       f"This view is built from Owna as at {FC_AT} plus the forecast model's February intake. The model's own month-by-month path will replace it once the model is final.") + '</div>')
def wg_forecast(c):
    f = wg.F[c]; m = wg.month_dollars(c); labels = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]; grp = ["Actual"] * 3 + ["Forecast"] * 4
    f0 = lambda v: f"{v:.0f}"; fk = lambda v: f"{v:.0f}k"
    w2r = f["w2r"][1:8]; wk = [v / 1e3 for v in f["wages"][1:8]]; ink = [v / 1e3 for v in f["inc"][1:8]]
    rows = (crow("Wage to revenue", f"{w2r[3]:.0f}<small>% Nov</small>", f"Dec {w2r[4]:.0f}% · Jan {w2r[5]:.0f}% · Feb {w2r[6]:.0f}%", w2r, None, "", f0, labels, grp, (), None,
                 [("Solid bars:", "Xero actuals: wages net of the Worker Retention Grant ÷ income."), ("Outlined bars:", "the cash flow model's wages ÷ income for each month. The model is a draft in its final build."),
                  ("November:", f"the forecast is {w2r[3]:.0f}%. On the roster so far, November is heading for about {m['w2r_h']:.0f}%; the working is on the Month tab."),
                  ("Why it moves:", "income falls in December and January with the holidays and the school leavers; wages do not fall as fast, so the share rises. It eases when new families start in February."), ("Chart:", "the scale starts above zero.")], zoom=True, ghost=4)
            + crow("Wages", f"${wk[3]:.0f}k<small> Nov</small>", f"Dec ${wk[4]:.0f}k · Jan ${wk[5]:.0f}k · Feb ${wk[6]:.0f}k", wk, None, "", fk, labels, grp, (), None,
                   [("Measure:", "wages net of the Worker Retention Grant, $000 a month. Solid = Xero; outlined = the cash flow model (draft)."), ("Chart:", "the scale starts above zero.")], zoom=True, ghost=4)
            + crow("Income", f"${ink[3]:.0f}k<small> Nov</small>", f"Dec ${ink[4]:.0f}k · Jan ${ink[5]:.0f}k · Feb ${ink[6]:.0f}k", ink, None, "", fk, labels, grp, (), None,
                   [("Measure:", "centre income, $000 a month. Solid = Xero; outlined = the cash flow model (draft)."), ("Chart:", "the scale starts above zero.")], zoom=True, ghost=4))
    return (f'<div class="pd"><ul class="pd-l">{rows}</ul><p class="pd-key">Solid = actual · Outlined = forecast (draft)</p>'
            + pl.about("November to February, by month, from the cash flow model. Draft: the model is in its final build and these figures will be refreshed from the final version. "
                       "How the roster is set to meet these months is a question for Robyn.") + '</div>')
def occ_section(logo, back, sm_ahead, cb_ahead, legend, foot, week_label):
    def centre(c, ahead):
        return (f'<div data-pane="d" hidden>{occ_yesterday(c)}</div><div data-pane="w">{occ_week(c)}</div><div data-pane="m" hidden>{occ_month(c)}</div><div data-pane="f" hidden>{occ_forecast(c)}</div>'
                f'<div class="oc-ahead"><div class="pd-indh">Looking ahead: base case to end Feb 27</div><p class="pd-key" style="text-align:left;margin:0 0 6px">As at {week_label}. Occupancy now, less school leavers, plus enrolled and pending.</p><div class="legend">{legend}</div>{ahead}</div>')
    return f'''
<section id="report" class="scr" hidden>
  <header class="topbar">{back}
    <div class="ttl"><h1>Occupancy</h1><div class="sub" data-d="Yesterday · {pl.YLAB}" data-w="Week ending {pl.WLAB}" data-m="Month ending {pl.MLAB}" data-f="Forecast · {pl.FLAB} · draft">Week ending {pl.WLAB}</div></div>
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
PTABS = '''
  <nav class="pdtabs ptabs" role="tablist" aria-label="Period">
    <button type="button" role="tab" aria-selected="false" data-p="d">Yesterday</button>
    <button type="button" role="tab" aria-selected="true" data-p="w">Week</button>
    <button type="button" role="tab" aria-selected="false" data-p="m">Month</button>
    <button type="button" role="tab" aria-selected="false" data-p="f">Forecast</button>
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
    f2 = lambda v: f"{v:.2f}"; f0 = lambda v: f"{v:.0f}"
    rows = (crow("Rostered hours a day", f"{hrs[-1]:.0f}", lambda a: f"13-week average {a:.0f}", hrs, None, "", f0, WLABS, WGRP, WMARK, None, [("Measure:", WD["hrs"] + " Average over the open days in each week. The chart's scale starts above zero.")], fname="Average", avgname="13-week average", zoom=True)
            + crow("Hours per booked child", f"{hpc[-1]:.2f}", lambda a: f"13-week average {a:.2f}", hpc, None, "", f2, WLABS, WGRP, WMARK, None,
                   [("Measure:", WD["hpc"]), ("Reading it:", "a rising bar means more staff time for each booked child. It can come from extra hours or from a younger mix of children; this chart cannot tell which. The chart's scale starts above zero.")], fname="Average", avgname="13-week average", zoom=True))
    return (f'<div class="pd"><ul class="pd-l">{rows}</ul><p class="pd-key">Dashed = 13-week average · ▲ = off the scale · * = closed day</p>'
            + pl.about(f"The 13 complete weeks to {pl.WLAB}. These are averages for reference, not forecasts: the wages forecast is on the Month tab.") + '</div>')
def wages_section(logo, back):
    def centre(c):
        p = wg.panel(c, parts=True)
        return (f'<div data-pane="d" hidden>{wg_yesterday(c, p)}</div><div data-pane="w">{wg_week(c)}</div>'
                f'<div data-pane="m" hidden><div class="centre"><ul class="measures kpl"><li class="kp wg-main">{p["tm"]}{p["w2r"]}{p["ew"]}{p["age"]}{p["rooms"]}</li></ul></div></div><div data-pane="f" hidden>{wg_forecast(c)}</div>')
    foot = wg.section(logo); foot = foot[foot.index('<details class="foot">'):foot.index('</section>')]
    return f'''
<section id="wages" class="scr" hidden>
  <header class="topbar">{back}
    <div class="ttl"><h1>Wages</h1><div class="sub" data-d="Yesterday · {pl.YLAB}" data-w="Week ending {pl.WLAB}" data-m="November so far · forecast is a draft" data-f="Forecast · {pl.FLAB} · draft">Week ending {pl.WLAB}</div></div>
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
.fc-t{font-size:11.5px}.fc-t th{font-size:9.5px;line-height:1.15;vertical-align:bottom}.fc-t td,.fc-t th{padding-left:3px;padding-right:3px}
.pdtabs button{font-size:12.5px;padding-left:2px;padding-right:2px}
.oc-ahead{margin:6px 18px 10px;padding:12px 0 0;border-top:1px solid rgba(43,35,32,.12)}
.oc-ahead .legend{padding-left:0;padding-right:0}.oc-ahead .centre{padding-left:0;padding-right:0}
"""
js = """
  Array.prototype.slice.call(document.querySelectorAll('.ptabs button')).forEach(function(b){ b.addEventListener('click', function(){
    var sec=b.closest('section'), p=b.dataset.p;
    Array.prototype.slice.call(sec.querySelectorAll('.ptabs button')).forEach(function(x){ x.setAttribute('aria-selected', x.dataset.p===p?'true':'false'); });
    Array.prototype.slice.call(sec.querySelectorAll('[data-pane]')).forEach(function(e){ e.hidden=(e.dataset.pane!==p); });
    var s=sec.querySelector('.sub[data-'+p+']'); if(s) s.textContent=s.getAttribute('data-'+p); window.scrollTo(0,0);
  }); });
"""
