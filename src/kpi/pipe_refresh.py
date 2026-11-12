"""Rewrite kpi/pipe.py (Pipeline Yesterday / Month data) from two dashboard pulls.
Usage: python3 pipe_refresh.py events.json first_contact.json "<snapshot_completed_at>"
events.json: rows [g, centre, period, kind, n, x] (g = D daily or M monthly); first_contact.json: rows [centre, enquired 'YYYY-MM-DD HH:MM', first contact or null, status].
Each file may be the bare run_sql result, the saved tool-result wrapper, or a plain list of rows. SQL: PIPELINE_TABS.md."""
import json, sys, pathlib, datetime as dt
def rows(p):
    j = json.load(open(p))
    if isinstance(j, list) and j and isinstance(j[0], dict) and "text" in j[0]: j = json.loads(j[0]["text"])
    return j["rows"] if isinstance(j, dict) else j
ev, fc = rows(sys.argv[1]), rows(sys.argv[2]); snap = dt.datetime.fromisoformat(sys.argv[3])
D = [(c, p, k, n or 0, x or 0) for g, c, p, k, n, x in ev if g == "D"]
M = [(c, p, k, n or 0, x or 0) for g, c, p, k, n, x in ev if g == "M"]
F = [tuple(r) for r in fc]
pathlib.Path(__file__).with_name("pipe.py").write_text(
    f"# Pipeline tabs data, dashboard snapshot {snap:%d %b %y %H:%M}\nSNAP = {snap.isoformat()!r}\nD = {D!r}\nM = {M!r}\nF = {F!r}\n")
print("pipe.py:", snap.date(), len(D), len(M), len(F))
