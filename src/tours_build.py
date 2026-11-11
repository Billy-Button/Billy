# Tours — Billy's third screen, v2 (11 Nov 26): centre by centre, 12 months, trend line, missing data, tour givers.
# Every figure from the dashboard's certified views tour_giver / tour_giver_month and metric tour_no_show_families (snapshot 11 Nov 26 03:08).
SAGE="#6E8B57"; AMBER="#E39B2D"; EARTH="#A45823"; INK="#1A1A1A"
ASOF="12 months to 11 Nov"; IND=40; TOP=80

NAMES={"S-RK2L":"Pallavi","S-RPV4":"Robyn","S-HBWH":"Fiona","S-IOVK":"Ebony","S-RN6J":"Angelique",
       "S-GWZO":"Amy","S-P2CN":"Georgia","S-L2B7":"Yamamah","S-VGYF":"Rachel","S-JZA4":"Shirley",None:"Not named"}

# monthly: (month, families toured, enrolled since)  — status runs excluded
MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov"]
MONTHLY={
 "South Morang":[(1,0),(10,2),(37,5),(24,3),(10,3),(12,6),(4,0),(15,3),(10,1),(10,1),(4,0)],
 "Craigieburn":[(0,0),(25,17),(14,9),(20,5),(5,1),(21,8),(14,5),(16,3),(21,9),(18,4),(5,0)],
}
SR={
 "South Morang":[(0,0),(1,1),(4,3),(5,5),(2,1),(3,1),(1,1),(7,6),(5,3),(6,2),(0,0)],
 "Craigieburn":[(0,0),(26,24),(22,19),(5,2),(6,4),(5,5),(2,2),(7,6),(7,3),(11,8),(0,0)],
}
ALL={c:[(a[0]+b[0],a[1]+b[1]) for a,b in zip(MONTHLY[c],SR[c])] for c in MONTHLY}
# headline, 12 months (metric tour_givers_12_months, centre total)
HEAD={"South Morang":(167,57),"Craigieburn":(238,130)}   # every Tour Completed, back-filled included
HEAD_REC={"South Morang":(133,24),"Craigieburn":(153,61)}
# missing data: (label, sub, this quarter Sep–Nov, last quarter Jun–Aug, year)  each as (n, of) or None
MISSING={
 "South Morang":[
  ("Tour giver recorded","of tours",(24,24),(31,35),(83,142)),
  ("Tour logged at the time","of Tour Completed",(24,35),(35,46),(142,176)),
  ("Tour outcome recorded","of booked tours now past",(36,40),(44,47),(169,183))],
 "Craigieburn":[
  ("Tour giver recorded","of tours",(46,49),(45,58),(131,176)),
  ("Tour logged at the time","of Tour Completed",(49,67),(58,72),(176,261)),
  ("Tour outcome recorded","of booked tours now past",(59,63),(62,67),(234,286))],
}
RK={
 "South Morang":{
  "Tour recorded on the day":("of families marked Tour Completed",[(1,1),(10,11),(37,41),(24,29),(10,12),(12,15),(4,5),(15,22),(10,15),(10,16),(4,4)])},
 "Craigieburn":{
  "Tour recorded on the day":("of families marked Tour Completed",[(0,0),(25,51),(14,36),(20,25),(5,11),(21,26),(14,16),(16,23),(21,28),(18,29),(5,5)])},
}
OFFER2={
 "South Morang":[(0,1),(0,10),(6,37),(2,25),(3,10),(4,14),(0,4),(6,17),(4,10),(3,10),(2,4)],
 "Craigieburn":[(0,0),(3,28),(1,14),(2,21),(4,6),(0,24),(7,16),(9,18),(11,25),(10,19),(1,5)],
}
OFFER_AT={   # Offered (or further) within an hour of Tour Completed, tours recorded on the day: (tours, offered at the tour) Jan..Nov
 "South Morang":[(1,0),(10,0),(37,2),(25,2),(10,2),(14,3),(4,0),(17,6),(10,4),(10,3),(4,2)],
 "Craigieburn":[(0,0),(28,2),(14,1),(21,2),(6,2),(24,0),(16,5),(18,7),(25,5),(19,9),(5,1)],
}
AT_TOUR={("South Morang","S-HBWH"):3,("South Morang","S-RPV4"):6,("South Morang","S-VGYF"):3,("South Morang","S-IOVK"):3,
 ("South Morang","S-RN6J"):3,("South Morang","S-L2B7"):4,("Craigieburn","S-GWZO"):7,("Craigieburn","S-HBWH"):10,
 ("Craigieburn","S-RK2L"):7,("Craigieburn","S-RPV4"):7,("Craigieburn","S-P2CN"):3}
