# Pipeline Follow Up — Billy's second screen. One line per rule: this week, last week, four weeks ago, arrows.
# Source: dashboard exception ledger (rule findings with first_detected / last_seen) and enquiry_week.
import re
from fnr_build import SAGE, EARTH, INK

FU_ASOF = "Fri 6 Nov 26"
FU_WEEK_AGO = "30 Oct"
FU_FOUR_AGO = "9 Oct"

# (label, unit, this_txt, last_txt, four_txt, (this_n, last_n, four_n)) — all framed as "met the rule": up is good
DATA = {
 "South Morang": [
  ("sec", "First contact"),
  ("First contact within 10 min", "of new enquiries", "0 of 4", "0 of 3", "1 of 4", (0, 0, 1)),
  ("sec", "Tours"),
  ("Tours kept", "show rate · of tours booked", "4 of 4", "3 of 3", "3 of 4", (4, 3, 3)),
  ("Closed on the tour", "offer or form same day · of tours", "0 of 1", "3 of 4", "2 of 4", (0, 3, 2)),
  ("Tour outcome recorded", "of tours booked", "0 of 4", "2 of 3", "3 of 4", (0, 2, 3)),
  ("Tour followed up, 2 days", "of tours booked", "3 of 4", "2 of 3", "2 of 4", (3, 2, 2)),
  ("No-show followed up", "of tours not kept", "—", "—", "0 of 1", (None, None, 0)),
  ("sec", "Stalled"),
  ("Stalled cleared", "families moved on a stage", "24", "4", "3", (24, 4, 3)),
 ],
 "Craigieburn": [
  ("sec", "First contact"),
  ("First contact within 10 min", "of new enquiries", "2 of 6", "1 of 6", "3 of 5", (2, 1, 3)),
  ("sec", "Tours"),
  ("Tours kept", "show rate · of tours booked", "4 of 6", "5 of 6", "2 of 4", (4, 5, 2)),
  ("Closed on the tour", "offer or form same day · of tours", "1 of 5", "3 of 4", "7 of 8", (1, 3, 7)),
  ("Tour outcome recorded", "of tours booked", "1 of 6", "2 of 6", "3 of 4", (1, 2, 3)),
  ("Tour followed up, 2 days", "of tours booked", "4 of 6", "0 of 6", "0 of 4", (4, 0, 0)),
  ("No-show followed up", "of tours not kept", "2 of 2", "0 of 1", "1 of 2", (2, 0, 1)),
  ("sec", "Stalled"),
  ("Stalled cleared", "families moved on a stage", "26", "11", "15", (26, 11, 15)),
 ],
}
OPEN = {"South Morang": (48, 45, 18), "Craigieburn": (64, 58, 41)}

def arr(now, then):
    """up green, down red, within 10% of the comparison orange"""
    if now is None or then is None:
        return '<span class="fa flat">—</span>'
    d = now - then
    if abs(d) <= 0.1 * then:
        return '<span class="fa same">→</span>'
    return f'<span class="fa {"good" if d > 0 else "bad"}">{"↑" if d > 0 else "↓"}</span>'

def pct(txt):
    m = re.match(r'(\d+) of (\d+)', str(txt))
    if not m: return txt
    a, b = int(m.group(1)), int(m.group(2))
    return "—" if b == 0 else f"{round(100*a/b)}%"

def line(label, unit, this, last, four, nums):
    n_this, n_last, n_four = nums
    is_ratio = " of " in str(this) or " of " in str(last) or " of " in str(four)
    if is_ratio:
        def pv(t):
            m = re.match(r'(\d+) of (\d+)', str(t))
            return None if (not m or int(m.group(2)) == 0) else 100*int(m.group(1))/int(m.group(2))
        n_this, n_last, n_four = pv(this), pv(last), pv(four)
    now_big = pct(this) if is_ratio else this
    now_small = this if is_ratio else ""
    return f'''
      <li class="fl">
        <div class="fl-lab">{label}<span class="fl-unit">{unit}</span></div>
        <div class="fl-now">{now_big}<span class="fl-ns">{now_small}</span></div>
        <div class="fl-prev">{arr(n_this, n_last)}<span class="fl-pv">{pct(last)}</span></div>
        <div class="fl-prev">{arr(n_this, n_four)}<span class="fl-pv">{pct(four)}</span></div>
      </li>'''

def centre_panel(rows, name=None):
    out = []
    for r in rows:
        if r[0] == "sec":
            out.append(f'<li class="sec"><span class="sec-t">{r[1]}</span></li>')
        else:
            out.append(line(*r))
    o = OPEN.get(name)
    openline = f'<div class="fu-open"><b>{o[0]}</b> stalled (waiting on us) · {o[1]} last wk · {o[2]} four wks ago</div>' if o else ''
    head = '<li class="fu-head"><span></span><span>this wk</span><span>last wk</span><span>4 wks</span></li>'
    return f'{openline}<div class="centre"><ul class="measures fu">{head}{"".join(out)}</ul></div>'

