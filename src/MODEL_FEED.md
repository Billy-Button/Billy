# Financial Model feed in the Billy app

- `kpi/model_feed.json` is a copy of the project doc `claude/model/billy-feed.json`. Every Base Case, Forecast, Target, pending and wage plan figure the app shows comes from it. The app calculates none of them.
- `kpi/model_register.json` holds the version named in `claude/model/model-register.md`. If it differs from the feed's version, every model screen hides its figures and shows "Model update pending".
- Refresh: read the register. If it names a later version than `kpi/model_feed.json`, set `kpi/model_register.json` "version" to the register's version (so the app shows "Model update pending") and tell Cameron. Do not copy a new feed in without Cameron's approval: a new feed may change field names and must be checked by Claude in the app chat.
- Profit, budget and the CAAE loan are owner-only. They stay off the app until there is hosting with sign-in.
