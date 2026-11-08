---
layout: default
title: Run the import
lab: 4
time: 45 min
level: ServiceNow
order: 4
permalink: /labs/04-run-import/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>Run the connector's jobs <em>one at a time</em>, in the order the app expects — like building with blocks: account, then region, then networks. "Processed" only means the engine looked at a row; you still have to open the lists and count real Configuration Items (CIs).</p>
</div>

## Two bars: minimum evidence vs basic PoC

| Bar | What it proves | Labs that assume it |
|---|---|---|
| **Minimum evidence** (orders **100–120** + screenshots below) | Account, datacenter, two VPC **network** CIs | You can start [Lab 5]({{ '/labs/05-ire/' | relative_url }}) IRE reading with real partials |
| **Basic PoC import** (orders **130–180**, counters/text only) | Subnet, security group, one **VM** from EC2 — graph **not** clean | [Labs 6–9]({{ '/labs/06-etl-mappings/' | relative_url }}) are **curriculum**, not repetition of the PoC |

**Basic PoC done ≠ whole lab done.** Labs 5 onward teach IRE depth, ETL edits, CSDM, multisource, and drift — even when your VM row already exists.

Do **not** run **`SG-AWS-Organization`** (cascades 36 children including SSM/EKS).

## Objective

Run standalone AWS schedules **one at a time**, read **Executions** counters and the **correct CI table**, and meet the minimum evidence bar (through VPC). Continue through EC2 only when you are ready for the basic PoC chain in §9.

## 1. Schedules and order (use these names)

Filter Navigator → **Service Graph Connector for AWS → Scheduled Imports** (or the same list in SGC Central / Guided Setup).

Run **Execute Now** on **one** schedule at a time, in this order:

| Order | Schedule name | Why this position |
|---|---|---|
| **100** | `SG-AWS-Service-Account` | Seeds the cloud service account CI locally |
| **110** | `SG-AWS-Datacenters` | Region/datacenter CIs VPC import expects |
| **120** | `SG-AWS-VPC` | Lands in **`cmdb_ci_network`** (not `cmdb_ci_vpc`) |
| 130+ | See §8 | Basic PoC — verified counters (Lab 5 adds VM IRE screenshots when published) |

## 2. Where to watch (read the plumbing)

Walkthrough screenshots below are **real UI captures**, cropped and redacted (VPC IDs, DHCP option IDs, instance hostnames, account identifiers). Match **CIDR**, **state**, and **transform counters** on your instance — not every internal record number.

After each **Execute Now**, open the run from **Executions** (or **Concurrent Import Sets** → `sys_import_set_run_list.do`) and drill into **all** of these tabs — the summary line on the schedule record is not enough:

1. **Import Sets** — raw row counts landed from AWS.
2. **Concurrent Import Set Jobs** — job state (`Loaded`, **`Pending`**, `Complete`).
3. **Transform Histories** — Robust Transform Engine (RTE) counters: Total, Processed, Inserts, Updates, Ignored, Skipped, Errors.
4. **Import Set Rows → Comments** — per-row outcome; partial/warning comments are **not** success by themselves.
5. **Import Log** — may be empty even when work happened (observed on a verified run). Do not treat an empty log as proof nothing ran.

### `Loaded` / `Pending` means wait — not click again

If a concurrent job shows **`Pending`**, the platform has queued work. **Refresh** the list or open the job again after a short wait. Do **not** hammer **Execute Now** on the same schedule while jobs are still pending — you only duplicate runs.

![Concurrent import set job in Pending state]({{ '/assets/img/lab04/pending.png' | relative_url }})
*Concurrent Import Set Jobs tab: **Pending** while datacenter work finishes — refresh, do not re-execute.*

### RTE counters — how to read them without fooling yourself

| Counter | ELI5 | Pitfall |
|---|---|---|
| **Processed** | "Looked at this row" | **Not** "created a CI" |
| **Inserts** | CMDB-side creates across **all** classes touched by the payload | One VPC row can insert many related rows (tags, relations, supporting records) |
| **Updates** | Matched and merged | Healthy on a rerun |
| **Ignored / Skipped** | Row intentionally not committed | Read Comments |
| **Errors** | Hard failures on that row | Investigate; do not dismiss |

**Transform Map** may show **(empty)** on RTE paths — that is normal for Service Graph connector imports.

## 3. Step 100 — `SG-AWS-Service-Account`

**Execute Now** on `SG-AWS-Service-Account` only.

Verified behaviour:

