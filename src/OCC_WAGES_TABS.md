# Occupancy and Wages tabs (live from 13 Nov 26): data pull for kpi/occ.py
python3 kpi/occ_refresh.py days.json "<snapshot_completed_at>"
```sql
select coalesce(o.centre_key, r.centre_key) c, coalesce(o.occurred_on, r.shift_date)::text d, o.booked b, o.attended a, o.casual k, round(r.rostered_minutes/60.0,1) h, r.staff_rostered s, o.attended_minutes am, o.distinct_children dc
from semantic_v2.current_owna_occupancy_day o full join semantic_v2.current_owna_roster_day r on r.centre_key=o.centre_key and r.shift_date=o.occurred_on
where coalesce(o.occurred_on, r.shift_date) between date '2025-01-01' and (now() at time zone 'Australia/Melbourne')::date - 1 and coalesce(o.centre_key, r.centre_key) is not null
order by 1,2
```
