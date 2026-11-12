"""Rewrite kpi/daily.py from a dashboard pull.
Usage: python3 refresh_daily.py rows.json "2026-11-12T03:08:46+11:00"
rows.json: the run_sql result rows [[centre, date, hrs, booked|null], ...] from the SQL in WAGES_DAILY.md."""
import json, sys, pathlib, datetime as dt
rows = json.load(open(sys.argv[1])); snap = dt.datetime.fromisoformat(sys.argv[2])
out = {"South Morang": [], "Craigieburn": []}
for c, d, h, b in rows:
    if c in out: out[c].append((d, float(h), None if b is None else int(b)))
for c in out: out[c].sort()
asat = snap.strftime("%-d %b %y")
p = pathlib.Path(__file__).with_name("daily.py")
p.write_text(f"# Daily rostered hours and booked children (dashboard current_owna_roster_day + current_owna_occupancy_day), snapshot {snap:%d %b %y %H:%M}\n"
             f"ASAT = {asat!r}\nSNAP = {snap.isoformat()!r}\nSM = {out['South Morang']!r}\nCB = {out['Craigieburn']!r}\n")
print("daily.py:", asat, len(out["South Morang"]), len(out["Craigieburn"]))
