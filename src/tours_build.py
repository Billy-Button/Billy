# Tours — Billy's third screen: tour givers A–E, 13-week window, benchmark 40%. Figures from the dashboard touchpoints (11 Nov 26 snapshot).
from fnr_build import SAGE, EARTH, INK
AMBER="#E39B2D"; RED="#B3261E"
WINDOW="13 weeks to 6 Nov"; PRIOR_LABEL="prior 13 weeks"

TEAM=(20, "18 of 90", 37)
CONV=[("A",35,"8 of 23",None),("B",20,"4 of 20",20),("D",20,"2 of 10",None),("C",15,"3 of 20",44),("E",9,"1 of 11",None)]
SPEED=[("A",10,"days to Enrolled",None),("B",24,"",32),("D",10,"",None),("C",21,"",24),("E",14,"",None)]
OFFER=[("A",39,"9 of 23",None),("B",45,"9 of 20",60),("D",20,"2 of 10",None),("C",35,"7 of 20",44),("E",27,"3 of 11",None)]
WINBACK=[("A",14),("B",50),("D",11),("C",51),("E",9)]

def bar(v, tick=80, ind=40, maxv=100):
    W=300; x=lambda p: 12+(W-24)*min(p,maxv)/maxv
    col = SAGE if v>=tick else (AMBER if v>=ind else EARTH)
    return (f'<svg class="tr-b" viewBox="0 0 {W} 14"><line x1="12" y1="7" x2="{W-12}" y2="7" stroke="rgba(43,35,32,.12)" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="12" y1="7" x2="{x(v):.1f}" y2="7" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="{x(ind):.1f}" y1="0" x2="{x(ind):.1f}" y2="14" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x(tick):.1f}" y1="0" x2="{x(tick):.1f}" y2="14" stroke="{INK}" stroke-width="2"/></svg>')
def team_bar(v, tick=80, ind=40, maxv=100):
    W=300; x=lambda p: 12+(W-24)*min(p,maxv)/maxv
    col = SAGE if v>=tick else (AMBER if v>=ind else EARTH)
    return (f'<svg class="tr-b tr-bt" viewBox="0 0 {W} 34"><line x1="12" y1="7" x2="{W-12}" y2="7" stroke="rgba(43,35,32,.12)" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="12" y1="7" x2="{x(v):.1f}" y2="7" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
            f'<line x1="{x(ind):.1f}" y1="0" x2="{x(ind):.1f}" y2="14" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x(tick):.1f}" y1="0" x2="{x(tick):.1f}" y2="14" stroke="{INK}" stroke-width="2"/>'
            f'<text x="{x(ind):.1f}" y="29" text-anchor="middle" font-size="10.5" fill="{INK}" opacity=".7">ind. ave. {ind}%</text>'
            f'<text x="{x(tick):.1f}" y="29" text-anchor="middle" font-size="10.5" fill="{INK}" opacity=".7">top performers {tick}%</text></svg>')
NAMES={"A":"Pallavi","B":"Robyn","C":"Fiona","D":"Ebony","E":"Angelique"}  # staff_names released 11 Nov 26
def nm(l): return NAMES.get(l, f"Name {l}")
def arrow(now, then, higher_better=True):
    if then is None: return '<div class="tr-arr na">—</div>'
    d=now-then
    if abs(d)<=0.1*then: return '<div class="tr-arr fl">→</div>'
    good=(d>0)==higher_better
    return f'<div class="tr-arr {"up" if good else "dn"}">{"↑" if d>0 else "↓"}</div>'
def line(l, big, small, arr, b=""):
    return f'<li class="tr-ln"><div class="tr-lt">{nm(l)}</div><div class="tr-mid"><div class="tr-n"><b>{big}</b><span>{small}</span></div>{b}</div>{arr}</li>'

