# Enrolled occupancy: every current Owna enrolment (attending), including children not yet started.
# Source: semantic_v2.owna_child where attending. Refresh with the SQL in ENROLLED.md.
SNAP = "2026-11-24T03:08:33+11:00"
AS_AT = "2026-11-24"
# centre: (children, booked spots a week, not-yet-started children, their spots)
E = {'Craigieburn': (106, 314.0, 3, 6.0), 'South Morang': (151, 425.0, 4, 11.0)}
# casual days booked in the last full week (Mon-Fri), current_owna_occupancy_day.casual
CAS_WEEK = "16-20 Nov"
CAS = {'South Morang': 13, 'Craigieburn': 8}
