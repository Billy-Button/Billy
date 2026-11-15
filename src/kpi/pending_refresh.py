"""Rewrite kpi/pending_followup.py from the Dashboard's pipeline_committed rows.
Usage (from src): python3 kpi/pending_refresh.py rows.json "<snapshot_completed_at>"
rows.json: the result rows of SQL in PENDING_FOLLOWUP.md, as a list of [centre_key, expected_start_month, families, pulled, days_requested, days_booked]."""
import json, sys, datetime as dt, pathlib
rows = json.load(open(sys.argv[1])); snap = dt.datetime.fromisoformat(sys.argv[2])
pf = {c: {"past": [0, 0.0], "no date": [0, 0.0], "no days": [0, 0.0]} for c in ("South Morang", "Craigieburn")}
for c, m, fam, pulled, req, booked in rows:
    if c not in pf: continue
    if m in ("past", "no date"): pf[c][m][0] += fam; pf[c][m][1] += float(req or 0)
    elif not req: pf[c]["no days"][0] += fam
out = ("# Pending records counted as nil in the Base Case until updated in Owna. Dashboard semantic_v2.pipeline_committed, snapshot "
       f"{snap:%d %b %y %H:%M}.\n# Counts only: the Dashboard does not release a list of committed families by record number.\n"
       f'SNAP = "{snap.day} {snap:%b %y}"\nPF = {{' + ",\n      ".join(f'"{c}": {{' + ", ".join(f'"{k}": ({v[0]}, {v[1]:.1f})' for k, v in d.items()) + "}" for c, d in pf.items()) + "}\n")
pathlib.Path(__file__).with_name("pending_followup.py").write_text(out); print(out)
