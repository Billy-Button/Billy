# Billy — Billy Button's phone app shell. Home screen + report screens.
# Reuses the Friday Night Report builder (fnr_build.py) for the report screen.
import pathlib, re
from fnr_build import html as report_html, sm, cb, icon, logo, fred, nun, ISSUE, WEEK_LABEL, SNAPSHOT, SAGE, EARTH

css = report_html.split("<style>")[1].split("</style>")[0]
legend = report_html.split('<div class="legend">')[1].split("</div>")[0]
foot = report_html.split('<details class="foot">')[1].split("</details>")[0]

ISSUED = "Sat 7 Nov 26"   # when the current issue went live (set by the Saturday run)

shell_css = """
.app { max-width:430px; margin:0 auto; min-height:100dvh; display:flex; flex-direction:column; }
.scr[hidden] { display:none; }
/* home */
.hero { background:var(--yellow); padding:max(16px, env(safe-area-inset-top)) 20px 18px 22px; border-radius:0 0 26px 26px; display:flex; align-items:center; justify-content:space-between; gap:14px; }
.hero .logo { width:150px; height:auto; display:block; flex:0 0 auto; }
.hero .txt { min-width:0; flex:1 1 auto; }
.hello { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:27px; line-height:1.05; margin:0 0 5px; white-space:nowrap; }
.hello-sub { font-size:13px; font-weight:700; color:var(--earth); white-space:nowrap; }
.tiles { padding:18px 18px 8px; display:grid; grid-template-columns:minmax(0,1fr); gap:12px; }
.tile { min-width:0; display:flex; align-items:center; gap:14px; width:100%; text-align:left; font:inherit; color:var(--ink); background:#fff; border:1px solid var(--ink-12); border-radius:20px; padding:16px 16px; cursor:pointer; -webkit-tap-highlight-color:transparent; box-shadow:0 1px 0 rgba(43,35,32,.04); }
.tile:active { transform:scale(.99); }
.tile[disabled] { cursor:default; background:transparent; border-style:dashed; }
.tile[disabled] .t-ico { opacity:.55; }
.t-ico { flex:0 0 52px; width:52px; height:52px; border-radius:16px; display:flex; align-items:center; justify-content:center; }
.t-ico svg { width:28px; height:28px; }
.t-body { min-width:0; flex:1 1 auto; display:block; }
.t-name, .t-sub { display:block; }
.t-name { font-family:"Fredoka","Nunito",sans-serif; font-weight:600; font-size:19px; line-height:1.1; }
.t-sub { font-size:12.5px; color:var(--ink-70); margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.t-badge { font-size:10px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--earth); border:1px solid var(--earth); border-radius:6px; padding:1px 6px; margin-left:6px; vertical-align:middle; }
.t-badge.live { color:var(--sage); border-color:var(--sage); }
.t-arrow { flex:0 0 auto; color:var(--ink-50); }
.home-foot { margin-top:auto; padding:18px 22px max(22px, env(safe-area-inset-bottom)); font-size:11.5px; color:var(--ink-50); display:flex; justify-content:space-between; align-items:center; }
.home-foot b { color:var(--ink-70); }
/* report screen top bar */
.topbar { position:sticky; top:0; z-index:6; background:var(--yellow); display:flex; align-items:center; gap:8px; padding:max(10px, env(safe-area-inset-top)) 12px 10px; }
.back { font:inherit; font-weight:800; color:var(--ink); background:transparent; border:0; padding:8px 8px 8px 4px; display:inline-flex; align-items:center; gap:4px; cursor:pointer; -webkit-tap-highlight-color:transparent; }
.topbar .ttl { min-width:0; }
.topbar h1 { font-size:22px; }
.topbar .sub { margin-top:2px; }
.topbar .logo { width:56px; margin-left:auto; }
/* placeholder */
.soon { padding:26px 22px; }
.soon h2 { font-size:24px; margin:0 0 8px; }
.soon p { font-size:14px; color:var(--ink-70); margin:0 0 12px; line-height:1.45; }
.soon ul { margin:0; padding-left:18px; font-size:14px; color:var(--ink-70); line-height:1.6; }
.pill { display:inline-block; font-size:11px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--earth); background:rgba(164,88,35,.1); border-radius:999px; padding:4px 10px; margin-bottom:14px; }
"""

