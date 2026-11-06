---
layout: default
title: Drift and monitoring
lab: 9
time: 25 min
level: Operations
order: 9
permalink: /labs/09-drift-monitoring/
---

## Objective

Make the cloud change and watch the CMDB react. A CMDB that only ever grows is a liability;
the value is in drift.

## 1. Drift on purpose

1. In AWS, **change** the instance: retag it (`Environment: prod`), or better, **terminate** it
   and launch a replacement with a different instance ID.
2. Run the hardware import again.
3. Observe in ServiceNow:

| Change in AWS | Expected CMDB behaviour |
|---|---|
| Retag `Environment` | CI updated, IRE outcome **Updated** |
| Instance type changed | CI updated on the mapped field from Lab 6 |
| Instance terminated | Depends on connector config: CI marked **retired/absent**, or left untouched (stale) — check and note which |
| Replacement instance launched | **New** CI inserted; the old one does not disappear unless lifecycle handling is configured |

The "terminated instance" row is the classic gap: discovery tools see what exists, not what
vanished. Note what your release does, because that is the first thing an auditor asks.

## 2. Prove staleness is detectable

Query for CIs that the connector has not touched recently:

```sql
-- CMDB CI list, filter: last_discovered older than 7 days AND discovery_source = AWS
```

Save that filter. In production it is the report that catches a broken connector before a
month of wrong data accumulates.

## 3. Monitor the connection

- **SGC Central** (newer releases) shows each connection's last run, duration and error count.
- Otherwise, watch the scheduled job: **System Scheduler → Scheduled Jobs → AWS …** — check
  **Last run**, **Next run**, and the run's log for non-zero failures.
- Check **Import Sets** for rows with `State: Processed with errors` and read the transform
  errors; a single bad payload doesn't stop the run, which is why it goes unnoticed.

## 4. Automate the check

```bash
python3 scripts/verify_cmdb.py --stale-days 7
```

Exits non-zero when the expected tables are empty or stale — put it on a cron and you have a
crude but honest freshness monitor.

## Checkpoint

<ul class="check">
<li>You produced at least one real drift event and can describe the CMDB response</li>
<li>You have a saved filter for connector-stale CIs</li>
<li>You know where the connection's run history lives on your release</li>
</ul>

Next: [Lab 10 — troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }})
