# Draft build (preview/ only) — Pipeline tabs: Yesterday · Week · Month

This folder is Cameron's DRAFT of Billy. It builds to preview/index.html only and never to the live index.html.
It differs from src/ by: Pipeline tabs (pipeline_build.py), Wages "So what" lines, Home vision line.

Each weekday morning, after the live Wages refresh:
1. cp src/kpi/daily.py draft/kpi/daily.py (same Wages data as live).
2. Run SQL A and SQL B below on the Billy Button dashboard (run_sql). Save each result as JSON (the bare result, or the saved tool-result file).
3. python3 draft/kpi/pipe_refresh.py events.json first_contact.json "<snapshot_completed_at>"
4. cd draft && BILLY_OUT=/tmp/outd python3 billy_build.py ; python3 pipeline_build.py (prints the day's figures)
5. sed 's/href="icon/href="..\/icon/g' "/tmp/outd/261106 - Billy app - v2.4.html" > preview/index.html ; commit draft/kpi/pipe.py, draft/kpi/daily.py, preview/index.html ; push.

Definitions (back-tested 13 Nov 26: the five days of the week ending 6 Nov sum to the live weekly Pipeline figures for all nine rows at both centres):
- Yesterday = the last working day before the snapshot (weekend and closed days after it are added in and labelled).
- Direction = the day against last week's Mon–Fri total ÷ open days; level when within 0.5. No arrow on Enrolment complete, Started, Lost spots.
- Week = 13 complete Mon–Fri weeks built from the daily events; dashed line = their average = the forecast; green line = target (TGT_W / TGT_M in pipeline_build.py).
- Month = complete months only; dashed line = average of the last three.
- Charts: a bar above max(3 x median, median + 4) runs off the top with its number; the average still counts it. Week x-axis = Friday date under each bar, month beneath.
- First contact in 1 hour = share of the period's enquiries contacted by a person within 60 work minutes (FAST), uncontacted count as misses; target 80%; forecast = pooled share over the window. Work hours 8:30am–5:30pm Mon–Fri (assumption, to review); constants OPEN/CLOSE/CLOSED/FAST in pipeline_build.py.
- Waiting for first contact = no human contact yet AND still at New Enquiry, enquiries of the last 30 days.

## SQL A — events (daily from 1 Apr 26 to yesterday, monthly from Mar 26)
```sql
with enq as (select f.centre_key, (f.enquired_at at time zone 'Australia/Melbourne')::date d, 'enq' k, count(*)::numeric n, 0::numeric x
  from semantic_v2.first_contact f left join semantic_v2.family_stage s on s.family_key=f.family_key left join semantic_v2.family_record_flags r on r.family_key=f.family_key
  where coalesce(s.effective_status,'')<>'rejected' and not coalesce(r.recorded_after_care,false) group by 1,2),
j as (select centre_key, (event_time at time zone 'Australia/Melbourne')::date d, case journey_stage when 'tour_scheduled' then 'ts' when 'tour_completed' then 'tc' when 'offered' then 'of' end k, count(distinct family_key)::numeric n, 0::numeric x
  from semantic_v2.current_journey_event where journey_stage in ('tour_scheduled','tour_completed','offered') group by 1,2,3),
pe as (select centre_key, submitted_on d, 'pe' k, count(*)::numeric n, coalesce(sum(requested_days),0)::numeric x from semantic_v2.owna_enrolment_submission group by 1,2),
ec as (select centre_key, added_on d, 'ec' k, count(*)::numeric n, 0::numeric x from semantic_v2.owna_child_pull where added_on is not null group by 1,2),
st as (select centre_key, active_from d, 'st' k, sum(booked_days_per_week)::numeric n, count(*)::numeric x from semantic_v2.owna_child_place where not finish_before_start group by 1,2),
lo as (select centre_key, finish_date d, 'lo' k, sum(booked_days_per_week)::numeric n, count(*)::numeric x from semantic_v2.owna_child_place where finish_kind='withdrawal' group by 1,2),
u as (select centre_key,d,k,n,x from enq union all select centre_key,d,k,n,x from j union all select centre_key,d,k,n,x from pe union all select centre_key,d,k,n,x from ec union all select centre_key,d,k,n,x from st union all select centre_key,d,k,n,x from lo),
mm as (select 'enq' k, centre_key, month m, enquiries::numeric v, 0::numeric x from semantic_v2.enquiry_month where not bulk_import and month>='2026-03'
union all select 'ts', centre_key, month, families_tour_booked::numeric, 0 from semantic_v2.tour_month where month>='2026-03'
union all select 'tc', centre_key, month, tours_completed::numeric, 0 from semantic_v2.tour_month where month>='2026-03'
union all select 'of', centre_key, to_char(event_time at time zone 'Australia/Melbourne','YYYY-MM'), count(distinct family_key)::numeric, 0 from semantic_v2.current_journey_event where journey_stage='offered' and event_time>=timestamptz '2026-03-01 00:00+11' group by 2,3
union all select 'pe', centre_key, to_char(submitted_on,'YYYY-MM'), count(*)::numeric, 0 from semantic_v2.owna_enrolment_submission where submitted_on>=date '2026-03-01' group by 2,3
union all select 'ec', centre_key, to_char(added_on,'YYYY-MM'), count(*)::numeric, 0 from semantic_v2.owna_child_pull where added_on>=date '2026-03-01' group by 2,3
union all select 'st', centre_key, month, new_children_spots::numeric, new_children::numeric from semantic_v2.owna_spot_movement where month>='2026-03'
union all select 'lo', centre_key, month, left_spots::numeric, left_children::numeric from semantic_v2.owna_spot_movement where month>='2026-03')
select 'D' g, u.centre_key c, u.d::text p, u.k, u.n, u.x from u where u.d between date '2026-04-01' and (now() at time zone 'Australia/Melbourne')::date - 1 and u.centre_key is not null
union all select 'M', mm.centre_key, mm.m, mm.k, mm.v, mm.x from mm where mm.centre_key is not null
order by 1,2,3,4
```
## SQL B — first contact
```sql
select f.centre_key c, to_char(f.enquired_at at time zone 'Australia/Melbourne','YYYY-MM-DD HH24:MI') e, to_char(f.first_contact_at at time zone 'Australia/Melbourne','YYYY-MM-DD HH24:MI') t, coalesce(s.effective_status,'') s
from semantic_v2.first_contact f left join semantic_v2.family_stage s on s.family_key=f.family_key left join semantic_v2.family_record_flags r on r.family_key=f.family_key
where f.enquired_at >= timestamptz '2025-10-01 00:00+11' and f.centre_key is not null and coalesce(s.effective_status,'')<>'rejected' and not coalesce(r.recorded_after_care,false)
order by 1,2
```
