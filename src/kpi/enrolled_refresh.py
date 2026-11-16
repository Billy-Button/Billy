# Rewrite kpi/enrolled.py. Usage (from src): python3 kpi/enrolled_refresh.py enrolled.json casual.json "<snapshot_completed_at>" "<casual week label, e.g. 16-20 Nov>"
import json, sys, pathlib
def rows(p):
    d = json.load(open(p)); cols = d.get("columns"); r = d.get("rows", d)
    return [dict(zip(cols, x)) for x in r] if cols else r
e, c, snap, wk = rows(sys.argv[1]), rows(sys.argv[2]), sys.argv[3], sys.argv[4]
E = {x["centre_key"]: (int(x["children"]), float(x["spots"]), int(x["ns_children"]), float(x["ns_spots"])) for x in e}
CAS = {x["centre_key"]: int(float(x["cas"] or 0)) for x in c}
assert set(E) == {"South Morang", "Craigieburn"} and set(CAS) == set(E), (E, CAS)
as_at = e[0]["as_at"]
out = f'''# Enrolled occupancy: every current Owna enrolment (attending), including children not yet started.
# Source: semantic_v2.owna_child where attending. Refresh with the SQL in ENROLLED.md.
SNAP = "{snap[:19]}+11:00"
AS_AT = "{as_at}"
# centre: (children, booked spots a week, not-yet-started children, their spots)
E = {E!r}
# casual days booked in the last full week (Mon-Fri), current_owna_occupancy_day.casual
CAS_WEEK = "{wk}"
CAS = {CAS!r}
'''
pathlib.Path(__file__).with_name("enrolled.py").write_text(out); print(out)
