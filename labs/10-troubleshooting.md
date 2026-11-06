---
layout: default
title: Troubleshooting
lab: 10
time: reference
level: Reference
order: 10
permalink: /labs/10-troubleshooting/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>A ladder, not a guess. Each rung rules out a whole layer, so you never debug the same problem twice: is the instance awake, is the app installed, do the credentials work, did the job run, did rows arrive, did they map, did IRE accept them, do the records look right?</p>
</div>

## The failure ladder

Work top to bottom. Each rung eliminates a whole layer, so you never debug the same problem
twice.

| # | Check | Where | Green means |
|---|---|---|---|
| 1 | Does the PDI work at all? | Log in, open a list | Instance awake and healthy |
| 2 | Does the app exist and install? | System Applications | Connector present |
| 3 | Does the connection test pass? | Guided Setup / SGC Central | Credentials + network + IAM fine |
| 4 | Did the schedule run? | Scheduled Jobs, SGC Central | The job executed |
| 5 | Did rows arrive? | Import Sets (`sys_import_set_row_list.do`) | The REST call returned data |
| 6 | Did rows transform? | Import set → errors per row | Mapping works |
| 7 | Did IRE accept them? | `cmdb_ire_output_item` | Records inserted/updated |
| 8 | Do the CIs look right? | `cmdb_ci_ec2_instance` | Field mappings correct |

## Common failures, in the order you will hit them

**The app is not in the list.**
PDI releases differ, and Store apps can require entitlement. Use the
[IRE REST fallback]({{ '/labs/fallback-ire-api/' | relative_url }}) — you still learn
identification, ETL-equivalent field mapping and relationships.

**Install fails on a dependency.**
Install dependencies one at a time (Integration Commons for CMDB first), reload the UI between
attempts, then retry the connector. A partially installed dependency leaves the instance in a
confusing state, so check **System Applications → Installed** for half-finished entries.

**`InvalidClientTokenId` / `SignatureDoesNotMatch`.**
Bad key or secret. Recreate the access key and paste the secret fresh — trailing whitespace
from a copied block is the most common cause.

**`AccessDenied` on a specific action.**
The read-only policy is missing an action. Read the action name from the import set error and
add it, or use managed `ReadOnlyAccess` in the lab and narrow later.

**Import set processes, zero CIs appear.**
Rows read, then dropped. Look at the import set row's `Error` field and at
`cmdb_ire_output_item` for rejection reasons. Frequently: an empty identifier (so IRE cannot
match or create), or a reference to a parent CI that does not exist.

**CIs duplicate on every run.**
Identification (IRE — Identification and Reconciliation Engine) is not matching. Check the class's identification rule and confirm the payload
really carries the identifier attribute; the connector may be mapping a display name but not
the instance ID.

**Schedule says "Error" with no rows.**
Usually egress: the instance cannot reach `*.amazonaws.com`, or a proxy intercepts TLS. Test
with **System Diagnostics → Outbound REST** (or a REST test step) against a simple AWS
endpoint.

**Everything worked yesterday.**
PDI hibernated, woke with a different hostname, or the credentials record was invalidated. Wake
it, re-test the connection, re-run the schedule. This is the most common "regression" in this
lab.

**Azure: `AuthorizationFailed`.**
The service principal lacks **Reader** at the subscription scope, or you assigned the role to
the app *registration object* instead of the **Enterprise Application** service principal.

**Multisource: values flip between imports.**
Two sources update the same attribute with no precedence. Set an explicit reconciliation rule
in CI Class Manager rather than letting source order decide.

## Diagnostic queries

```text
-- IRE outcomes, last 24h
cmdb_ire_output_item.list  (filter: sys_created_on > yesterday)

-- connector-created CIs
cmdb_ci_ec2_instance.list  (filter: discovery_source contains AWS)

-- failed import rows
sys_import_set_row_list.do  (filter: error is not empty)
```

## Checkpoint

<ul class="check">
<li>You can place any failure on the ladder before opening a log</li>
<li>You know which table proves "rows arrived" versus "CIs created"</li>
</ul>

Next: [Lab 11 — cleanup]({{ '/labs/11-cleanup/' | relative_url }})
