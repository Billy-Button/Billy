# KPIs & Trends — Billy screen (mock-up 11 Nov 26). Monthly, per centre. Sources: dashboard snapshot 11 Nov 26 03:08; Xero (read-only) for wage to revenue.
import math
SAGE="#6E8B57"; AMBER="#E39B2D"; EARTH="#A45823"; INK="#1A1A1A"; SKY="#5E80A0"
M12=["2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09","2026-10","2026-11"]
NOW="2026-11"; ASOF="10 Nov"; PF=10/30
LET={"01":"J","02":"F","03":"M","04":"A","05":"M","06":"J","07":"J","08":"A","09":"S","10":"O","11":"N","12":"D"}

def ser(d): return [d.get(m) for m in M12]
def roll3(d):
    out={}
    for i,m in enumerate(M12):
        w=[d.get(x) for x in M12[max(0,i-2):i+1]]
        if None in w or len(w)<3: continue
        out[m]=round(sum(w)/3,1)
    return out

# ---------- data ----------
D={
 "South Morang":dict(
  enq={"2026-03":23,"2026-04":26,"2026-05":13,"2026-06":23,"2026-07":11,"2026-08":12,"2026-09":29,"2026-10":15,"2026-11":5}, enq_t=31, enq_f=19,
  ttfc={"2026-03":5640,"2026-04":13523,"2026-05":3881,"2026-06":6871,"2026-07":11269,"2026-08":2207,"2026-09":6232,"2026-10":744,"2026-11":152},
  ttfc_c=("5 of 7 contacted",),
  t2p={"2026-03":3,"2026-04":9.5,"2026-05":6,"2026-06":17,"2026-07":53,"2026-08":21,"2026-09":22,"2026-11":36},
  p2e={"2026-03":1.5,"2026-04":16.5,"2026-05":6,"2026-06":1,"2026-07":2,"2026-08":0,"2026-09":14,"2026-10":10,"2026-11":0},
  lost={"2025-11":3,"2025-12":14,"2026-01":23,"2026-02":27,"2026-03":10,"2026-04":15,"2026-05":19,"2026-06":13,"2026-07":15,"2026-08":22,"2026-09":10,"2026-10":10,"2026-11":10}, lost_t=9, lost_f=14,
  occ={"2025-11":87.7,"2025-12":85.7,"2026-01":82.5,"2026-02":75.0,"2026-03":74.5,"2026-04":76.8,"2026-05":73.6,"2026-06":76.7,"2026-07":77.5,"2026-08":76.5,"2026-09":78.8,"2026-10":79.3,"2026-11":79.6}, occ_t=85, occ_f=78,
  w2r={"2025-11":53.0,"2025-12":54.8,"2026-01":50.6,"2026-02":59.5,"2026-03":59.8,"2026-04":55.9,"2026-05":58.1,"2026-06":50.0,"2026-07":70.2,"2026-08":58.0,"2026-09":60.7,"2026-10":54.8,"2026-11":57.9}, w2r_avg=(57.1,"12 months to Oct 26"),
  sick={"2025-11":6.6,"2025-12":2.2,"2026-01":4.0,"2026-02":3.5,"2026-03":4.1,"2026-04":3.9,"2026-05":7.8,"2026-06":4.3,"2026-07":3.3,"2026-08":2.4,"2026-09":4.0,"2026-10":1.2,"2026-11":0.6},
  lwop={"2025-11":0.2,"2025-12":3.1,"2026-01":2.0,"2026-02":2.4,"2026-03":3.6,"2026-04":1.6,"2026-05":1.3,"2026-06":0.2,"2026-07":0.2,"2026-08":0.2,"2026-09":1.3,"2026-10":0.9,"2026-11":1.9},
 ),
 "Craigieburn":dict(
  enq={"2026-03":29,"2026-04":16,"2026-05":16,"2026-06":37,"2026-07":16,"2026-08":22,"2026-09":48,"2026-10":31,"2026-11":6}, enq_t=150, enq_f=33,
  ttfc={"2026-03":8316,"2026-04":5311,"2026-05":4238,"2026-06":4374,"2026-07":7365,"2026-08":4885,"2026-09":3784,"2026-10":2870,"2026-11":0.3},
  ttfc_c=("3 of 7 contacted",),
  t2p={"2026-02":5,"2026-03":6,"2026-04":6.5,"2026-05":4,"2026-06":10,"2026-07":5.5,"2026-08":9,"2026-09":5.5,"2026-10":15,"2026-11":16},
  p2e={"2026-02":2.5,"2026-03":8,"2026-04":56,"2026-05":10,"2026-06":9,"2026-07":9,"2026-08":5,"2026-09":5.5,"2026-10":6.5,"2026-11":12},
  lost={"2026-02":2,"2026-03":13,"2026-04":10,"2026-05":7,"2026-06":16,"2026-07":22,"2026-08":29,"2026-09":12,"2026-10":11,"2026-11":6}, lost_t=9, lost_f=17,
  occ={"2026-02":10.8,"2026-03":23.6,"2026-04":28.4,"2026-05":29.8,"2026-06":30.9,"2026-07":33.3,"2026-08":33.4,"2026-09":33.6,"2026-10":34.6,"2026-11":35.3}, occ_t=70, occ_f=34,
  w2r={"2026-03":69.9,"2026-04":77.5,"2026-05":62.4,"2026-06":72.2,"2026-07":68.3,"2026-08":86.9,"2026-09":67.7,"2026-10":70.8,"2026-11":68.5}, w2r_avg=(71.8,"Mar–Oct 26, since opening"),
  sick={"2026-03":1.4,"2026-04":0.9,"2026-05":1.0,"2026-06":3.4,"2026-07":4.7,"2026-08":3.6,"2026-09":2.9,"2026-10":5.2,"2026-11":2.6},
  lwop={"2026-02":4.5,"2026-03":3.6,"2026-04":8.0,"2026-05":4.9,"2026-06":2.9,"2026-07":5.5,"2026-08":5.5,"2026-09":7.8,"2026-10":11.0,"2026-11":6.0},
 ),
}

