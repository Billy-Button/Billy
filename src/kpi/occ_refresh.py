"""Rewrite kpi/occ.py (daily booked, attended, casual, rostered hours) from one dashboard pull.
Usage: python3 occ_refresh.py days.json "<snapshot_completed_at>"   rows: [centre, date, booked, attended, casual, rostered_hours, ...]. SQL: OCC_WAGES_TABS.md."""
import json, sys, pathlib, datetime as dt
j = json.load(open(sys.argv[1]))
if isinstance(j, list) and j and isinstance(j[0], dict) and "text" in j[0]: j = json.loads(j[0]["text"])
rows = j["rows"] if isinstance(j, dict) else j
snap = dt.datetime.fromisoformat(sys.argv[2])
D = [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows if r[1] >= "2026-03-01"]
pathlib.Path(__file__).with_name("occ.py").write_text(f"# Occupancy and Wages tabs data, dashboard snapshot {snap:%d %b %y %H:%M}\nSNAP = {snap.isoformat()!r}\nD = {D!r}\n")
print("occ.py:", snap.date(), len(D))