OA_LO, OA_HI, OA_TARGET = 70, 90, 100
def oacol(v): return SAGE if v>=OA_HI else (AMBER if v>=OA_LO else EARTH)
def chart_oa(m):
    pts=[]
    for i in range(1,len(m)):
        f=sum(x[0] for x in m[max(0,i-2):i+1]); e=sum(x[1] for x in m[max(0,i-2):i+1])
        pts.append((MONTHS[i], pct(e,f) if f else 0))
    W,H,L,R,T,B=330,150,62,10,12,26
    xs=lambda i: L+(W-L-R)*i/(len(pts)-1); ys=lambda v: T+(H-T-B)*(1-v/100)
    g=f'<rect x="{L}" y="{ys(100)}" width="{W-L-R}" height="{ys(OA_HI)-ys(100)}" fill="{SAGE}" opacity=".10"/>'
    g+=f'<rect x="{L}" y="{ys(OA_HI)}" width="{W-L-R}" height="{ys(OA_LO)-ys(OA_HI)}" fill="{AMBER}" opacity=".12"/>'
    g+=f'<rect x="{L}" y="{ys(OA_LO)}" width="{W-L-R}" height="{ys(0)-ys(OA_LO)}" fill="{EARTH}" opacity=".08"/>'
    g+=f'<line x1="{L}" y1="{ys(OA_TARGET)}" x2="{W-R}" y2="{ys(OA_TARGET)}" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3" opacity=".5"/>'
    g+=f'<text x="{L-5}" y="{ys(OA_TARGET)+3}" text-anchor="end" font-size="9.5" font-weight="700" fill="{INK}" opacity=".75">100%</text>'
    g+=f'<text x="{L-5}" y="{ys(OA_TARGET)+14}" text-anchor="end" font-size="8.5" fill="{INK}" opacity=".6">target</text>'
    g+=f'<text x="{L-5}" y="{ys(50)+3.5}" text-anchor="end" font-size="9.5" fill="{INK}" opacity=".6">50%</text>'
    for i in range(1,len(pts)):
        g+=f'<line x1="{xs(i-1):.1f}" y1="{ys(pts[i-1][1]):.1f}" x2="{xs(i):.1f}" y2="{ys(pts[i][1]):.1f}" stroke="{oacol(pts[i][1])}" stroke-width="3" stroke-linecap="round"/>'
    for i,(lab,v) in enumerate(pts):
        g+=f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="5" fill="{oacol(v)}"/>'
        g+=f'<text x="{xs(i):.1f}" y="{H-8}" text-anchor="middle" font-size="10" fill="{INK}" opacity=".7">{lab[0]}</text>'
    return f'<svg class="tr-trend" viewBox="0 0 {W} {H}">{g}</svg>'
