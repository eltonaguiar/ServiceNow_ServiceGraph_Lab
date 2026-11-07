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

## Part A — First safe navigation (confirm on your UI)

Menu names move between releases. Use **Filter Navigator** and search; do not trust a single path from this doc until you see it:

1. Open **IntegrationHub**, **Flow Designer**, or the **Service Graph Connector for AWS** app — whichever exists.
2. Search for **ETL**, **transform**, or **mapping** definitions tied to **EC2**, **VM**, or **hardware** (exact title varies).
3. Open the definition used by **`SG-AWS-EC2`** (match name or schedule link on your release).
4. In **Transform**, locate mappings targeting **`cmdb_ci_vm_instance`** (not `cmdb_ci_ec2_instance`).

**Learner confirmation:** write down the **exact definition name** and **three target fields** you see (`name`, `object_id`, and one tag). If you cannot find a mapping editor, stop at Part A — note “mapping UI not exposed on this PDI” and continue to Lab 7.

## Part A — Read one field (no edits)

1. On the VM from Lab 5, note **`name`**, **`object_id`**, and one tag value on the form.
2. In Transform, find the **target** field(s) for those attributes.
3. Note the **source** expression or path shown in the UI (do not assume `Reservations[].Instances[]`).
4. Open the latest **`SG-AWS-EC2`** import set row and view **payload** / staging data if the UI offers it — compare structure to the mapping path.

**Screenshot slot (pending):** `assets/img/lab06/etl-vm-transform-readonly.png` — Transform stage with mappings visible; redact credentials.

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
<li>You found the EC2/VM mapping surface on <b>your</b> instance (name recorded in notes)</li>
<li>You linked one VM field to a transform target <b>without</b> assuming REST EC2 JSON shape</li>
<li>You know where import row <b>payload</b> lives for path verification</li>
</ul>

**Optional (Part B):**

<ul class="check">
<li>One string mapping added, verified, and <b>reverted</b></li>
</ul>

Next: [Lab 7 — CSDM and the service graph]({{ '/labs/07-csdm-graph/' | relative_url }})
