# Enrolled occupancy: every current Owna enrolment (attending), including children not yet started.
# Source: semantic_v2.owna_child where attending. Refresh with the SQL in ENROLLED.md.
SNAP = "2026-11-19T03:09:21+11:00"
AS_AT = "2026-11-19"
# centre: (children, booked spots a week, not-yet-started children, their spots)
E = {'Craigieburn': (106, 317.0, 4, 7.0), 'South Morang': (152, 427.0, 4, 11.0)}
# casual days booked in the last full week (Mon-Fri), current_owna_occupancy_day.casual
CAS_WEEK = "9-13 Nov"
CAS = {'South Morang': 9, 'Craigieburn': 7}