RK_TARGET=90
def rkcol(v): return SAGE if v>=RK_TARGET else (AMBER if v>=70 else EARTH)
def spark(series):
    pts=[]
    for i in range(1,len(series)):
        n=sum(x[0] for x in series[max(0,i-2):i+1]); o=sum(x[1] for x in series[max(0,i-2):i+1])
        pts.append((MONTHS[i], pct(n,o) if o else None))
    W,H,L,R,T,B=330,74,30,10,8,18
    xs=lambda i: L+(W-L-R)*i/(len(pts)-1); ys=lambda v: T+(H-T-B)*(1-v/100)
    g=f'<line x1="{L}" y1="{ys(RK_TARGET)}" x2="{W-R}" y2="{ys(RK_TARGET)}" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3" opacity=".5"/>'
    g+=f'<text x="{L-4}" y="{ys(RK_TARGET)+3.5}" text-anchor="end" font-size="9.5" fill="{INK}" opacity=".7">{RK_TARGET}%</text>'
    g+=f'<text x="{L-4}" y="{ys(50)+3.5}" text-anchor="end" font-size="9.5" fill="{INK}" opacity=".7">50%</text>'
    prev=None
    for i,(lab,v) in enumerate(pts):
        if v is not None and prev is not None:
            g+=f'<line x1="{xs(i-1):.1f}" y1="{ys(prev):.1f}" x2="{xs(i):.1f}" y2="{ys(v):.1f}" stroke="{rkcol(v)}" stroke-width="2.5" stroke-linecap="round"/>'
        if v is not None:
            g+=f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="3.5" fill="{rkcol(v)}"/>'
        g+=f'<text x="{xs(i):.1f}" y="{H-4}" text-anchor="middle" font-size="9.5" fill="{INK}" opacity=".6">{lab[0]}</text>'
        prev=v
    return f'<svg class="tr-spark" viewBox="0 0 {W} {H}">{g}</svg>'
def rk_line(label, sub, series):
    n=sum(x[0] for x in series[-3:]); o=sum(x[1] for x in series[-3:]); v=pct(n,o)
    return (f'<li class="tr-rk"><div class="tr-rkh"><div class="tr-mt"><b>{label}</b><span>{sub}</span></div>'
            f'<div class="tr-n"><b style="color:{rkcol(v)}">{v}%</b><span>{n} of {o}</span></div></div>{spark(series)}</li>')
SR_ENR={"South Morang":23,"Craigieburn":69}
# givers: (code, fams, enrolled, closed, fams_recent, enr_recent, fams_prior, enr_prior, med_days, last_tour)
GIVERS={
 "South Morang":[
  ("S-HBWH",18,2,5,0,0,18,2,177,"Apr"),("S-RPV4",15,1,6,12,1,3,0,29,"Oct"),("S-VGYF",12,5,3,11,4,1,1,87,"Sep"),
  ("S-IOVK",11,2,3,11,2,0,0,10,"Nov"),("S-RN6J",11,1,3,11,1,0,0,14,"Aug"),("S-L2B7",9,5,4,9,5,0,0,98,"Jul"),
  (None,59,8,1,6,1,53,7,162,"Jun")],
 "Craigieburn":[
  ("S-GWZO",33,15,7,13,4,20,11,49,"Jul"),("S-HBWH",29,7,11,29,7,0,0,21,"Nov"),("S-RK2L",23,8,9,23,8,0,0,10,"Oct"),
  ("S-RPV4",17,6,7,13,4,4,2,40,"Nov"),("S-P2CN",14,5,3,6,1,8,4,41,"Jun"),
  (None,44,21,0,15,6,29,15,46,"Oct")],
}
WINBACK={"South Morang":{"S-HBWH":12,"S-RPV4":10,"S-IOVK":7,"S-VGYF":7,"S-RN6J":5,"S-L2B7":4,None:46},
         "Craigieburn":{"S-HBWH":16,"S-GWZO":13,"S-RPV4":9,"S-RK2L":8,"S-P2CN":4,None:15}}

def pct(a,b): return round(100*a/b) if b else None
CENTRE_PCT={c:pct(e,f) for c,(f,e) in HEAD.items()}
TEAM=(pct(sum(e for f,e in HEAD.values()),sum(f for f,e in HEAD.values())),"both centres",None)
def col(v): return SAGE if v>=TOP else (AMBER if v>=IND else EARTH)
def nm(c): return NAMES.get(c, "Not named")