def fmt_min(m):
    if m < 1: return "&lt;1<small>min</small>"
    if m < 60: return f"{m:.0f}<small>min</small>"
    if m < 1440: return f"{m/60:.1f}<small>hrs</small>"
    return f"{m/1440:.1f}<small>days</small>"
def fmt_min_plain(m):
    return fmt_min(m).replace("<small>"," ").replace("</small>","")

# ---------- chart ----------
FC="#B07A3C"
def nice_ticks(lo,hi,n=3):
    span=hi-lo; raw=span/n; mag=10**math.floor(math.log10(raw)); step=min([1,2,2.5,5,10],key=lambda k:abs(k*mag-raw))*mag
    t=math.ceil(lo/step)*step; out=[]
    while t<=hi+1e-9: out.append(round(t,6)); t+=step
    return out
def chart(vals, colf, target=None, tlabel="", lo=0, hi=None, log=False, bands=None, ticks=None, fcst=None, flabel="", unit="", vfmt=None, act=None, under=False, pscale=1, tprefix="Target"):
    W,H,L,R,T,B=340,110,34,74,10,16
    if under: H,B=124,30
    vv=[v for v in vals if v is not None]
    if hi is None: hi=max(vv+[x for x in (target,fcst) if x is not None])*1.15 or 1
    tf=(lambda v: math.log10(max(v,0.5))) if log else (lambda v: v)
    a,b=tf(lo),tf(hi)
    xs=lambda i: L+(W-L-R)*i/(len(vals)-1); ys=lambda v: T+(H-T-B)*(1-(min(max(tf(v),a),b)-a)/(b-a))
    vfmt=vfmt or (lambda v: f"{v:g}{unit}")
    g=""
    if bands:
        for (y0,y1,c) in bands:
            g+=f'<rect x="{L}" y="{ys(y1):.1f}" width="{W-L-R}" height="{ys(y0)-ys(y1):.1f}" fill="{c}" opacity=".10"/>'
    if ticks is None: ticks=[(t,f"{t:g}{unit}") for t in nice_ticks(lo,hi)]
    for (tv,tl) in ticks:
        g+=f'<line x1="{L}" y1="{ys(tv):.1f}" x2="{W-R}" y2="{ys(tv):.1f}" stroke="{INK}" opacity=".07"/>'
        g+=f'<text x="{L-4}" y="{ys(tv)+3:.1f}" text-anchor="end" font-size="8.5" fill="{INK}" opacity=".45">{tl}</text>'
    lab=[]
    if fcst is not None:
        g+=f'<line x1="{L}" y1="{ys(fcst):.1f}" x2="{W-R}" y2="{ys(fcst):.1f}" stroke="{FC}" stroke-width="1.4" stroke-dasharray="1.5 3" stroke-linecap="round"/>'
        lab.append([ys(fcst),f"Forecast {flabel}",FC])
    if target is not None:
        g+=f'<line x1="{L}" y1="{ys(target):.1f}" x2="{W-R}" y2="{ys(target):.1f}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="5 3" opacity=".7"/>'
        lab.append([ys(target),f"{tprefix} {tlabel}",INK])
    if act is not None:
        g+=f'<line x1="{L}" y1="{ys(act):.1f}" x2="{W-R}" y2="{ys(act):.1f}" stroke="{EARTH}" stroke-width="1.2" stroke-dasharray="5 3" opacity=".8"/>'
        lab.append([ys(act),f"Act {act:g}%",EARTH])
    if len(lab)==2 and abs(lab[0][0]-lab[1][0])<11:
        lo_i=0 if lab[0][0]>lab[1][0] else 1; lab[lo_i][0]+=6; lab[1-lo_i][0]-=6
    for (y,t,c) in lab:
        g+=f'<text x="{W-R+4}" y="{y+3:.1f}" font-size="9" font-weight="800" fill="{c}">{t}</text>'
    NI=M12.index(NOW); cf=lambda i,v: colf(v/pscale) if i==NI else colf(v)
    pi=None
    for i,v in enumerate(vals):
        if v is not None and pi is not None:
            dash=' stroke-dasharray="3 4"' if i==NI else ''
            g+=f'<line x1="{xs(pi):.1f}" y1="{ys(vals[pi]):.1f}" x2="{xs(i):.1f}" y2="{ys(v):.1f}" stroke="{cf(i,v)}" stroke-width="2.5" stroke-linecap="round"{dash}/>'
        if v is not None: pi=i
    last=max([i for i,v in enumerate(vals) if v is not None])
    for i,v in enumerate(vals):
        if v is not None:
            if i==NI: g+=f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="4" fill="#FBF6EE" stroke="{cf(i,v)}" stroke-width="2.2"/>'
            else: g+=f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="{4.2 if i==last else 3.2}" fill="{colf(v)}"/>'
        g+=f'<text x="{xs(i):.1f}" y="{H-3-(14 if under else 0)}" text-anchor="middle" font-size="9" fill="{INK}" opacity=".45">{LET[M12[i][5:]]}</text>'
        if under and v is None and i==M12.index(NOW):
            g+=f'<text x="{xs(i):.1f}" y="{H-3}" text-anchor="middle" font-size="8" font-weight="700" fill="{INK}" opacity=".4">close</text>'
        if under and v is not None:
            g+=f'<text x="{xs(i):.1f}" y="{H-3}" text-anchor="middle" font-size="8.5" font-weight="800" fill="{cf(i,v)}">{"~" if i==NI else ""}{v:.0f}</text>'
    if under: return f'<svg class="kp-ch" viewBox="0 0 {W} {H}">{g}</svg>'
    v=vals[last]; pv=[x for x in vals[:last] if x is not None]; up=(not pv) or tf(pv[-1])<=tf(v)
    ly=(ys(v)-8 if ys(v)>T+12 else ys(v)+15) if up else (ys(v)+15 if ys(v)<H-B-14 else ys(v)-8)
    g+=f'<text x="{xs(last)-5:.1f}" y="{ly:.1f}" text-anchor="end" font-size="9.5" font-weight="800" fill="{cf(last,v)}" stroke="#FBF6EE" stroke-width="3" paint-order="stroke">{vfmt(v)}</text>'
    return f'<svg class="kp-ch" viewBox="0 0 {W} {H}">{g}</svg>'

