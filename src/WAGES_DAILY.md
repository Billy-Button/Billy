# Wages daily refresh (weekdays)

Changes ONLY the Wages data (src/kpi/daily.py) and the "as at" date. Weekly figures (Occupancy, Pipeline, Tours, KPIs) stay at Friday's close until the Saturday issue.

SQL (Billy Button dashboard run_sql), FROM = '2026-10-01', TO = today + 7 days:

    select r.centre_key, r.shift_date::text, round(r.rostered_minutes/60.0,1) hrs, o.booked
    from semantic_v2.current_owna_roster_day r
    left join semantic_v2.current_owna_occupancy_day o on o.centre_key=r.centre_key and o.occurred_on=r.shift_date
    where r.shift_date between 'FROM' and 'TO' and extract(isodow from r.shift_date) < 6
    order by 1,2

Closed days (e.g. Cup Day 3 Nov) stay in; the screen notes them.

Steps: save rows as JSON -> python3 src/kpi/refresh_daily.py rows.json "<snapshot_completed_at>" -> cd src && BILLY_OUT=/tmp/out python3 billy_build.py.
Checks before publishing: page builds; no Python errors; 'as at <today>' on Wages; South Morang and Craigieburn each have booked children for the latest weekday; heading-for wages within ±25% of forecast; Pipeline/Occupancy/Tours HTML sections identical to yesterday's live page (diff the #perf, #report, #tours sections).
