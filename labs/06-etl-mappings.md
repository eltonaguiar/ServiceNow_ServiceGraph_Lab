---
layout: default
title: Change an ETL mapping
lab: 6
time: 30 min
level: Data
order: 6
permalink: /labs/06-etl-mappings/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>ETL is the translator between cloud JSON and CMDB fields. <strong>First</strong> find how your connector already maps your lab VM — only then, optionally, change something on a throwaway PDI.</p>
</div>

## Prerequisites

- Lab 5 **minimum** complete: one **`cmdb_ci_vm_instance`**, same identity on EC2 rerun.
- **Own PDI** — not a shared instance.

## Two parts

| Part | Required? | What you do |
|---|---|---|
| **A — Observational** | **Yes** | Locate the EC2/VM mapping definition; trace how **`name`**, **`object_id`**, and tag fields are filled **today** |
| **B — Optional edit** | No | Add **one** string field on a **clone/sandbox** mapping, verify, **rollback** |

Part A does not assume classic EC2 **`DescribeInstances`** JSON (`Reservations[].Instances[]`). This connector path is tied to **AWS Config** / Service Graph payloads — **your** import set row payload is the source of truth for JSON paths.

## Part A — Verified navigation (read-only)

Walkthrough-confirmed path (yours should match before you trust it):

1. **All** → search **IntegrationHub ETL**.
2. **Configuration → IntegrationHub ETL**.
3. Expand **CMDB Application: SG-AWS** (count varies, e.g. **33**).
4. Open **Name** **`SG-AWS-EC2-Instance`** — this is the **ETL definition**, not the scheduled import label **`SG-AWS-EC2`** and not the data source alone.

**Transform Map Assistant** banner (verbatim meaning): no import set associated → maps are **read-only** until you pick a sample import set under **Specify Basic Details**. For this lab: **stay read-only** — do **not** select a sample, **do not** deactivate assistant controls to “unlock” edit.

**Step 3 — Map Data to CMDB and Add Relationships** → **Select CMDB Classes to Map Source Data**. Observed cards on one instance:

| Card | Count | Notes |
|---|---|---|
| **Virtual Machine Instance** | 1 | Table **`cmdb_ci_vm_instance`**; dependent on `cmdb_ci_logical_datacenter`, `cmdb_ci_rubrik_cluster`, `cmdb_ci_kubernetes_cluster`, `cmdb_ci_virtualization_server`, `cmdb_ci_computer`; condition `object.isDeletedResource=false` |
| Availability Zone | 1 | (shown; details not expanded in walkthrough) |
| Cloud Network | 1 | |
| Cloud Subnet | 1 | |

Next learner step: **View Mapping** on the **Virtual Machine Instance** card only (field-level mappings not yet captured in this doc — describe what you see in notes).

**Do not** toggle controls, select sample import sets, or edit mappings for Part A minimum.

## Part A — After View Mapping (no edits)

1. On the VM from Lab 5, note display **`name`**, tags, and list columns you can see **without** pasting ids into git.
2. In **View Mapping** for **Virtual Machine Instance**, record **target fields** and **source paths** exactly as labeled in the UI (do not assume `Reservations[].Instances[]`).
3. Optional cross-check: latest **`SG-AWS-EC2`** import set row **payload** in ServiceNow — compare shape to source paths (keep payload private).

## Part B — Optional edit (own PDI only)

Skip Part B unless you have a **supported** way to duplicate or customize mappings without breaking the store connector, and you can **revert**.

| Do | Don't (unsafe defaults) |
|---|---|
| Map a plain **string** to an existing string or `u_*` attribute | Point **`model_id`** at raw **`InstanceType`** without a reference/catalog transform |
| Clone/customize only if your release documents it | Edit **stock** connector mappings in production scope |
| Revert mapping, re-import, confirm VM unchanged | Deliberately break **`name`** mapping to “learn” — use payload inspection instead |
| One field, one re-import, rollback | Leave broken mappings on a shared instance |

After an optional edit: **Execute Now** on **`SG-AWS-EC2`** only, confirm the VM count still **1**, then **undo** the mapping change.

## Checkpoint

**Minimum (Part A only):**

<ul class="check">
<li>You opened <code>SG-AWS-EC2-Instance</code> under IntegrationHub ETL and saw <b>Virtual Machine Instance</b> card (read-only)</li>
<li>You linked one VM field to a transform target <b>without</b> assuming REST EC2 JSON shape</li>
<li>You know where import row <b>payload</b> lives for path verification</li>
</ul>

**Optional (Part B):**

<ul class="check">
<li>One string mapping added, verified, and <b>reverted</b></li>
</ul>

Next: [Lab 7 — CSDM and the service graph]({{ '/labs/07-csdm-graph/' | relative_url }})
