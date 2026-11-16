# Enrolled occupancy (headline occupancy)

Definition (agreed by Cameron 16 Nov 26): booked days a week of every child currently enrolled in Owna,
including children not yet started, divided by licensed places x 5. Point in time, one decimal.
Places: South Morang 108, Craigieburn 174. Plus casual days booked in the last full week (see below).

Refresh each weekday: run this and rewrite kpi/enrolled.py (SNAP = snapshot_completed_at, AS_AT = as_at).

    select centre_key, count(*) children, sum(booked_days_per_week) spots,
     count(*) filter (where active_from > current_date) ns_children,
     sum(case when active_from > current_date then booked_days_per_week else 0 end) ns_spots,
     current_date as_at
    from semantic_v2.owna_child where attending group by 1

Casuals (added 16 Nov at Cameron's request): casual days booked in the last full Mon-Fri week.
Rewrite CAS and CAS_WEEK in kpi/enrolled.py from:

    select centre_key, sum(casual) cas from semantic_v2.current_owna_occupancy_day
    where occurred_on between <last Monday> and <last Friday> group by 1