ICON_REPORT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 19h16"/><path d="M7 15v-4"/><path d="M12 15V7"/><path d="M17 15v-7"/></svg>'
ICON_CASH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="12" rx="2.5"/><circle cx="12" cy="12" r="2.6"/><path d="M6.5 9.5h.01M17.5 14.5h.01"/></svg>'
ICON_KPI = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/><path d="M12 3.5V1.8M20.5 12h1.7"/></svg>'
ICON_PEOPLE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5"/><circle cx="17" cy="9.5" r="2.4"/><path d="M15.5 14.3c2.6 0 4.3 1.5 4.9 4.2"/></svg>'

def tile(target, name, sub, ico, bg, badge=None, live=False, disabled=False):
    b = f'<span class="t-badge{" live" if live else ""}">{badge}</span>' if badge else ""
    dis = " disabled" if disabled else ""
    arrow = '' if disabled else '<span class="t-arrow"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg></span>'
    return f'''<button class="tile" data-go="{target}"{dis}>
      <span class="t-ico" style="background:{bg}">{ico}</span>
      <span class="t-body"><span class="t-name">{name}{b}</span><span class="t-sub">{sub}</span></span>{arrow}
    </button>'''

home = f'''
<section id="home" class="scr">
  <div class="hero">
    <div class="txt"><div class="hello" id="hello">Hello</div><div class="hello-sub" id="hello-sub">Week ending {WEEK_LABEL}</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="Billy Button Early Learning">
  </div>
  <div class="tiles">
    {tile("report", "Friday Night Report", f"Weekly occupancy · w/e {WEEK_LABEL}", ICON_REPORT, "rgba(110,139,87,.18); color:#4d6a3a", "Live", live=True)}
    {tile("cash", "Cash position", "Weekly cash and funding · from the model", ICON_CASH, "rgba(94,128,160,.16); color:#3f5f7d", "Soon", disabled=True)}
    {tile("people", "People & rosters", "Hours, ratios and wage to revenue", ICON_PEOPLE, "rgba(164,88,35,.14); color:#8a4a1e", "Soon", disabled=True)}
    {tile("kpis", "KPIs", "The improvement plan's measures, tracked", ICON_KPI, "rgba(253,197,70,.35); color:#7a5a10", "Soon", disabled=True)}
  </div>
  <div class="home-foot"><span id="who">Billy · Billy Button reporting</span><span>v{ISSUE}</span></div>
</section>'''

report = f'''
<section id="report" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>Friday Night Report</h1><div class="sub">Weekly occupancy report · {WEEK_LABEL}</div></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <nav class="toggle" role="tablist" aria-label="Centre">
    <button type="button" role="tab" id="tab-sm" aria-controls="south-morang" aria-selected="true" data-target="south-morang">South Morang</button>
    <button type="button" role="tab" id="tab-cb" aria-controls="craigieburn" aria-selected="false" data-target="craigieburn">Craigieburn</button>
  </nav>
  <div class="legend">{legend}</div>
  <div class="screens">
    <div id="south-morang" class="screen" role="tabpanel" aria-labelledby="tab-sm">{sm}</div>
    <div id="craigieburn" class="screen" role="tabpanel" aria-labelledby="tab-cb" hidden>{cb}</div>
  </div>
  <details class="foot">{foot}</details>
</section>'''

def soon(id_, title, blurb, items):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'''
<section id="{id_}" class="scr" hidden>
  <header class="topbar">
    <button class="back" data-go="home" aria-label="Home"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></button>
    <div class="ttl"><h1>{title}</h1></div>
    <img class="logo" src="data:image/png;base64,{logo}" alt="">
  </header>
  <div class="soon"><span class="pill">Coming soon</span><h2>{title}</h2><p>{blurb}</p><ul>{lis}</ul></div>
</section>'''

cash = soon("cash", "Cash position", "The week's cash across the group, against the model, in the same plain style as the Friday Night Report.",
            ["Cash in bank by entity, Friday close", "Funding drawn against the cap, and the week it bites", "Receipts and payments this week against forecast", "Debtors over 30 days"])
people = soon("people", "People & rosters", "Who is rostered against who is booked, and what it costs.",
              ["Rostered hours against booked children, by room", "Wage to revenue, week by week", "Leave, vacancies and agency use", "Ratios flagged before the day, not after"])