def latest(d):
    ks=[m for m in M12 if d.get(m) is not None]
    return (ks[-1], d[ks[-1]]) if ks else (None,None)
def mon(m):
    return ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][int(m[5:])]

SUBS = []
def row(label, sub, big, small, ch, col=INK, grey=False):
    cls=' kp-grey' if grey else ''
    if not grey and (label, sub) not in SUBS: SUBS.append((label, sub))
    return (f'<li class="kp{cls}"><div class="kp-h"><div class="kp-l"><b>{label}</b>{f"<span>{sub}</span>" if grey else ""}</div>'
            f'<div class="kp-v"><b style="color:{col}">{big}</b><span>{small}</span></div></div>{ch}</li>')

def panel(c):
    d=D[c]; out=[]
    neutral=lambda v: SKY
    P=lambda m: f"Nov to {ASOF}" if m==NOW else (f"{mon(m)} 26" if m>="2026" else f"{mon(m)} 25")
    PL=lambda m: P(m) if m==NOW else P(m)+" month"
    # 1 Enquiries
    m,v=latest(d["enq"])
    ec=lambda x: SAGE if x>=d["enq_t"] else (AMBER if x>=d["enq_f"] else EARTH)
    pf=PF if m==NOW else 1
    out.append(row("New enquiries","LineLeader · families a month", f"{v}", PL(m) + (f" · on pace {v/pf:.0f}" if m==NOW else ""),
                   chart(ser(d["enq"]), ec, d["enq_t"], f"{d['enq_t']}", fcst=d["enq_f"], flabel=f"{d['enq_f']}", hi=max(d['enq_t'],max(d['enq'].values()))*1.12, pscale=PF), ec(v/pf)))
    # 2 Time to first contact
    m,v=latest(d["ttfc"])
    tc=lambda x: SAGE if x<=10 else (AMBER if x<=60 else EARTH)
    out.append(row("Time to first contact","median · first human contact", fmt_min(v), f"{PL(m)} · {d['ttfc_c'][0]}",
                   chart(ser(d["ttfc"]), tc, 10, "10 min", lo=3, hi=20160, log=True, ticks=((60,"1 hr"),(1440,"1 day"),(10080,"1 wk")), vfmt=fmt_min_plain), tc(v)))
    # 3 Tour -> Pending
    m,v=latest(d["t2p"])
    sc=lambda x: SAGE if x<=2 else (AMBER if x<=7 else EARTH)
    out.append(row("Tour → Pending","median days · Owna form in", f"{v:g}<small>days</small>", PL(m),
                   chart(ser(d["t2p"]), sc, 2, "2 b.days", hi=60 if max(d['t2p'].values())>30 else 30, vfmt=lambda x:f"{x:g} d"), sc(v)))
    # 4 Pending -> Enrolment complete
    m,v=latest(d["p2e"])
    pc=lambda x: SAGE if x<=7 else (AMBER if x<=14 else EARTH)
    out.append(row("Pending → Enrolment complete","median days · pulled into Owna", f"{v:g}<small>days</small>", PL(m),
                   chart(ser(d["p2e"]), pc, 7, "5 b.days", hi=60 if max(d['p2e'].values())>30 else 30, vfmt=lambda x:f"{x:g} d"), pc(v)))
    # 5 Lost spots, monthly
    r=d["lost"]; m,v=latest(r); LP=8/21; pf=LP if m==NOW else 1
    lc=lambda x: SAGE if x<=d["lost_t"] else (AMBER if x<=d["lost_t"]*1.3 else EARTH)
    out.append(row("Lost spots","spots a month", f"{v:.0f}", PL(m) + (" · 8 of 21 days" if m==NOW else ""),
                   chart(ser(r), lc, d["lost_t"], f"{d['lost_t']}", fcst=d["lost_f"], flabel=f"{d['lost_f']}", lo=0, hi=5*math.ceil(max(r.values())*1.1/5), vfmt=lambda x:f"{x:.0f}", pscale=LP), lc(v/pf)))
    # 6 Occupancy
    m,v=latest(d["occ"])
    oc=lambda x: SAGE if x>=d["occ_t"] else (AMBER if x>=d["occ_f"] else EARTH)
    out.append(row("Occupancy","average for the month · incl. casual", f"{v:.0f}%", PL(m),
                   chart(ser(d["occ"]), oc, d["occ_t"], f"{d['occ_t']}%", fcst=d["occ_f"], flabel=f"{d['occ_f']}%", lo=(60 if min(d['occ'].values())>60 else 0), hi=100, unit="%", vfmt=lambda x:f"{x:.0f}%"), oc(v)))
    # 7 Wage to revenue: 12-month average up front, monthly line
    m,v=latest(d["w2r"]); av,per=d["w2r_avg"]
    wc=lambda x: SAGE if x<55 else (AMBER if x<=60 else EARTH)
    out.append(row("Wage to revenue","Xero · net of grant · % · Nov ~ proxy", f"{av:.0f}%", f"avg · {per}",
                   chart(ser(d["w2r"]), wc, 55, "55%", lo=40, hi=90, unit="%", bands=[(40,55,SAGE),(55,60,AMBER),(60,90,EARTH)], ticks=[(50,"50%"),(70,"70%"),(80,"80%")], act=60, under=True), wc(av)))
    # 8 Sick days
    m,v=latest(d["sick"])
    out.append(row("Sick days","personal and carer's leave · % of rostered days", f"{v:g}%", PL(m),
                   chart(ser(d["sick"]), neutral, hi=max(d["sick"].values())*1.25, unit="%")))
    # 9 LWOP
    m,v=latest(d["lwop"])
    out.append(row("Leave without pay","% of rostered days", f"{v:g}%", PL(m),
                   chart(ser(d["lwop"]), neutral, hi=max(d["lwop"].values())*1.25, unit="%")))
    coming=[]
    for lab,sub,txt in (("Opening checklist","% of open days completed in Owna","Dima to bring the Owna checklist into the dashboard"),
                        ("Closing checklist","% of open days completed in Owna","Dima to bring the Owna checklist into the dashboard"),
                        ("Signed in and out","% of child attendances and staff shifts missing a sign-in or sign-out","Waiting on sign-in records from Owna; repeat cases flagged by code"),
                        ("Fixed wages","management, admin and kitchen · $ a month","Waiting on fixed roles coded in Owna and Xero")):
        coming.append(row(lab,sub,"—","not yet in the dashboard",f'<div class="kp-none">{txt}</div>', grey=True))
    out.append(f'<li class="kp"><details class="kp-coming"><summary>Coming next ({len(coming)})</summary><ul class="measures kpl">{"".join(coming)}</ul></details></li>')
    return "".join(out)

