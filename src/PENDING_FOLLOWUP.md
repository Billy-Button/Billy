# Pending records to update in Owna (Pipeline summary)

Families with an Owna form in whose start date has passed with no start, who have no start date, or who have no days requested. The Base Case counts them as nil until the office updates them in Owna.

Refresh (weekday refresh and Saturday issue):

```sql
select p.centre_key, p.expected_start_month, p.families, p.pulled, p.days_requested, p.days_booked
from semantic_v2.pipeline_committed p order by 1, 2
```

Save the result rows as JSON (a list of rows in that column order), then from src:
`python3 kpi/pending_refresh.py rows.json "<snapshot_completed_at>"`

Rules: past = expected_start_month 'past'; no date = 'no date'; no days = a dated month with days_requested 0. Counts only; the Dashboard gives no list by record number (to come from Dima).