- Produces **one** cloud service account CI from **local** instance data (synthetic account row), **without** an AWS Organizations API call for that step.
- Confirm in Filter Navigator → `cmdb_ci_cloud_service_account.list` (count **1** is the verified shape).

This CI is **not** a substitute for an IAM or credential test.

> A partial **cloud org** relation may still appear in standalone mode when org fields are blank. An account CI can be created while org linkage is incomplete — do not assume that is harmless without checking `cmdb_ire_partial_payloads` and related lists on your instance.

## 4. Step 110 — `SG-AWS-Datacenters` (prerequisite for VPC)

**Execute Now** on `SG-AWS-Datacenters`.

Verified first-run shape:

1. Import set may show **`Loaded`** while a concurrent job is **`Pending`** — wait/refresh (§2).
2. After completion, transform history showed **Processed** with a row **Comment** indicating **inserted 1** (exact wording varies by release).
3. List view **`cmdb_ci_aws_datacenter.list`** showed **one** row: region **`us-east-2`**.

![AWS Datacenter list with us-east-2]({{ '/assets/img/lab04/datacenter.png' | relative_url }})
*After order **110**: one **AWS Datacenter** row for region `us-east-2`.*

<ul class="check">
<li><code>cmdb_ci_aws_datacenter</code> contains your lab region (verified: <code>us-east-2</code>)</li>
<li>Transform history shows a commit (insert/update), not only Processed</li>
</ul>

## 5. Step 120 — `SG-AWS-VPC` **before** datacenter exists (lesson)

If you already ran VPC once **before** step 110 completed, you are not alone — a verified walkthrough did exactly that.

### AWS side (sanity check)

In the AWS console → **VPC → Your VPCs**, a verified lab account showed **two** **Available** VPCs (different purposes — **not** duplicates):

| Name (tag) | IPv4 CIDR | Notes |
|---|---|---|
| `sgclab-vpc` | `10.42.0.0/16` | Named lab VPC |
| *(empty)* | `172.31.0.0/16` | Default VPC pattern |

![Two Available VPCs in AWS]({{ '/assets/img/lab04/aws-vpcs.png' | relative_url }})
*AWS console **Your VPCs** — two **Available** CIDRs (`sgclab-vpc` vs default-style `172.31.0.0/16`). Resource IDs redacted in the published image.*

### ServiceNow side (why zero CIs)

Transform history for the **first** VPC run (datacenter missing):

| Total / source rows | Processed | Inserts | Updates | Errors |
|---|---|---|---|---|
| 2 | 2 | **0** | **0** | 0 |

![First VPC transform — zero inserts]({{ '/assets/img/lab04/vpc-transform.png' | relative_url }})
*Transform Histories on the **first** VPC run: **2** processed, **0** inserts/updates (datacenter still missing).*

Both **`cmdb_ci_network.list`** and **`cmdb_ci_vpc.list`** were **empty** — even though AWS had two VPCs.

Diagnosis (verified via `cmdb_ire_partial_payloads` export, not Import Log):

- Reason: **`MISSING_MATCHING_ATTRIBUTES`**
- Lookup-only native key shape: `<connection>|<account>|<region>` (e.g. connection + account + **`us-east-2`**)
- VPC payloads were **parked** waiting for the datacenter CI

**Class lookup:** VPCs from this connector map to **`cmdb_ci_network`** (Cloud Networks), **not** `cmdb_ci_vpc`. Searching the wrong table looks like a failed import.

Row-level **Comments** showed partial / warning text — treat that as "not done yet", not as success.

## 6. Step 120 — `SG-AWS-VPC` **rerun** after datacenter (verified success)

After §4 is green, **Execute Now** on `SG-AWS-VPC` again (do not re-run Organization).

Verified transform history shape on the rerun:

| Total | Processed | Inserts | Updates | Ignored | Errors |
|---|---|---|---|---|---|
| 2 | 2 | **15** | **2** | 0 | 0 |

![VPC rerun transform counters]({{ '/assets/img/lab04/vpc-rerun.png' | relative_url }})
*After datacenter exists: **2** processed, **15** inserts, **2** updates — related records, not fifteen VPCs.*

### End checkpoint — Cloud Networks (verified)

Refresh **`cmdb_ci_network.list`** (title **Cloud Networks**). Verified list:

| CIDR | State |
|---|---|
| `10.42.0.0/16` | Available |
| `172.31.0.0/16` | Available |

On your instance, **Name** / **Object ID** include AWS VPC ids — compare to the AWS console. Do not commit unredacted ids into public repos.

