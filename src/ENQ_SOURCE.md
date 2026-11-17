# Enquiries by contact type (home Enquiries card table)

As LineLeader records it (Phone, Web, Walk-in, Link, Other, Not recorded): contact type only, not marketing source.
Refresh each weekday: run this, save as JSON, then from src: python3 kpi/enq_source_refresh.py rows.json "<snapshot_completed_at>"

    select centre_key, month, source, enquiries from semantic_v2.pipeline_enquiry_month
    where month >= to_char(current_date - interval '6 months', 'YYYY-MM') order by 1,2,3