fu_css = """
.measures.fu { padding-top:2px; }
.measures.fu .sec { padding:18px 0 4px; }
.fl { display:grid; grid-template-columns:minmax(0,1fr) 66px 50px 50px; align-items:center; gap:6px; padding:9px 0; border-bottom:1px solid rgba(43,35,32,.07); }
.fl:last-child { border-bottom:0; }
.fl-lab { font-size:13.5px; font-weight:700; line-height:1.2; min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.fl-unit { display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-size:10.5px; font-weight:600; color:var(--ink-50); margin-top:1px; }
.fl-now { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:22px; text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; line-height:1; }
.fl-ns { display:block; font-family:"Nunito",sans-serif; font-size:10px; font-weight:700; color:var(--ink-50); margin-top:2px; }
.fl-prev { display:flex; flex-direction:column; align-items:center; line-height:1.1; }
.fa { font-size:24px; font-weight:800; line-height:1; }
.fa.bad { color:#B3261E; } .fa.good { color:var(--sage); } .fa.same { color:#E39B2D; } .fa.flat { color:var(--ink-50); }
.fu-open { padding:8px 18px 0; font-size:12.5px; color:var(--ink-70); } .fu-open b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:16px; color:var(--ink); }
.fl-pv { font-size:10.5px; font-weight:700; color:var(--ink-70); white-space:nowrap; margin-top:1px; }
.fl-pk { display:none; font-size:9px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:var(--ink-50); }
.fu-head { display:grid; grid-template-columns:minmax(0,1fr) 66px 50px 50px; gap:6px; padding:12px 0 0; font-size:9.5px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; color:var(--ink-50); text-align:center; }
.fu-head span:first-child { text-align:left; }
.fu-act { margin:18px 18px 0; padding:12px 16px; background:#fff; border-radius:14px; font-size:13px; line-height:1.45; }
.fu-act b { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; }
"""

fu_notes = f"""
    <summary>About the numbers</summary>
    <p>Every line counts families who <b>met the rule</b>, so up is good: green arrow = more than the comparison, red = fewer, orange = within 10% either side. <b>This wk</b> is the week ending {FU_ASOF}; <b>last wk</b> ends {FU_WEEK_AGO}, <b>4 wks</b> ends {FU_FOUR_AGO}. All from the dashboard's rule findings (when each miss was first detected) against the week's enquiries and tours.</p>
    <p><b>First contact within 10 min</b>: new enquiries in the week whose first outgoing human contact — a call, text or email logged in LineLeader — came within 10 minutes of the enquiry arriving. LineLeader data, read through the dashboard. The rule is 10 minutes; it carries no forecast or target. A call that is not logged does not count.</p>
    <p><b>Tours kept</b>: the dashboard's show rate — booked tours whose day has passed less those recorded <i>Tour Not Completed</i>. <b>Offer made at the tour</b>: moved to <i>Offered</i> in LineLeader within two hours of the tour. <b>Tour outcome recorded</b>: tours booked less those still with no outcome entered. <b>Tour followed up, 2 days</b>: tours booked less those with no call, text or email within 2 business days. <b>No-show followed up</b>: tours recorded <i>Tour Not Completed</i> less those not contacted.</p>
    <p><b>Follow-ups cleared</b>: families whose stalled flag was cleared in the week because the next step happened. The line above the list is the other side of it: stalled (waiting on us) at the close of the week (stalled at a stage), with the two earlier readings. That one should fall.</p>
    <p>Where a miss is detected after the week closes it counts in the week detected, so recent weeks can firm up for a week or two. Names are never shown here; each line has its own list on the dashboard's Follow-ups screen.</p>
"""

def section(logo):
    return f'''
<section id="followups" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>Pipeline Follow Up</h1><div class="sub">Families waiting on us · w/e {FU_ASOF[4:]}</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <nav class="toggle fu" role="tablist" aria-label="Centre">
    <button type="button" role="tab" aria-selected="true" data-fu="fu-sm">South Morang</button>
    <button type="button" role="tab" aria-selected="false" data-fu="fu-cb">Craigieburn</button>
  </nav>
  <div class="screens">
    <div id="fu-sm" class="screen">{centre_panel(DATA["South Morang"], "South Morang")}</div>
    <div id="fu-cb" class="screen" hidden>{centre_panel(DATA["Craigieburn"], "Craigieburn")}</div>
  </div>
  <div class="fu-act"><b>Where to act.</b> Dashboard → Follow-ups: each line is a filter; work it record by record in LineLeader. Every line here should go up; the waiting number should come down.</div>
  <details class="foot">{fu_notes}</details>
</section>'''

fu_js = """
  var fuTabs = Array.prototype.slice.call(document.querySelectorAll('.toggle.fu button'));
  fuTabs.forEach(function(t){ t.addEventListener('click', function(){
    fuTabs.forEach(function(x){ x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
    ['fu-sm','fu-cb'].forEach(function(id){ document.getElementById(id).hidden = (id !== t.dataset.fu); });
  }); });
"""
