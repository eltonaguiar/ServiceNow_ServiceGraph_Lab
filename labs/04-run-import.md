---
layout: default
title: Run the import
lab: 4
time: 20 min
level: ServiceNow
order: 4
permalink: /labs/04-run-import/
---

## Objective

Run the scheduled imports and confirm — with numbers, not vibes — that AWS data created CMDB
records.

## 1. Find the schedules

Filter Navigator → **Service Graph Connector for AWS → Scheduled Imports** (or **Schedules**
inside the app's menu, or the same list surfaced in SGC Central).

You will see several, typically:

| Schedule | What it loads |
|---|---|
| Organization / Account | `cmdb_ci_cloud_service_account`, AWS account metadata |
| Hardware | EC2 instances, and usually VPCs and related network CIs |
| Software (if present) | installed software via SSM inventory — optional |

## 2. Execute them

Use **Execute Now** on Organization first, then Hardware. Do not wait for the cron.

Then watch the plumbing, in this order:

1. **AWS → Import Sets** (or `System Import Sets → Import Sets`) — a new set per run with
   `State: Processed` or `Processed with errors`.
2. **Concurrent Import Sets** (`/sys_import_set_run_list.do`) — the run-level log.
3. The CI list itself: **Configuration → CMDB → CI → Hardware** or the direct table
   `cmdb_ci_ec2_instance`.

## 3. Verify with numbers

The repo ships a verifier that queries the instance over REST and prints a table of counts:

```bash
export SN_INSTANCE="dev123456"
export SN_USER="admin"
export SN_PASS="your-pdi-password"
python3 scripts/verify_cmdb.py
```

Expected shape after a successful first import (your counts vary):

```
table                            count
cmdb_ci_cloud_service_account        1
cmdb_ci_ec2_instance                 1
cmdb_ci_vpc                          1
```

If the verifier shows `0` for `cmdb_ci_ec2_instance` while the import set says *Processed*,
the rows were read from AWS and then dropped by IRE or by the ETL mapping — that is Lab 5's job.

## 4. Prove the record is real

Open the EC2 CI record and check:

- **Name / object_id** contains your `i-…` instance ID
- **Install Status** and **Operational Status** are populated
- **Discovery source / correlation id** points at the connector, not at "manual"
- The attributes you tagged in Lab 1 (`Environment`, `Owner`, `Application`) appear either on
  the CI or in its attributes/relations

> A CI whose discovery source is `ServiceNow` with no source tag was probably created by hand.
> The whole point of this lab is CIs whose source is the AWS connector.

## Checkpoint

<ul class="check">
<li>Import sets are <code>Processed</code> (errors are fine — read them)</li>
<li><code>cmdb_ci_ec2_instance</code> contains your instance</li>
<li>The CI shows a connector discovery source, not <code>manual</code></li>
<li>You saved the verifier output for your notes</li>
</ul>

Next: [Lab 5 — read the IRE results]({{ '/labs/05-ire/' | relative_url }})
