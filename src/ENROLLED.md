# Enrolled occupancy (headline occupancy, as Owna shows it)

Definition (agreed by Cameron 16 Nov 26): booked days a week of every child currently enrolled in Owna,
including children not yet started, plus casual days booked in the last full Mon-Fri week,
divided by licensed places x 5. Point in time, one decimal. Places: South Morang 108, Craigieburn 174.

Refresh each weekday. Save each result as JSON, then from src:
  python3 kpi/enrolled_refresh.py enrolled.json casual.json "<snapshot_completed_at>" "<Mon d-Fri d Mon of last full week, e.g. 9-13 Nov>"

enrolled.json:

    select centre_key, count(*) children, sum(booked_days_per_week) spots,
     count(*) filter (where active_from > current_date) ns_children,
     sum(case when active_from > current_date then booked_days_per_week else 0 end) ns_spots,
     current_date as_at
    from semantic_v2.owna_child where attending group by 1

casual.json (last full Monday to Friday before today):

    select centre_key, sum(casual) cas from semantic_v2.current_owna_occupancy_day
    where occurred_on between date '<last Monday>' and date '<last Friday>' group by 1