def section(logo):
    return f'''
<section id="kpis" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>KPIs &amp; Trends</h1><div class="sub">Rolling 12 months · Dec 25 to Nov 26</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <nav class="toggle kp" role="tablist" aria-label="Centre">
    <button type="button" role="tab" aria-selected="true" data-kp="kp-sm">South Morang</button>
    <button type="button" role="tab" aria-selected="false" data-kp="kp-cb">Craigieburn</button>
  </nav>
  <div class="screens">
    <div id="kp-sm" class="screen"><div class="centre"><ul class="measures kpl">{panel("South Morang")}</ul></div></div>
    <div id="kp-cb" class="screen" hidden><div class="centre"><ul class="measures kpl">{panel("Craigieburn")}</ul></div></div>
  </div>
  <details class="foot"><summary>About this screen</summary>
    <p><b>What each row counts.</b> {" · ".join(f"{a}: {b}" for a, b in SUBS)}.</p>
    <p>Each dot is a month. The hollow dot at the end is November so far (dashboard build of 11 Nov 26, so to 10 Nov); it moves with each overnight build. For counts (enquiries, lost spots) its colour is judged on pace: enquiries against the target for 10 of 30 days, lost spots for 8 of 21 open days. The big figure is November so far, except wage to revenue (average of the period shown, as November isn't closed in Xero yet). Two reference lines: <b>Target</b>, dark dashes, is where we are aiming; <b>Forecast</b>, brown dots, is where the current run rate takes us. Colours: sage at or better than target, amber between forecast and target (or close to target where there is no forecast), earth worse. Blue where no target is set yet. Time measures have targets only, no forecast yet.</p>
    <p><b>New enquiries</b>: LineLeader enquiries by month on the dashboard's rules (metric enquiries_month). February is the LineLeader import and is left out. Target is the model's Target chain (South Morang 31 a month, Craigieburn 150); forecast is the 13-week average run rate (4.3 and 7.7 a week) × 4.33.</p>
    <p><b>Time to first contact</b>: median minutes from the enquiry to the first human contact — never LineLeader's automatic reply (view first_contact). Log scale from minutes to two weeks; target 10 minutes. Only contacted families are in the median; the line under the figure says how many of the month's enquiries were contacted.</p>
    <p><b>Tour → Pending</b> and <b>Pending → Enrolment complete</b>: the dashboard's pipeline steps, median days by the month the step was completed (view pipeline_step_month). Targets: Owna form in 2 business days after the tour; pulled into Owna 5 business days after the form. Months with one family are left out.</p>
    <p><b>Lost spots</b>: children who left plus fewer days, school graduations apart (metric spot_movement_month), each month; November is the month so far against the end of October. Target 9 a month (2.1 a week, from the model). Forecast is the three-month rule on this same monthly count: the average of Aug to Oct 26 (South Morang 14, Craigieburn 17). The Pipeline screen's weekly forecast (2.4 and 3.8 a week) is not used here: a month's lost spots compare the month's closing week with the month before, so they don't add up from the weekly figures. Colours: sage at or under target, amber within 30% of it, earth beyond.</p>
    <p><b>Occupancy</b>: average spots for the month over capacity, casual included (spot_movement_month). Target is occupancy at 30 Jun 27 (South Morang 85%, Craigieburn 70%); forecast is the base case for end Feb 27 (78% and 34%), as on the Occupancy screen.</p>
    <p><b>Wage to revenue</b>: from Xero. (HR trust recharge + agency staff − all Worker Retention Grant received) ÷ (trading income less the grant). The line is each month; the big figure is the average for the period shown, weighted by revenue: 12 months to Oct 26 at South Morang; Mar to Oct 26 at Craigieburn (February, the opening month, was 155% on almost no revenue and is left out). This is the Advisory Panel's September 2026 method, applied to every month. November (hollow, marked ~) is the estimate from the Wages screen: November's daily rostered hours so far, run forward to month end and costed at October's wages per rostered hour, over the forecast's November income. A working estimate only; Xero replaces it when November closes. It is not in the average. Last three months: South Morang 58%, Craigieburn 75%. No forecast line until the model forecasts wages. Warn 55%, act 60% (decision D-17).</p>
    <p><b>Sick days</b> and <b>leave without pay</b>: staff-days of personal/carer's leave, and of leave without pay, from the Owna roster's leave entries, as a share of rostered staff-days in the month.</p>
    <p><b>Opening and closing checklists</b>: done on the iPad in Owna each morning and night; not yet in the dashboard.</p>
  </details>
</section>'''

