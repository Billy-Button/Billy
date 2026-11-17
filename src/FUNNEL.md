# Pipeline: what each month's enquiries became (home Pipeline card, More)

Refresh each weekday: run this, save as JSON, then from src: python3 kpi/funnel_refresh.py rows.json "<snapshot_completed_at>"

    select centre_key, month, sum(enquiries) enq, sum(tour_booked) tb, sum(toured) tr, sum(form_paid) fp,
     sum(enrolment_complete) ec, sum(started) st, bool_or(still_converting) conv
    from semantic_v2.pipeline_enquiry_month
    where month >= to_char(current_date - interval '6 months', 'YYYY-MM') group by 1,2 order by 1,2

Wages detail (kpi/wage_drivers.json and kpi/w2r_xero.py) is monthly: Claude updates it when a month closes in Xero.
