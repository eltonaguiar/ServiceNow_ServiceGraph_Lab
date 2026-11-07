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

## What this lab has verified (and what it has not)

| Verified through this walkthrough | Not verified yet |
|---|---|
| `SG-AWS-Service-Account` → one local service-account CI (synthetic; no AWS API for that row) | `SG-AWS-Subnets` (130) and below |
| `SG-AWS-Datacenters` → `cmdb_ci_aws_datacenter` for `us-east-2` | EC2 instance import |
| `SG-AWS-VPC` (after datacenter) → **two** rows in **`cmdb_ci_network`** (Cloud Networks), state Available | Full organization parent import |
| Dependency partial payloads (`MISSING_MATCHING_ATTRIBUTES`) when VPC ran too early | Claiming "15 inserts = 15 VPCs" |

Do **not** run the parent schedule **`SG-AWS-Organization`**. On a verified instance it is **inactive** for good reason: activating it cascades **36** child schedules (including SSM and EKS paths this lab does not need).

## Objective

Execute the minimal Service Graph Connector for AWS schedule chain for a **standalone** account, inspect **Executions** (not only top-level state), and prove AWS VPCs landed as **Cloud Network** CIs.

## 1. Schedules and order (use these names)

Filter Navigator → **Service Graph Connector for AWS → Scheduled Imports** (or the same list in SGC Central / Guided Setup).

Run **Execute Now** on **one** schedule at a time, in this order:

| Order | Schedule name | Why this position |
|---|---|---|
| **100** | `SG-AWS-Service-Account` | Seeds the cloud service account CI locally |
| **110** | `SG-AWS-Datacenters` | Region/datacenter CIs VPC import expects |
| **120** | `SG-AWS-VPC` | VPC payloads (maps to **`cmdb_ci_network`**, not `cmdb_ci_vpc`) |
| 130+ | `SG-AWS-Subnets`, `SG-AWS-NetworkInterface`, `SG-AWS-SecurityGroup`, `SG-AWS-EC2`, … | **Proposed** next steps — run one at a time, inspect before continuing; **not** verified in this lab |

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
<li>You have <b>not</b> claimed EC2/subnet success — only VPC/network through order <b>120</b></li>
</ul>

## 7. Optional verifier script

From the cloned repo ([Lab 0 §4]({{ '/labs/00-prerequisites/' | relative_url }})):

```bash
export SN_INSTANCE="dev123456"
export SN_USER="admin"
export SN_PASS="your-pdi-password"
# After order 120 only (before EC2 schedules):
python3 scripts/verify_cmdb.py --vpc-checkpoint
# Full lab (still requires cmdb_ci_ec2_instance after you run SG-AWS-EC2):
python3 scripts/verify_cmdb.py
```

Expected output shape after the **VPC checkpoint** (`--vpc-checkpoint`; your IDs differ):

```
Mode: Lab 4 VPC checkpoint (before EC2)

table                            count
cmdb_ci_cloud_service_account        1
cmdb_ci_aws_datacenter               1
cmdb_ci_network                      2
cmdb_ci_ec2_instance                 0
cmdb_ci_vpc                          0
```

Default mode (no flag) is the **full lab** goal and exits non-zero until `cmdb_ci_ec2_instance` is populated. `cmdb_ci_vpc` may stay **0** even when VPCs succeeded — VPCs on this path live in **`cmdb_ci_network`**.

## 8. What to run next (parent lab direction — unverified here)

When you continue, keep the **one schedule at a time** rule:

`SG-AWS-Subnets` (130) → `SG-AWS-NetworkInterface` (140) → `SG-AWS-SecurityGroup` (150) → … → `SG-AWS-EC2` (180).

Inspect Executions and the target CI table **before** the next **Execute Now**. This lab does **not** assert full EC2 success until someone verifies it the same way as VPC.

## Troubleshooting pointers

- Partial payloads: `cmdb_ire_partial_payloads.list` (export JSON for the exact `reason`).
- Full ladder: [Lab 10 — Troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }}).
- IRE vocabulary: [Lab 5]({{ '/labs/05-ire/' | relative_url }}).

## Checkpoint (current verified scope)

<ul class="check">
<li>Schedules <code>100 → 110 → 120</code> run individually; Organization parent left inactive</li>
<li>Datacenter CI exists for your region before VPC rerun</li>
<li><code>cmdb_ci_network</code> shows two Available VPC CIDRs matching AWS</li>
<li>You can explain why <b>Processed</b> with <b>0 inserts</b> happened once, and why <b>15 inserts</b> is not "15 VPCs"</li>
</ul>

Next: [Lab 5 — read the IRE results]({{ '/labs/05-ire/' | relative_url }})