kp_js = """
  var kpTabs = Array.prototype.slice.call(document.querySelectorAll('.toggle.kp button'));
  kpTabs.forEach(function(t){ t.addEventListener('click', function(){
    kpTabs.forEach(function(x){ x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
    ['kp-sm','kp-cb'].forEach(function(id){ document.getElementById(id).hidden = (id !== t.dataset.kp); });
  }); });
"""

kp_css = """
.measures.kpl .kp { padding:14px 0 8px; border-bottom:1px solid rgba(43,35,32,.08); }
.kp-h { display:flex; justify-content:space-between; align-items:flex-end; gap:10px; }
.kp-l b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; line-height:1.15; } .kp-l span { font-size:11px; color:var(--ink-70); font-weight:700; }
.kp-v { text-align:right; flex:0 0 auto; } .kp-v b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:26px; line-height:1; } .kp-v b small { font-size:13px; margin-left:3px; } .kp-v span { font-size:10.5px; color:var(--ink-50); font-weight:700; white-space:nowrap; }
.kp-ch { width:100%; height:auto; display:block; margin-top:4px; font-family:"Nunito",sans-serif; }
.kp-grey { opacity:.45; } .kp-none { font-size:11.5px; color:var(--ink-50); font-weight:700; padding:12px 0 6px; }
"""