![Cloud Networks list — two VPC CIs]({{ '/assets/img/lab04/vpc-success.png' | relative_url }})
*Verified end checkpoint: **Cloud Networks** — two rows, **Available**, CIDRs `10.42.0.0/16` and `172.31.0.0/16` (VPC ids redacted here).*

<ul class="check">
<li>Exactly <b>two</b> cloud network rows matching your two AWS VPCs (CIDR + state Available)</li>
<li>Latest VPC transform shows non-zero <b>Inserts</b> and lists are populated</li>
</ul>

**Minimum evidence checkpoint (screenshots above):** orders **100 → 110 → 120** only. Stop here if you are tracing dependency partials before touching subnets.

## 7. Verifier script

```bash
python3 scripts/verify_cmdb.py --vpc-checkpoint   # after order 120
python3 scripts/verify_cmdb.py                    # after SG-AWS-EC2 (needs cmdb_ci_vm_instance)
```

(`SN_INSTANCE`, `SN_USER`, `SN_PASS` — [Lab 0 §4]({{ '/labs/00-prerequisites/' | relative_url }}).)

## 8. Basic PoC chain (130–180) — verified counters, validate in lists

Open **Scheduled Imports** under the **Service Graph Connector for AWS** application (not Azure). The list may show only the first rows — **search Name** for `EC2`, `Subnet`, or `Security`.