def bar(v, maxv=100):
    W=300; x=lambda p: 12+(W-24)*min(p,maxv)/maxv
    return (f'<svg class="tr-b" viewBox="0 0 {W} 14"><line x1="12" y1="7" x2="{W-12}" y2="7" stroke="rgba(43,35,32,.12)" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="12" y1="7" x2="{x(v):.1f}" y2="7" stroke="{col(v)}" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="{x(IND):.1f}" y1="0" x2="{x(IND):.1f}" y2="14" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x(TOP):.1f}" y1="0" x2="{x(TOP):.1f}" y2="14" stroke="{INK}" stroke-width="2"/></svg>')

def trend(centre, m=None, bands=True):
    m=m or ALL[centre]; pts=[]
    for i in range(1,len(m)):                       # rolling three months, Feb..Nov
        f=sum(x[0] for x in m[max(0,i-2):i+1]); e=sum(x[1] for x in m[max(0,i-2):i+1])
        pts.append((MONTHS[i], pct(e,f), f))
    W,H,L,R,T,B=330,150,62,10,12,26
    xs=lambda i: L+(W-L-R)*i/(len(pts)-1); ys=lambda v: T+(H-T-B)*(1-v/100)
    g=""
    if not bands:
        for i in range(1,len(pts)):
            g+=f'<line x1="{xs(i-1):.1f}" y1="{ys(pts[i-1][1]):.1f}" x2="{xs(i):.1f}" y2="{ys(pts[i][1]):.1f}" stroke="#5E80A0" stroke-width="3" stroke-linecap="round"/>'
        for i,(lab,v,f) in enumerate(pts):
            g+=f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="5" fill="#5E80A0"/>'
            g+=f'<text x="{xs(i):.1f}" y="{H-8}" text-anchor="middle" font-size="10" fill="{INK}" opacity=".7">{lab[0]}</text>'
        for v in (0,50,100):
            g+=f'<text x="{L-5}" y="{ys(v)+3.5}" text-anchor="end" font-size="9.5" fill="{INK}" opacity=".7">{v}%</text>'
            g+=f'<line x1="{L}" y1="{ys(v)}" x2="{W-R}" y2="{ys(v)}" stroke="{INK}" stroke-width="1" opacity=".08"/>'
        return f'<svg class="tr-trend" viewBox="0 0 {W} {H}">{g}</svg>'
    g+=f'<rect x="{L}" y="{ys(100)}" width="{W-L-R}" height="{ys(TOP)-ys(100)}" fill="{SAGE}" opacity=".10"/>'
    g+=f'<rect x="{L}" y="{ys(TOP)}" width="{W-L-R}" height="{ys(IND)-ys(TOP)}" fill="{AMBER}" opacity=".12"/>'
    g+=f'<rect x="{L}" y="{ys(IND)}" width="{W-L-R}" height="{ys(0)-ys(IND)}" fill="{EARTH}" opacity=".08"/>'
    for v,lab in ((IND,f"ind. ave. {IND}%"),(TOP,f"top performers {TOP}%")):
        g+=f'<line x1="{L}" y1="{ys(v)}" x2="{W-R}" y2="{ys(v)}" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3" opacity=".5"/>'
        g+=f'<text x="{L-5}" y="{ys(v)-1}" text-anchor="end" font-size="9.5" font-weight="700" fill="{INK}" opacity=".75">{v}%</text>'
        g+=f'<text x="{L-5}" y="{ys(v)+10}" text-anchor="end" font-size="8.5" fill="{INK}" opacity=".6">{"top" if v==TOP else "ind. ave."}</text>'
    for i in range(1,len(pts)):
        v0,v1=pts[i-1][1],pts[i][1]
        g+=f'<line x1="{xs(i-1):.1f}" y1="{ys(v0):.1f}" x2="{xs(i):.1f}" y2="{ys(v1):.1f}" stroke="{col(v1)}" stroke-width="3" stroke-linecap="round"/>'
    for i,(lab,v,f) in enumerate(pts):
        last=(i==len(pts)-1)
        g+=f'<circle cx="{xs(i):.1f}" cy="{ys(v):.1f}" r="5" fill="{"#fff" if last else col(v)}" stroke="{col(v)}" stroke-width="2.5"/>'
        g+=f'<text x="{xs(i):.1f}" y="{H-8}" text-anchor="middle" font-size="10" fill="{INK}" opacity=".7">{lab[0]}</text>'
    return f'<svg class="tr-trend" viewBox="0 0 {W} {H}">{g}</svg>'