kpis = soon("kpis", "KPIs", "The Turnaround Plan's key measures, one screen, updated as each plan reports.",
            ["Operations, Marketing and Finance plan measures side by side", "Each against its target and the date it is due", "Owner and status, plain words", "Trend since the plan started"])

page = f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#FDC546">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Billy">
<link rel="apple-touch-icon" href="data:image/png;base64,{icon}">
<link rel="icon" href="data:image/png;base64,{icon}">
<title>Billy</title>
<style>{css}
{shell_css}
</style>
</head>
<body>
<div class="app">
{home}
{report}
{cash}
{people}
{kpis}
</div>
<script>
(function(){{
  var scrs = ['home','report','cash','people','kpis'];
  var screens = {{'south-morang': document.getElementById('south-morang'), 'craigieburn': document.getElementById('craigieburn')}};
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.toggle button'));
  function showCentre(id, push){{
    if(!screens[id]) id = 'south-morang';
    Object.keys(screens).forEach(function(k){{ screens[k].hidden = (k !== id); }});
    tabs.forEach(function(t){{ t.setAttribute('aria-selected', t.dataset.target === id ? 'true' : 'false'); }});
    try {{ localStorage.setItem('bbw-centre', id); }} catch(e) {{}}
    if(push) setHash('report/' + id);
    window.scrollTo(0, 0);
  }}
  function setHash(h){{ if(location.hash !== '#' + h){{ try {{ history.pushState(null, '', '#' + h); }} catch(e) {{ location.hash = h; }} }} }}
  function route(){{
    var h = location.hash.replace('#','');
    var parts = h.split('/');
    var s = scrs.indexOf(parts[0]) >= 0 ? parts[0] : 'home';
    scrs.forEach(function(k){{ document.getElementById(k).hidden = (k !== s); }});
    if(s === 'report'){{
      var c = parts[1];
      if(!screens[c]){{ try {{ c = localStorage.getItem('bbw-centre') || 'south-morang'; }} catch(e) {{ c = 'south-morang'; }} }}
      showCentre(c, false);
    }}
    window.scrollTo(0, 0);
  }}
  document.addEventListener('click', function(e){{
    var b = e.target.closest('[data-go]'); if(!b || b.disabled) return;
    var go = b.dataset.go;
    if(go === 'report'){{ var c; try {{ c = localStorage.getItem('bbw-centre') || 'south-morang'; }} catch(err) {{ c = 'south-morang'; }} setHash('report/' + c); }}
    else if(go === 'home'){{ setHash('home'); }}
    else setHash(go);
    route();
  }});
  tabs.forEach(function(t){{ t.addEventListener('click', function(){{ showCentre(t.dataset.target, true); }}); }});
  window.addEventListener('hashchange', route);
  window.addEventListener('popstate', route);
  route();
  // swipe between centres on the report screen
  var x0 = null, y0 = null;
  document.addEventListener('touchstart', function(e){{ x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }}, {{passive:true}});
  document.addEventListener('touchend', function(e){{
    if(x0 === null || document.getElementById('report').hidden) return;
    var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null;
    if(Math.abs(dx) > 70 && Math.abs(dx) > Math.abs(dy) * 1.5) showCentre(dx < 0 ? 'craigieburn' : 'south-morang', true);
  }}, {{passive:true}});
  // greeting by time of day; name from the signed-in viewer when the platform tells us
  var hr = new Date().getHours();
  var greet = hr < 12 ? 'Good morning' : hr < 17 ? 'Good afternoon' : 'Good evening';
  var hello = document.getElementById('hello'); hello.textContent = greet;
  if(window.claude && window.claude.use){{
    window.claude.use('user').then(function(u){{
      if(!u || !u.me) return;
      var me = u.me(); var name = (me && me.name) ? String(me.name).split(' ')[0] : '';
      if(name) hello.textContent = greet + ', ' + name;
      var who = document.getElementById('who'); if(who && me && me.name) who.textContent = 'Signed in as ' + me.name;
    }}).catch(function(){{}});
  }}
}})();
</script>
</body>
</html>'''

if __name__ == "__main__":
    out = pathlib.Path("/mnt/user-data/outputs"); out.mkdir(parents=True, exist_ok=True)
    p = out / f"261106 - Billy app - v{ISSUE}.html"
    p.write_text(page, encoding="utf-8")
    print(p, len(page)//1024, "KB")