| Order | Schedule (exact name) | Validate in | Verified shape (your ids differ) |
|---|---|---|---|
| **130** | `SG-AWS-Subnets` | `cmdb_ci_cloud_subnet.list` | **4** processed, **33** inserts, **6** updates, **0** errors |
| **140** | `SG-AWS-Network-Interface` | `cmdb_ci_nic.list` | Creates the NIC CIs that EC2 will only *reference*. Skipping it is allowed for the PoC **if you accept the partials** — see [§9](#lab4-partial-dependencies). **0 rows is a signal to investigate, not a pass.** |
| **150** | `SG-AWS-Security-Group` | `cmdb_ci_compute_security_group.list` | **3** processed, **22** inserts; **3** CIs incl. `labgroup` |
| **160** | `SG-AWS-Storage-Volume` | `cmdb_ci_storage_volume.list` | Creates the EBS volume CIs that EC2 will only *reference*. Was missing from the original PoC list — see [§9](#lab4-partial-dependencies). |
| **180** | `SG-AWS-EC2` | **`cmdb_ci_vm_instance.list`** | Row comment **inserted 1 / updated 1**; VM **`sgclab-app-01`**, state **Off**, AWS id matches; tags `Environment`/`Application`/`Owner` visible |

**EC2 is not `cmdb_ci_ec2_instance` on this connector path** — always open **Virtual Machine Instance** / `cmdb_ci_vm_instance`.

**Rerun check:** second **Execute Now** on `SG-AWS-EC2` → list still **1** row, same `object_id` (duplicate identification **pass**); transform **processed** count can be **>1** without creating a second VM. **`discovery_source`:** verified **`SG-AWS`** on the walkthrough VM ([Lab 5]({{ '/labs/05-ire/' | relative_url }})).

**Not a clean graph:** EC2 row comments still report partial/warning counts (`storage_volume` 1/1; `nic` 2/2; `relations` 3/3 unresolved) while **`os_template`**, **`compute_template`**, **`endpoint_block`**, **`endpoint_vnic`**, **`storage_mapping`** were created. Subnet import **corroborates** EC2 unchanged (no duplicate VM). These six are **caused by the PoC order skipping 140 and 160** — see [§9](#lab4-partial-dependencies).

## 9. Why the PoC shows `nic` / `storage_volume` partials — and how to get a clean graph
{: #lab4-partial-dependencies}

If you followed §8 exactly, your EC2 run reports **2 `cmdb_ci_nic`**, **1 `cmdb_ci_storage_volume`** and **3 `cmdb_rel_ci`** partial/warning entries — every single run. Those six are not a broken mapping and not a bug in the connector. This section is the explanation, verified against a real instance.

**What is actually happening.** The EC2 mapping does not create NICs or volumes. Its `Cloud Mgmt Network Interface 1/2` and `Storage Volume 1` entities are **reference-only stubs**:

| Entity in the EC2 mapping | Fields it maps |
|---|---|
| `Cloud Mgmt Network Interface 1` | `source_native_key`, `cmdb_ci` (reference to the VM entity) |
| `Cloud Mgmt Network Interface 2` | `source_native_key` |
| `Storage Volume 1` | `source_native_key` |

The attributes (`object_id`, `name`, `private_ip`, `public_ip`, `volume_id`, `size`, …) live in the **`SG-AWS-Network-Interface` (140)** and **`SG-AWS-Storage-Volume` (160)** mappings. Both CI classes use a **dependent identifier** (`cmdb_identifier.independent = false`), so a stub that only carries `discovery_source` plus a source key cannot create a record — it can only *link* to one that already exists.

So if 140/160 never ran, there is nothing to link to, and IRE parks the item as `MISSING_DEPENDENCY` in `cmdb_ire_partial_payloads` (values reduced to `discovery_source: SG-AWS`). Correct behaviour, unhelpful symptom.

**Two legitimate choices**

| Choice | Do this | Accept |
|---|---|---|
| **A. PoC, partials expected** | Nothing extra. Continue to [Lab 5]({{ '/labs/05-ire/' | relative_url }}) — the partials are excellent reading material | The 6 partials stay on every run; the VM, tags and the created supporting CIs are still correct |
| **B. Clean graph** | Execute **140**, then **160**, then re-run **180** (`SG-AWS-EC2`) | `ire_partial` drops to **0**; `cmdb_ci_nic` gains your eni with a real `object_id`; VM→NIC and VM→volume relations appear |

Do **not** activate `SG-AWS-Organization` to get this automatically — it cascades 36 children including SSM/EKS (see the banner above). Run 140 → 160 → 180 by hand.

**If 140 itself loads 0 rows, stop and investigate.** A run that completes with `state = complete` but **`rows = 0`** means the AWS call returned nothing — the import never had data to map. That is a different problem from "we skipped it", and it is exactly the failure found in a real session: `SG-AWS-Network-Interface` ran once (`CEX0001013`) with `rows = 0`, `SG-AWS-Storage-Volume` had **never executed at all**, so `cmdb_ci_nic` stayed empty and every EC2 run reported 6 partials. The cause there was not the mapping; it was the prerequisites never producing data. Check `sn_cmdb_int_util_cmdb_integration_execution.list` (`rows` column) and the staging table `sn_aws_integ_sg_aws_network_interface.list` before touching any mapping.

One re-run on its own only proves the condition **recurs** — it does not identify the cause. Conclusive evidence is the loader's own response (HTTP status, endpoint, body or error) for this account/region, so arrange capture **before** spending an execution, and keep "run it again" and "change the IAM policy/scope" as two separate decisions. Full walkthrough: [Lab 10 — case study]({{ '/labs/10-troubleshooting/' | relative_url }}#lab10-missing-dependency).

<details markdown="1">
<summary><strong>Quick check: did the prerequisites actually produce anything?</strong></summary>

| Question | Where | Failing answer |
|---|---|---|
| Did 140/160 run at all? | `sn_cmdb_int_util_cmdb_integration_execution.list` (`CEX…`) | **no record** = never ran |
| Did they fetch data? | same table, **`rows`** column | **0** = AWS returned nothing |
| Did rows land in staging? | `sn_aws_integ_sg_aws_network_interface.list`, `sn_aws_integ_sg_aws_storage_volume.list` | empty table |
| Did the CIs get created? | `cmdb_ci_nic.list`, `cmdb_ci_storage_volume.list` — read `discovery_source` and `object_id` | 0 rows, or rows with `discovery_source = ServiceNow` (Mid Server disks, blank `object_id`) |
| Does the exact key exist? | `sys_object_source.list`, filter `id` contains your `eni-…` / `vol-…` | no row = CI never created |

</details>


## Troubleshooting pointers

- Partial payloads: `cmdb_ire_partial_payloads.list` (export JSON for the exact `reason`).
- Full ladder: [Lab 10 — Troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }}).
- IRE vocabulary: [Lab 5]({{ '/labs/05-ire/' | relative_url }}).

## Checkpoint

**Minimum (Lab 4 evidence):**

<ul class="check">
<li>Orders <code>100 → 110 → 120</code>; <code>cmdb_ci_network</code> = two Available CIDRs</li>
<li>Can explain Processed vs Inserts and datacenter-before-VPC partials</li>
</ul>

**Basic PoC (optional continuation in §8):**

<ul class="check">
<li>One <code>cmdb_ci_vm_instance</code> for <code>sgclab-app-01</code>; rerun still count 1</li>
<li>Subnets + security groups in the tables above; you accept NIC partials on EC2</li>
</ul>

Next: [Lab 5 — read the IRE results]({{ '/labs/05-ire/' | relative_url }})
