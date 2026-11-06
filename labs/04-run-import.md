---
layout: default
title: Run the import
lab: 4
time: 20 min
level: ServiceNow
order: 4
permalink: /labs/04-run-import/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>Press the button, then check the box actually filled. "The job ran" and "the data arrived" are two different claims, and this lab makes you prove the second one.</p>
</div>

## Objective

Run the scheduled imports and confirm — with numbers, not vibes — that AWS data created CMDB (Configuration Management Database)
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

The repo ships a verifier that queries the instance over REST and prints a table of counts. You
need the clone from [Lab 0 §4]({{ '/labs/00-prerequisites/' | relative_url }}) — the run command
below assumes
`ServiceNow_ServiceGraph_Lab/` is your working directory:

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
the rows were read from AWS and then dropped by IRE (Identification and Reconciliation
Engine) or by the ETL (Extract, Transform, Load) mapping — that is Lab 5's job.

## 4. Prove the record is real

Open the EC2 CI record and check:

- **Name / object_id** contains your `i-…` instance ID
- **Install Status** and **Operational Status** are populated
- **Discovery source / correlation id** points at the connector, not at "manual"
- The attributes you tagged in Lab 1 (`Environment`, `Owner`, `Application`) appear either on
  the CI or in its attributes/relations

> A CI whose discovery source is `ServiceNow` with no source tag was probably created by hand.
> The whole point of this lab is CIs whose source is the AWS connector.

### Minimum viable success — the exact bar

You are done with this lab when **all four** of these are true. Anything less is not done, and
anything more is optional polish:

<ul class="check">
<li><code>cmdb_ci_ec2_instance</code> has exactly <b>one</b> row whose
<code>object_id</code> equals your AWS instance id <code>i-…</code></li>
<li>That row's <code>discovery_source</code> (or <code>correlation_id</code>/source field on your
release) names the AWS connector — <b>not</b> <code>manual</code>, not empty</li>
<li>The import set run shows <code>Processed</code> with a non-zero row count — a green job with
zero rows is a failure dressed as success</li>
<li>Re-running <b>Execute Now</b> leaves the count at one, not two (proof that identification
works, which Lab 5 explains)</li>
</ul>

If you cannot tick the second item, the data probably did not arrive at all. Check the import
set row count before debugging anything in IRE.

### "Processed with errors" — read this, do not panic

The first run almost always says **Processed with errors**. It is a warning, not a verdict:

| What the error says | Blocks CIs? | What to do |
|---|---|---|
| A field could not be coerced (`invalid reference`, `expected integer`) | No — the CI is still created, that field is blank | Note it; fix in Lab 6 if it matters |
| `missing correlation id` / `no identification attributes` | **Yes** — the row is dropped | This is the case Lab 5 exists for |
| `AccessDenied` on one `Describe*` call | Partially — that resource type is absent, the rest import | Add the action to the policy ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }})) |
| `duplicate key` / `unique constraint` | Yes, for that row | Usually two schedules mapping the same field; check ETL in Lab 6 |

Compare the number of **rows in the import set** with the number of **CIs created**. Equal (or
nearly) means errors were cosmetic. A large gap means rows were dropped and you should open a
row's `Error` field.

## Checkpoint

<ul class="check">
<li>Import sets are <code>Processed</code> (errors are fine — read them)</li>
<li><code>cmdb_ci_ec2_instance</code> contains your instance</li>
<li>The CI shows a connector discovery source, not <code>manual</code></li>
<li>You saved the verifier output for your notes</li>
</ul>

Next: [Lab 5 — read the IRE results]({{ '/labs/05-ire/' | relative_url }})
