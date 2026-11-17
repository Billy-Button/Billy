# Rewrite kpi/enq_source.json. Usage (from src): python3 kpi/enq_source_refresh.py rows.json "<snapshot_completed_at>"
import json, sys, pathlib
d = json.load(open(sys.argv[1])); cols = d.get("columns"); rows = d.get("rows", d)
if cols: rows = [dict(zip(cols, r)) for r in rows]
out = {"snap": sys.argv[2][:19] + "+11:00", "rows": [[r["centre_key"], r["month"], r["source"], int(r["enquiries"])] for r in rows]}
assert {r[0] for r in out["rows"]} == {"South Morang", "Craigieburn"}
pathlib.Path(__file__).with_name("enq_source.json").write_text(json.dumps(out)); print(len(out["rows"]), "rows")