def section(logo):
    conv="".join(line(l,f"{v}%",s,arrow(v,p),bar(v)) for l,v,s,p in CONV)
    speed="".join(line(l,f"{v} days","",arrow(v,p,False)) for l,v,s,p in SPEED)
    offer="".join(line(l,f"{v}%",s,arrow(v,p)) for l,v,s,p in OFFER)
    wb="".join(f'<li class="tr-wb"><div class="tr-lt">{nm(l)}</div><div class="todo"><b>{n}</b></div><div><b>0</b></div><div><b>0</b></div><div><b>0</b></div><div><b>0</b></div></li>' for l,n in WINBACK)
    t_pct, t_det, t_prior = TEAM
    return f'''
<section id="tours" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>Tours</h1><div class="sub">{WINDOW} · both centres</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <div class="tr-team"><div class="k">Billy Button · tour to Enrolled</div><div class="n"><b>{t_pct}%</b><span>{t_det} · {PRIOR_LABEL} {t_prior}%</span><div style="margin-left:auto">{arrow(t_pct,t_prior)}</div></div>{team_bar(t_pct)}</div>
  <div class="centre"><ul class="measures tr">
    <li class="sec"><span class="sec-t">Conversion</span><span class="sec-s">Tour Completed → Enrolled</span></li>{conv}
    <li class="sec"><span class="sec-t">Speed</span><span class="sec-s">median days from the tour to Enrolled</span></li>{speed}
    <li class="sec"><span class="sec-t">Closed on the day</span><span class="sec-s">moved to Offered or further on the tour day</span></li>{offer}
    <li class="sec"><span class="sec-t">Win-back</span><span class="sec-s">toured before, not enrolled · from next issue</span></li>
    <li class="tr-wb tr-wbh"><div></div><span>to call</span><span>called</span><span>reached</span><span>re-toured</span><span>enrolled</span></li>{wb}
  </ul></div>
  <details class="foot"><summary>About the numbers</summary>
    <p><b>Tour giver</b> is the staff member on the tour's own LineLeader record (the tour entry, else who completed the Tour task, else its assignee). First names only, from the dashboard's released staff list. A line shows only after five tours in the window.</p>
    <p><b>Window</b> is the 13 weeks to the Friday of the issue; arrows compare with the 13 weeks before. Green up, red down, orange within 10%. On Speed, fewer days is green.</p>
    <p><b>Conversion</b>: families toured who moved to <i>Enrolled</i> in LineLeader on or after the tour, credited to the family's last tour (dashboard view tour_giver). Bulk status edits that look like tours ("status runs") are left out. Two marks on each bar: the industry average, 40%, and top performers, 80%.</p>
    <p><b>Where 40% and 80% come from</b>: LineLeader, <i>2026 ECE Benchmark Report</i> (data from about 5,700 childcare operators on LineLeader). On the industry rate it says post-tour conversion is "trending toward 40%". On the top tier it defines the best-performing centres as those converting 79% or more of completed tours; we round that to 80% and set it as the mark for every tour giver. Below 40% shows earth, 40 to 80% amber, 80% and above sage.</p>
    <p><b>Speed</b>: median days from the tour to the move to <i>Enrolled</i>.</p>
    <p><b>Closed on the day</b>: moved to <i>Offered</i> or further in LineLeader on the day of the tour.</p>
    <p><b>Win-back</b>: LineLeader tasks assigned to each giver for families who toured and never enrolled, and their outcomes. "To call" is the pile today; the rest fill as calls are logged.</p>
  </details>
</section>'''

tr_css = """
.tr-chips { display:flex; gap:6px; padding:12px 18px 0; } .tr-chips span { border:1.5px solid var(--ink); border-radius:999px; padding:5px 12px; font-size:12.5px; font-weight:800; } .tr-chips .on { background:var(--ink); color:#fff; }
.tr-team { background:#fff; border-radius:16px; padding:14px 16px; margin:14px 18px 0; } .tr-team .k { font-size:10.5px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--earth); }
.tr-team .n { display:flex; align-items:baseline; gap:10px; } .tr-team .n b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:40px; line-height:1; } .tr-team .n span { font-size:12.5px; color:var(--ink-70); font-weight:700; }
.tr-note { font-size:11.5px; color:var(--ink-70); margin-top:6px; }
.tr-b { width:100%; height:14px; display:block; margin-top:4px; } .tr-bt { height:34px; font-family:"Nunito",sans-serif; }
.measures.tr .sec { padding:22px 0 6px; }
.tr-ln { display:grid; grid-template-columns:72px 1fr 34px; align-items:center; gap:8px; padding:9px 0; }
.tr-lt { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; line-height:1.1; }
.tr-mid { min-width:0; } .tr-n { display:flex; align-items:baseline; gap:8px; } .tr-n b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:24px; line-height:1; } .tr-n span { font-size:11.5px; color:var(--ink-70); font-weight:700; }
.tr-arr { font-size:26px; font-weight:800; text-align:center; line-height:1; } .tr-arr.up { color:var(--sage); } .tr-arr.dn { color:#B3261E; } .tr-arr.fl { color:#E39B2D; } .tr-arr.na { color:#c9c3ba; }
.tr-wb { display:grid; grid-template-columns:72px repeat(5,1fr); align-items:center; gap:4px; padding:8px 0; text-align:center; } .tr-wb .tr-lt { text-align:left; }
.tr-wb b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:18px; display:block; } .tr-wb span { font-size:9.5px; color:var(--ink-50); font-weight:700; text-transform:uppercase; letter-spacing:.04em; } .tr-wb .todo b { color:var(--earth); }
"""