def arrow(now, then, higher_better=True):
    if then is None or now is None: return '<div class="tr-arr na">—</div>'
    d=now-then
    if abs(d)<=0.1*max(then,1): return '<div class="tr-arr fl">→</div>'
    good=(d>0)==higher_better
    return f'<div class="tr-arr {"up" if good else "dn"}">{"↑" if d>0 else "↓"}</div>'

def cell(x, higher_better=False):
    if x is None: return '<div class="tr-c"><b>—</b></div>'
    n,of=x
    if of: return f'<div class="tr-c"><b>{pct(n,of)}%</b><span>{n} of {of}</span></div>'
    return f'<div class="tr-c"><b>{n}</b></div>'

CENTRE_OF=[None]
def giver_line(code, fams, enr, closed, fr, er, fp, ep, med, last):
    v=pct(enr,fams)
    now=pct(er,fr) if fr>=5 else None; then=pct(ep,fp) if fp>=5 else None
    if code is None: now=then=None
    od='' if code is None else f'<div class="tr-od">offered at the tour {pct(AT_TOUR.get((CENTRE_OF[0],code),0),fams)}%</div>'
    stale=f' <em>last tour {last}</em>' if code and last in ("Apr","May","Jun","Jul","Aug") else ""
    return (f'<li class="tr-ln"><div class="tr-lt">{nm(code)}{stale}</div><div class="tr-mid"><div class="tr-n"><b>{v}%</b><span>{enr} of {fams}</span></div>{bar(v)}{od}</div>{arrow(now,then)}</li>')

def panel(centre):
    f,e=HEAD[centre]; v=pct(e,f)
    miss="".join(rk_line(lab,sub,ser) for lab,(sub,ser) in RK[centre].items())
    oad=sum(x[0] for x in OFFER_AT[centre][-3:]); oan=sum(x[1] for x in OFFER_AT[centre][-3:]); oa=pct(oan,oad)
    gv=sorted(GIVERS[centre], key=lambda g:(g[0] is None, -(g[2]/g[1])))
    CENTRE_OF[0]=centre
    conv="".join(giver_line(*g) for g in gv)
    closed="".join(f'<li class="tr-ln"><div class="tr-lt">{nm(g[0])}</div><div class="tr-mid"><div class="tr-n"><b>{pct(g[3],g[1])}%</b><span>{g[3]} of {g[1]}</span></div></div><div></div></li>' for g in gv if g[0])
    speed="".join(f'<li class="tr-ln"><div class="tr-lt">{nm(g[0])}</div><div class="tr-mid"><div class="tr-n"><b>{g[8]} days</b></div></div><div></div></li>' for g in gv if g[0])
    wb=WINBACK[centre]
    wbl="".join(f'<li class="tr-wb"><div class="tr-lt">{nm(c)}</div><div class="todo"><b>{n}</b></div><div><b>0</b></div><div><b>0</b></div><div><b>0</b></div><div><b>0</b></div></li>' for c,n in sorted(wb.items(), key=lambda kv:(kv[0] is None,-kv[1])))
    return f'''
  <div class="tr-team"><div class="k">Tour Completed → Enrolled · 12 months</div><div class="n"><b>{v}%</b><span>{e} of {f} families</span></div>{bar(v)}
    <div class="tr-tl">Trend · rolling three months <span>· open dot still maturing</span></div>{trend(centre)}</div>
  <div class="tr-team"><div class="k">Offered at the tour · target 100%</div><div class="n"><b style="color:{oacol(oa)}">{oa}%</b><span>{oan} of {oad} tours · last three months</span></div>
    <div class="tr-tl">Trend · rolling three months</div>{chart_oa(OFFER_AT[centre])}</div>
  <div class="centre"><ul class="measures tr">
    <li class="sec"><span class="sec-t">Record keeping</span><span class="sec-s">last three months · trend by month</span></li>{miss}
    <li class="sec"><span class="sec-t">Tour givers</span><span class="sec-s">Tour Completed → Enrolled · 12 months</span></li>{conv}
  </ul></div>'''

