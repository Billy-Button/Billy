# Rewrite kpi/funnel.json. Usage (from src): python3 kpi/funnel_refresh.py rows.json "<snapshot_completed_at>"
import json, sys, pathlib
d = json.load(open(sys.argv[1])); cols = d.get("columns"); rows = d.get("rows", d)
if cols: rows = [dict(zip(cols, r)) for r in rows]
out = {"snap": sys.argv[2][:19] + "+11:00", "rows": [[r["centre_key"], r["month"], int(r["enq"]), int(r["tb"]), int(r["tr"]), int(r["fp"]), int(r["ec"]), int(r["st"]), bool(r["conv"])] for r in rows]}
assert {r[0] for r in out["rows"]} == {"South Morang", "Craigieburn"}
pathlib.Path(__file__).with_name("funnel.json").write_text(json.dumps(out)); print(len(out["rows"]), "rows")
