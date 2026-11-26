# Enrolled occupancy: every current Owna enrolment (attending), including children not yet started.
# Source: semantic_v2.owna_child where attending. Refresh with the SQL in ENROLLED.md.
SNAP = "2026-11-27T03:07:39+11:00"
AS_AT = "2026-11-27"
# centre: (children, booked spots a week, not-yet-started children, their spots)
E = {'Craigieburn': (106, 314.0, 3, 6.0), 'South Morang': (152, 428.0, 5, 14.0)}
# casual days booked in the last full week (Mon-Fri), current_owna_occupancy_day.casual
CAS_WEEK = "16-20 Nov"
CAS = {'South Morang': 13, 'Craigieburn': 8}