def section(logo):
    return f'''
<section id="tours" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>Tours</h1><div class="sub">{ASOF}</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <nav class="toggle tr" role="tablist" aria-label="Centre">
    <button type="button" role="tab" aria-selected="true" data-tr="tr-sm">South Morang</button>
    <button type="button" role="tab" aria-selected="false" data-tr="tr-cb">Craigieburn</button>
  </nav>
  <div class="screens">
    <div id="tr-sm" class="screen">{panel("South Morang")}</div>
    <div id="tr-cb" class="screen" hidden>{panel("Craigieburn")}</div>
  </div>
  <details class="foot"><summary>About the numbers</summary>
    <p><b>Window</b> is the 12 months to the issue date. The trend is a rolling three months, month by month; the open dot is the latest, which always reads low because enrolment runs 10 to 50 days behind the tour. Line and dots are earth below 40%, amber 40 to 80%, sage at 80% and above.</p>
    <p><b>Where 40% and 80% come from</b>: LineLeader, <i>2026 ECE Benchmark Report</i> (data from about 5,700 childcare operators on LineLeader). On the industry rate it says post-tour conversion is "trending toward 40%". On the top tier it defines the best-performing centres as those converting 79% or more of completed tours; we round that to 80% and set it as the mark for every tour giver.</p>
    <p><b>Tour to Enrolled</b> (lead card and trend): of every family marked <i>Tour Completed</i> in LineLeader, the share that moved to <i>Enrolled</i> on or after it. Every family tours before enrolling, so every <i>Tour Completed</i> counts, including those recorded later rather than on the day. A family who toured, was never recorded and didn't enrol can't be counted; outcomes are recorded for 90% or more of booked tours, so that gap is small. Each family counts once (dashboard view tour_giver, status runs included).</p>
    <p><b>Record keeping</b>: the line is the last three months, with the trend as a rolling three months by month; the dashed line is 90%, which is where a kept record should sit. Sage at 90% and above, amber 70 to 90, earth below 70. <i>Tour recorded on the day</i>: of families marked Tour Completed, the share with a tour entry or Tour task made at the time. The rest were marked Tour Completed later, usually in a run of clicks at enrolment (the dashboard calls these status runs); they count in the centre rate but carry no name, so they can't be credited to a tour giver.</p>
    <p><b>Tour givers</b>: tours recorded on the day only, because only those name a person. The staff member on the tour's own LineLeader record (the tour entry, else who completed the Tour task, else its assignee). First names from the dashboard's released staff list; a line needs five families in the window. The arrow compares the last six months with the six before, where each has five or more families. "Last tour" shows when a giver hasn't toured in the last two months.</p>
    <p><b>Offered at the tour</b>: of tours recorded on the day, the share where the family moved to <i>Offered</i> (or straight to <i>Orientation</i> or <i>Enrolled</i>) within an hour of <i>Tour Completed</i> — the closest the record gets to "before they walk out the door". From 11 Nov 26 every tour ends with an offer, so the target is 100%: sage at 90% and above, amber 70 to 90, earth below 70. LineLeader's status history starts 28 Jan 26, so the trend begins in February. Under each tour giver, <b>offered at the tour</b> is the same measure over 12 months.</p>
  </details>
</section>'''

