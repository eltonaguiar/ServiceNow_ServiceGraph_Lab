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

## Case study — "2 NIC, 1 volume, 3 relationships, all `MISSING_DEPENDENCY`"
{: #lab10-missing-dependency}

A real investigation on `dev296154` (Australia, Oct–Nov 2026) — and note that **following the Lab 4 PoC order reproduces a milder version of it on purpose**, because that path skips `SG-AWS-Network-Interface` (140) and never runs `SG-AWS-Storage-Volume` (160). If you landed here from [Lab 4 §9]({{ '/labs/04-run-import/' | relative_url }}#lab4-partial-dependencies), start with the fast path and use this case only to see the deeper failure. EC2 imports kept finishing
**complete** with 0 errors, yet every run produced the same 6 partial entries: `cmdb_ci_nic` (2),
`cmdb_ci_storage_volume` (1), `cmdb_rel_ci` (3) — while the VM itself updated fine, tags included.
Nothing was broken in the mapping. Read the blocks below in order: what happened, the fast
path, the queries, and what the platform's AI can (and cannot) do here.

<details markdown="1">
<summary><strong>Case study — why the warnings were correct, and what actually caused them</strong></summary>

**Symptoms.** `SG-AWS-EC2` updated VM `sgclab-app-01` (`i-0c9860cc1569c41a4`) every run —
`Environment` tag cycled `lab → drift-test → lab` in `cmdb_key_value` — but the run always left
6 partials. `cmdb_ci_nic` was empty. `cmdb_ci_storage_volume` held 7 records, all
`discovery_source = ServiceNow` (drive letters, `/dev/nvme0n1p1`), all with blank **Object ID** —
Mid Server disk discovery, nothing from AWS.

**The trap.** The EC2 mapping's `Cloud Mgmt Network Interface 1/2` and `Storage Volume 1` have
blank **Object ID** and **Public IP** mappings. That looks exactly like a half-filled ETL mapping.
It is not. Those entities are **reference stubs**, by design:

| Entity in `SG-AWS-EC2-Instance` (def `64c89952…`) | Fields it maps |
|---|---|
| `Cloud Mgmt Network Interface 1` | `source_native_key`, `cmdb_ci` |
| `Cloud Mgmt Network Interface 2` | `source_native_key` |
| `Storage Volume 1` | `source_native_key` |

The authoritative attributes live in the **prerequisite** feeds, not in EC2:

| Prerequisite mapping | Fields on the same class |
|---|---|
| `SG-AWS-Network-Interface` (def `57a39282…`) | `object_id`, `name`, `private_ip`, `public_ip`, `private_dns`, `public_dns`, `ip_address`, `state`, … |
| `SG-AWS-Storage-Volume` (def `9936cf02…`) | `object_id`, `volume_id`, `size`, `storage_type`, `name`, `state`, … |

Both CI classes use a **dependent** identifier (`cmdb_identifier.independent = false`), so a stub
carrying only `discovery_source` + a source key cannot mint a CI. It can only *link* to one that
already exists.

**Why the dependents could not resolve.** The prerequisites were configured and active, but
non-productive:

| Import | `run_type` | order | Execution history | Rows loaded |
|---|---|---|---|---|
| `SG-AWS-Network-Interface` | parent | 140 | 1 run, `CEX0001013` (07:00:31) | **0** |
| `SG-AWS-Storage-Volume` | parent | 160 | **none, ever** | **0** |
| `SG-AWS-EC2` | parent | 180 | 5 runs, all `complete` | 5 pages |

All three are children of `SG-AWS-Organization`, which is **inactive** — so they never run on a
schedule, and a manual *Execute Now* on EC2 runs **only EC2**. The 140 → 160 → 180 ordering exists
precisely so EC2 finds its prerequisites already populated.

**Proof that the resources were seen.** The EC2 staging table had 5 rows and every one contained
`eni-04843cac6d5784192` and `vol-0d78f1f1bebee052f`, so AWS data was reaching the instance. The
NIC feed's table had **0 rows**. `sys_object_source` held keys only for the CIs that *were* created
— `…|VNICEndpoint|…`, `…|StorageMapping|…`, `…|BlockEndpoint|…` — and no plain
`…|639051062568|us-east-2|eni-04843…` key, i.e. no NIC ever came into existence.

**Verdict.** Not a mapping defect. A missing dependency in the literal sense: the prerequisite
feeds never produced the CIs the EC2 stubs point at. Fix the prerequisites, not the mapping.

</details>

<details markdown="1">
<summary><strong>Fast path — the 20-minute version of this investigation</strong></summary>

Work in this order. Stop at the first rung that fails; you will usually finish at step 3.

1. **List every import with the same parent.** Filter Navigator → `scheduled_import_set_list.do`,
   group by **Parent**. You are looking for ordered siblings (140, 160, 180) — the lower order
   numbers are prerequisites by design, not coincidence.
2. **Read the execution history, not the schedule.** `sn_cmdb_int_util_cmdb_integration_execution_list.do`
   (`CEX…`). `state = complete` with **rows = 0** is the single most decisive signal on this
   connector: the job ran and AWS returned nothing. Zero execution records means it never ran.
   (A second run showing `rows = 0` again only proves it recurs — capture the loader's response
   before re-running if you need to name a cause. See *Approval lanes* in `SOLVED_FREEBUFF.MD`.)
3. **Confirm the staging tables.** `sn_aws_integ_sg_aws_network_interface_list.do`,
   `sn_aws_integ_sg_aws_storage_volume_list.do`, `sn_aws_integ_sg_aws_ec2_list.do`. If EC2's table
   contains the resource and the prerequisite's table is empty, the cause is upstream of mapping.
4. **Confirm the target CIs.** `cmdb_ci_nic_list.do`, `cmdb_ci_storage_volume_list.do` — and read
   `discovery_source` and `object_id`, never just the row count. Seven volumes that are all
   `ServiceNow` + blank `object_id` are *not* your AWS volume.
5. **Check `sys_object_source` for the exact key** you expect (`…|<account>|<region>|<resource-id>`).
   Present = the CI exists. Absent = it was never created, whatever the logs say.
6. **Only now open the partial payload** — `cmdb_ire_partial_payloads_list.do`. It tells you the
   *shape* of the failure (`MISSING_DEPENDENCY`, values stripped to `discovery_source`) but it will
   not tell you *which* prerequisite is missing. Steps 1–3 answer that.

**Rules that save the most time**

- A blank **Object ID** in a reference-only entity is not a bug. Check whether the entity maps
  attributes *at all* before calling it a defect.
- Never create a duplicate scheduled import because a name "looks missing". Confirm against
  `scheduled_import_set` by name **and** by `sys_id` first.
- Do not reprocess partials or manually create CIs to "unblock" a run. Both destroy the evidence
  and neither fixes the cause.
- Run the chain in order (140 → 160 → 180) and re-check `ire_partial` on the next EC2 execution.
  That number going 6 → 0 is the acceptance test.
- Verify what actually ran: `process`/`complete` is not the same as `rows > 0`, and
  **Processed** with zero inserts is not success.

</details>

<details markdown="1">
<summary><strong>Copy-paste table reference for this failure class</strong></summary>

| Question | Table / list | Notes |
|---|---|---|
| Which imports exist, in what order, under which parent? | `scheduled_import_set_list.do` | `active`, `run_type = parent`, `order` |
| Did it run, and did it fetch anything? | `sn_cmdb_int_util_cmdb_integration_execution_list.do` | `CEX…`; watch `rows`, `ire_partial`, `errors` |
| What landed in staging? | `sn_aws_integ_sg_aws_*_list.do` | one row = one JSON page, not one CI |
| Transform history | `sys_import_set_run_list.do` | `TH…`; on this connector `sys_transform_map` is blank and `sys_robust_transformer` is set |
| The mapping itself | `sys_robust_import_set_transformer` → `robust_transform_engine` → `sys_rte_definition` → `sys_rte_eb_entity` / `sys_rte_eb_field` | classic `sys_transform_entry` does **not** apply |
| Where the warning is stored | `cmdb_ire_partial_payloads_list.do` | field `payload_item` holds the JSON |
| Does the CI actually exist for a key? | `sys_object_source_list.do` | field `id` = `source_native_key` |
| Can this class be created by a stub? | `cmdb_identifier_list.do` | `independent = false` → dependent |
| Does the data source exist under another name? | `sys_data_source_list.do`, filter `name LIKE SG-AWS` | compare `import_set_table_name` |

**Reading the payload.** `values` containing only `discovery_source`, plus
`"reason": "MISSING_DEPENDENCY"`, plus a `referenceItems` entry pointing at an id that appears in
no `items[]` list — that combination means "this item was emitted as a link target and could not
be matched". The dangling id is a **symptom**: it changes on every run, and in runs where it *did*
point at the VM's own `internal_id` the NIC still failed. Do not chase it.

</details>

<details markdown="1">
<summary><strong>What ServiceNow's own AI and diagnostics can — and cannot — do here</strong></summary>

Be realistic about the split. On this failure the decisive evidence was **four counts across four
tables**; no product feature performs that comparison for you. What the platform does give you:

| Capability | What it is good for | Not good for |
|---|---|---|
| **Now Assist for CMDB** (generative AI, licence-dependent) | Summarising a CI and its relationships in plain language, suggesting a class when classification is ambiguous, drafting a description | Telling you *why* an item was partial — it reads the CI, not the import chain |
| **CMDB Health / CMDB Workspace dashboards** (rule-based, not AI) | Fast triage of which classes are under-populated, duplicate/stale signals | Root-causing a single run; no notion of import order |
| **IRE processing reports + “Reprocess partial payloads”** | Inspecting what IRE did with a specific item | Choosing the right fix; reprocessing before the prerequisite exists just reproduces the same partial |
| **Execution diagnosis** (`sn_cmdb_int_util_execution_diagnosis`) | Per-execution detail behind a `CEX…` record | Cross-import reasoning |
| **Service Graph Connector connection test / Guided Setup** | Proving credentials, alias and egress | Proving a feed returned data — that is the `rows` column |
| **Now Assist in platform search / docs Q&A** | Finding the documented prerequisite order for the connector version you have installed | Verifying it against your instance — always check §Fast path steps 1–3 |

How to use AI well on this class of problem:

1. **Feed it counts, not prose.** "NIC import: 1 execution, rows=0. Volume import: 0 executions.
   EC2: 5 runs, ire_partial=6." An assistant can rank hypotheses from that in one pass; it cannot
   derive it from "imports are failing".
2. **Ask for the discriminator, not the answer.** "Which single field separates 'mapping is broken'
   from 'prerequisite never ran'?" — here: whether the entity maps attributes at all, and whether
   the prerequisite's staging table has rows.
3. **Make it state the check that would falsify its theory**, then run that check yourself. Two
   parallel agents on this case concluded "the scheduled imports are not configured"; both were
   wrong, because neither queried `scheduled_import_set` by name. `active = true`, two records,
   both children of an inactive parent.
4. **Never let an assistant create, activate or reprocess anything on the strength of a summary.**
   Diagnosis is read-only; the change is a separate, reviewed step.

</details>

## Checkpoint

<ul class="check">
<li>You can place any failure on the ladder before opening a log</li>
<li>You know which table proves "rows arrived" versus "CIs created"</li>
</ul>

Next: [Lab 11 — cleanup]({{ '/labs/11-cleanup/' | relative_url }})
