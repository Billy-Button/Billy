# Tours — Billy's third screen: tour givers A–E, 13-week window, benchmark 40%. Figures from the dashboard touchpoints (11 Nov 26 snapshot).
from fnr_build import SAGE, EARTH, INK
AMBER="#E39B2D"; RED="#B3261E"
WINDOW="13 weeks to 6 Nov"; PRIOR_LABEL="prior 13 weeks"

TEAM=(20, "25 of 122", 35)          # this %, detail, prior %
CONV=[("A",30,"7 of 23",None),("C",22,"7 of 32",33),("D",18,"2 of 11",None),("B",16,"6 of 37",29),("E",16,"3 of 19",39)]
SPEED=[("A",10,"fastest 4 · slowest 34",None),("C",20,"4 · 46",7),("D",10,"5 · 14",None),("B",13,"5 · 32",5),("E",11,"5 · 32",14)]
OFFER=[("A",26,"6 of 23",None),("C",25,"8 of 32",22),("D",18,"2 of 11",None),("B",27,"10 of 37",71),("E",21,"4 of 19",33)]
WINBACK=[("A",14),("C",51),("D",11),("B",50),("E",34)]

def bar(v, tick=40, maxv=60):
    W=300; x=lambda p: 12+(W-24)*min(p,maxv)/maxv
    col = SAGE if v>=tick else (AMBER if v>=tick-10 else EARTH)
    return (f'<svg class="tr-b" viewBox="0 0 {W} 14"><line x1="12" y1="7" x2="{W-12}" y2="7" stroke="rgba(43,35,32,.12)" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="12" y1="7" x2="{x(v):.1f}" y2="7" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="{x(tick):.1f}" y1="0" x2="{x(tick):.1f}" y2="14" stroke="{INK}" stroke-width="2"/></svg>')
def arrow(now, then, higher_better=True):
    if then is None: return '<div class="tr-arr na">—</div>'
    d=now-then
    if abs(d)<=0.1*then: return '<div class="tr-arr fl">→</div>'
    good=(d>0)==higher_better
    return f'<div class="tr-arr {"up" if good else "dn"}">{"↑" if d>0 else "↓"}</div>'
def line(l, big, small, arr, b=""):
    return f'<li class="tr-ln"><div class="tr-lt">Name {l}</div><div class="tr-mid"><div class="tr-n"><b>{big}</b><span>{small}</span></div>{b}</div>{arr}</li>'

def section(logo):
    conv="".join(line(l,f"{v}%",s,arrow(v,p),bar(v)) for l,v,s,p in CONV)
    speed="".join(line(l,f"{v} days",s,arrow(v,p,False)) for l,v,s,p in SPEED)
    offer="".join(line(l,f"{v}%",s,arrow(v,p)) for l,v,s,p in OFFER)
    wb="".join(f'<li class="tr-wb"><div class="tr-lt">Name {l}</div><div class="todo"><b>{n}</b></div><div><b>0</b></div><div><b>0</b></div><div><b>0</b></div><div><b>0</b></div></li>' for l,n in WINBACK)
    t_pct, t_det, t_prior = TEAM
    return f'''
<section id="tours" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>Tours</h1><div class="sub">{WINDOW} · both centres</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <div class="tr-team"><div class="k">Billy Button · tour to enrolment</div><div class="n"><b>{t_pct}%</b><span>{t_det} · industry 40%</span><div style="margin-left:auto">{arrow(t_pct,t_prior)}</div></div>{bar(t_pct)}<div class="tr-note">{PRIOR_LABEL} {t_prior}% · tick is the LineLeader 2026 benchmark · names matched to staff shortly</div></div>
  <div class="centre"><ul class="measures tr">
    <li class="sec"><span class="sec-t">Conversion</span><span class="sec-s">Tour Completed → Enrolment complete</span></li>{conv}
    <li class="sec"><span class="sec-t">Speed</span><span class="sec-s">days from the tour to Pending</span></li>{speed}
    <li class="sec"><span class="sec-t">Offer made at the tour</span><span class="sec-s">of tours completed</span></li>{offer}
    <li class="sec"><span class="sec-t">Win-back</span><span class="sec-s">toured before, not enrolled · from next issue</span></li>
    <li class="tr-wb tr-wbh"><div></div><span>to call</span><span>called</span><span>reached</span><span>re-toured</span><span>enrolled</span></li>{wb}
  </ul></div>
  <details class="foot"><summary>About the numbers</summary>
    <p><b>Name A, Name B…</b> are tour givers, from the staff member on LineLeader's <i>Tour Completed</i> record. Names will be matched to staff shortly; until then the key is held by Cameron. A line shows only after five tours in the window.</p>
    <p><b>Window</b> is the 13 weeks to the Friday of the issue; arrows compare with the 13 weeks before. Green up, red down, orange within 10%. On Speed, fewer days is green.</p>
    <p><b>Conversion</b>: tours completed that reached <i>Enrolment complete</i> in Owna. The tick is 40%: LineLeader 2026 ECE Benchmark Report, post-tour conversion across 5,700 operators.</p>
    <p><b>Speed</b>: days from the tour to the enrolment going <i>Pending</i> in Owna (until the dashboard carries the Pending date, measured to the pull, which includes our processing time).</p>
    <p><b>Offer made at the tour</b>: moved to <i>Offered</i> in LineLeader within two hours of the tour.</p>
    <p><b>Win-back</b>: LineLeader tasks assigned to each giver for families who toured and never enrolled, and their outcomes. "To call" is the pile today; the rest fill as calls are logged.</p>
  </details>
</section>'''

tr_css = """
.tr-chips { display:flex; gap:6px; padding:12px 18px 0; } .tr-chips span { border:1.5px solid var(--ink); border-radius:999px; padding:5px 12px; font-size:12.5px; font-weight:800; } .tr-chips .on { background:var(--ink); color:#fff; }
.tr-team { background:#fff; border-radius:16px; padding:14px 16px; margin:14px 18px 0; } .tr-team .k { font-size:10.5px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--earth); }
.tr-team .n { display:flex; align-items:baseline; gap:10px; } .tr-team .n b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:40px; line-height:1; } .tr-team .n span { font-size:12.5px; color:var(--ink-70); font-weight:700; }
.tr-note { font-size:11.5px; color:var(--ink-70); margin-top:6px; }
.tr-b { width:100%; height:14px; display:block; margin-top:4px; }
.measures.tr .sec { padding:22px 0 6px; }
.tr-ln { display:grid; grid-template-columns:72px 1fr 34px; align-items:center; gap:8px; padding:9px 0; }
.tr-lt { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; line-height:1.1; }
.tr-mid { min-width:0; } .tr-n { display:flex; align-items:baseline; gap:8px; } .tr-n b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:24px; line-height:1; } .tr-n span { font-size:11.5px; color:var(--ink-70); font-weight:700; }
.tr-arr { font-size:26px; font-weight:800; text-align:center; line-height:1; } .tr-arr.up { color:var(--sage); } .tr-arr.dn { color:#B3261E; } .tr-arr.fl { color:#E39B2D; } .tr-arr.na { color:#c9c3ba; }
.tr-wb { display:grid; grid-template-columns:72px repeat(5,1fr); align-items:center; gap:4px; padding:8px 0; text-align:center; } .tr-wb .tr-lt { text-align:left; }
.tr-wb b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:18px; display:block; } .tr-wb span { font-size:9.5px; color:var(--ink-50); font-weight:700; text-transform:uppercase; letter-spacing:.04em; } .tr-wb .todo b { color:var(--earth); }
"""
