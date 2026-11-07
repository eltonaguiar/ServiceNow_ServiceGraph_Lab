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

## The first 60 minutes — the four failures that stop most people

If you have read nothing else on this page, read this table. These four account for almost every
"the lab does not work" message, and none of them is a bug.

| What happened | Almost always means | Fix | Where |
|---|---|---|---|
| The instance URL stopped resolving / XML error page | PDI hibernated | Wake it at developer.servicenow.com, re-check the URL, re-test the connection | [Lab 0]({{ '/labs/00-prerequisites/' | relative_url }}) |
| App listed, **Install greyed out** or entitlement error | PDI not licensed for the Store app | Take the fallback path, do not keep retrying | [Lab 12]({{ '/labs/fallback-ire-api/' | relative_url }}) |
| Connection test fails with `AccessDenied` | Policy not attached, or attached to a different IAM user | Compare the policy attached to the *user that owns the key* | [Lab 3]({{ '/labs/03-iam-connection/' | relative_url }}) |
| Import set says **Processed**, **zero inserts**, zero CIs in the list you expect | Often wrong table, dependency partial, or ran schedules out of order | Check `cmdb_ci_network` for VPC; `cmdb_ire_partial_payloads`; datacenter CI for region | [Lab 4]({{ '/labs/04-run-import/' | relative_url }}) / [Lab 5]({{ '/labs/05-ire/' | relative_url }}) |
| Concurrent job stuck in **Pending** | Queued work — not a reason to Execute Now again | Wait, refresh **Concurrent Import Set Jobs** tab | [Lab 4 §2]({{ '/labs/04-run-import/' | relative_url }}) |
| Import set says **Processed with errors**, zero CIs | Rows read then dropped — no identifier, or wrong discovery source | Open a row's `Error` / **Comments**, then `cmdb_ire_output_item` | [Lab 4]({{ '/labs/04-run-import/' | relative_url }}) / [Lab 5]({{ '/labs/05-ire/' | relative_url }}) |

Everything below is the same material in diagnostic order, for when the table above does not
match your symptom.

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
| 8 | Do the CIs look right? | `cmdb_ci_vm_instance` (AWS EC2) | Field mappings correct |

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

**Import set processes, zero CIs appear (or Processed with zero Inserts).**
Rows read, then dropped or parked. Check, in order:

1. Are you on the **right class**? Verified VPC lands in **`cmdb_ci_network`**, not `cmdb_ci_vpc`.
2. Import set row **Comments** (partial/warning is not success).
3. `cmdb_ire_partial_payloads` for `MISSING_MATCHING_ATTRIBUTES` (common when datacenter/region CI is missing).
4. `cmdb_ire_output_item` for hard rejections.

Frequently: parent CI missing (run **`SG-AWS-Datacenters`** before **`SG-AWS-VPC`**), or an empty identifier.

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

## "Processed" and "Processed with errors" — which signals matter

This is the single most misread part of the lab. Schedule state and even **Processed** row counts
are coarse. **Inserts** on Transform Histories and the **target CI list** are what prove success.

| Signal | CIs lost? | Action |
|---|---|---|
| **Processed** with **0 Inserts** and empty target list | **Yes** for that pass — often dependency partial | See `cmdb_ire_partial_payloads`; fix schedule order (Lab 4) |
| Row Comment = partial / warning | **Yes** until rerun after dependency fixed | Do not treat as success |
| Type coercion (`invalid integer`, `invalid reference`, date parse) | No — CI may still be created, field blank | Cosmetic; Lab 6 if the field matters |
| Missing identifier / no matching identification rule | **Yes** — row skipped by IRE | `cmdb_ire_output_item` |
| `AccessDenied` on a `Describe*` | Partial — that resource type missing | Lab 3 policy — absence of credential errors elsewhere is **not** proof IAM is complete |
| Duplicate/unique constraint | Yes, for that row | Inspect ETL / two schedules on same class |

Rule of thumb: **compare source row count, Inserts/Updates, and the CI list for the correct class.**
Do **not** assume "errors are almost always fine" or that **Processed** alone proves data landed.

## Navigation paths move between releases

Every menu path in this lab is release-dependent. When a path does not exist, use the table name
in the Filter Navigator instead — tables are far more stable than menus:

| You want | Type this in the Filter Navigator |
|---|---|
| Import set runs | `sys_import_set_run_list.do` |
| Import set rows + errors | `sys_import_set_row_list.do` |
| IRE outcomes | `cmdb_ire_output_item_list.do` |
| IRE partial / dependency payloads | `cmdb_ire_partial_payloads_list.do` |
| Cloud Networks (VPC on verified path) | `cmdb_ci_network_list.do` |
| AWS Datacenters | `cmdb_ci_aws_datacenter_list.do` |
| IRE rule hits | `cmdb_ire_output_rule_list.do` |
| AWS EC2 via SGC | `cmdb_ci_vm_instance_list.do` |
| `cmdb_ci_ec2_instance` | Other sources; often empty on this connector path |
| Subnets (verified path) | `cmdb_ci_cloud_subnet_list.do` |
| Compute security groups | `cmdb_ci_compute_security_group_list.do` |
| Store apps / plugins | `sys_store_app_list.do` / `v_plugin_list.do` |
| Scheduled jobs | `sysauto_script_list.do` (or `sys_trigger_list.do` for triggers) |
| Multisource CI view | `cmdb_ci_list.do`, then open a record's **CMDB 360** tab |

## Diagnostic queries

```text
-- IRE outcomes, last 24h
cmdb_ire_output_item.list  (filter: sys_created_on > yesterday)

-- connector-created CIs
cmdb_ci_vm_instance.list   (filter: name or object_id contains i-)
cmdb_ci_cloud_subnet.list
cmdb_ci_compute_security_group.list

-- failed import rows
sys_import_set_row_list.do  (filter: error is not empty)
```

## Checkpoint

<ul class="check">
<li>You can place any failure on the ladder before opening a log</li>
<li>You know which table proves "rows arrived" versus "CIs created"</li>
</ul>

Next: [Lab 11 — cleanup]({{ '/labs/11-cleanup/' | relative_url }})