tr_js = """
  var trTabs = Array.prototype.slice.call(document.querySelectorAll('.toggle.tr button'));
  trTabs.forEach(function(t){ t.addEventListener('click', function(){
    trTabs.forEach(function(x){ x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
    ['tr-sm','tr-cb'].forEach(function(id){ document.getElementById(id).hidden = (id !== t.dataset.tr); });
  }); });
"""

tr_css = """
.tr-team { background:#fff; border-radius:16px; padding:14px 16px; margin:14px 18px 0; } .tr-team .k { font-size:10.5px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--earth); }
.tr-team .n { display:flex; align-items:baseline; gap:10px; } .tr-team .n b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:40px; line-height:1; } .tr-team .n span { font-size:12.5px; color:var(--ink-70); font-weight:700; }
.tr-tl { font-size:11.5px; font-weight:800; color:var(--ink-70); margin-top:14px; } .tr-tl span { font-weight:600; }
.tr-trend { width:100%; height:auto; display:block; margin-top:4px; font-family:"Nunito",sans-serif; }
.tr-b { width:100%; height:14px; display:block; margin-top:4px; }
.measures.tr .sec { padding:22px 0 6px; }
.tr-ln { display:grid; grid-template-columns:84px 1fr 34px; align-items:center; gap:8px; padding:9px 0; }
.tr-lt { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; line-height:1.1; } .tr-lt em { display:block; font:700 10px/1.2 "Nunito",sans-serif; color:var(--ink-50); margin-top:2px; }
.tr-mid { min-width:0; } .tr-n { display:flex; align-items:baseline; gap:8px; } .tr-n b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:24px; line-height:1; } .tr-n span { font-size:11.5px; color:var(--ink-70); font-weight:700; }
.tr-arr { font-size:26px; font-weight:800; text-align:center; line-height:1; } .tr-arr.up { color:var(--sage); } .tr-arr.dn { color:#B3261E; } .tr-arr.fl { color:#E39B2D; } .tr-arr.na { color:#c9c3ba; }
.tr-ms { display:grid; grid-template-columns:1fr 64px 64px 64px; align-items:center; gap:6px; padding:9px 0; } .tr-msh span { font-size:9.5px; color:var(--ink-50); font-weight:700; text-transform:uppercase; letter-spacing:.04em; text-align:center; }
.tr-mt b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:15px; line-height:1.15; } .tr-mt span { font-size:11px; color:var(--ink-70); font-weight:700; }
.tr-rk { padding:10px 0 4px; } .tr-rkh { display:flex; justify-content:space-between; align-items:flex-end; gap:10px; } .tr-rkh .tr-n { flex-direction:column; align-items:flex-end; gap:2px; } .tr-spark { width:100%; height:auto; display:block; margin-top:2px; font-family:"Nunito",sans-serif; }
.tr-next { margin-top:12px; padding-top:10px; border-top:1px dashed rgba(43,35,32,.18); } .tr-next b { display:block; font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:15px; color:var(--ink-50); } .tr-next span { font-size:11.5px; color:var(--ink-50); font-weight:700; }
.tr-od { font-size:11px; font-weight:700; color:var(--ink-70); margin-top:3px; }
.tr-c { text-align:center; } .tr-c b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:20px; line-height:1; display:block; } .tr-c span { font-size:9.5px; color:var(--ink-50); font-weight:700; }
.tr-wb { display:grid; grid-template-columns:84px repeat(5,1fr); align-items:center; gap:4px; padding:8px 0; text-align:center; } .tr-wb .tr-lt { text-align:left; }
.tr-wb b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:18px; display:block; } .tr-wb span { font-size:9.5px; color:var(--ink-50); font-weight:700; text-transform:uppercase; letter-spacing:.04em; } .tr-wb .todo b { color:var(--earth); }
"""
