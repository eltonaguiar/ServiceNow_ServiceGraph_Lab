---
layout: default
title: Read the IRE results
lab: 5
time: 25 min
level: CMDB
order: 5
permalink: /labs/05-ire/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>IRE decides “new, same as before, or not yet.” This lab is <strong>look, don’t touch</strong>: read outcomes, one VM identity, and what is still partial — no rule edits for the minimum bar.</p>
</div>

## Prerequisites

- [Lab 4]({{ '/labs/04-run-import/' | relative_url }}) basic PoC: **one** row in **`cmdb_ci_vm_instance`** after **`SG-AWS-EC2`**.
- **Continuity check (separate from the screenshot):** re-run **`SG-AWS-EC2`** and confirm the list stays at **one** row with the **same** `object_id` (transform **processed** count may be **>1**).

## Objective (minimum)

**Observational:** confirm the lab VM’s **identity**, **source**, **identifier rule** (read-only), and **partial graph** caveats. Optional duplicate exercise stays optional ([§6](#optional-duplicate-exercise-throwaway-pdi-only)).

## 1. One CI on the list

| Check | Where | Pass when |
|---|---|---|
| Count **1** | `cmdb_ci_vm_instance.list` | Single lab VM (e.g. `sgclab-app-01`) |
| **State Off** | Same list / form | Matches stopped instance in AWS |
| **Discovery source `SG-AWS`** | List or form | Connector attribution visible |
| Rerun | Re-execute schedule | Still **one** row; same `object_id` in notes |

![One VM row — discovery source SG-AWS]({{ '/assets/img/lab05/vm-discovery-source.png' | relative_url }})
*List proof at one point in time: **Off**, **SG-AWS**. Object id redacted; rerun continuity is a separate step above.*

## 2. Identification rule (read-only)

**CI Class Manager** → **Virtual Machine Instance** → **Identification Rule** (or Identification and Reconciliation → rules for that class).

Verified shape on the walkthrough instance:

| Field | Value |
|---|---|
| Type | **Dependent** |
| Name | **VM Instance** |
| Identifier entry | **Standard**, priority **100**, active |
| Criterion | **Object ID** |
| Related entries | Azure/AWS extension tables — **assist** identification; not proof that every related table ran for this import |

**Do not edit** rules to pass the minimum lab.

![VM Instance dependent rule — Object ID]({{ '/assets/img/lab05/vm-identification-rule.png' | relative_url }})

## 3. Dependency diagram (vocabulary only)

**Dependent Relationships** on the same class shows **configured** hosting/containment options (Logical Datacenter, Computer, Rubrik/Kubernetes, Virtualization Server, …). They are **not** all mandatory and **not** all proven matched paths for this EC2 run.

The lab VM showing **Hosted on → AWS Datacenter** is **consistent** with the PoC; it does not replace reading IRE/partials.

![Dependent relationship diagram (configured options)]({{ '/assets/img/lab05/vm-dependent-relationships.png' | relative_url }})

## 4. Partials (no Config scope expansion)

Walkthrough after EC2:

- Partial payload work on VM / **endpoint_vnic**; skeletal **`cmdb_ci_nic`** / **`cmdb_ci_storage_volume`** with **`MISSING_DEPENDENCY`**.
- Rerun comments: **nic 2**, **storage_volume 1**, **relations 3** partial/warning — unchanged on later pass.

Lab **AWS Config** records only Instance/VPC/Subnet/SecurityGroup ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }})) — **no** NIC/Volume in scope. Partial NIC/storage edges are **expected**; exact loader prerequisites are **not proven** here. Do **not** widen paid Config merely to “clean” optional graph edges.

Use **`cmdb_ire_partial_payloads.list`** on your instance; do not commit raw payloads.

## 5. Quick tables

```text
cmdb_ci_vm_instance.list
cmdb_ire_output_item.list
cmdb_ire_partial_payloads.list
```

```bash
python3 scripts/verify_cmdb.py --ire
```

## Optional duplicate exercise (throwaway PDI only)

On **your own** lab PDI only: record `object_id` → break identifier → duplicate → delete **your** duplicate → restore → one row. Not required for Lab 6 Part A.

## Checkpoint

<ul class="check">
<li>List shows <b>one</b> VM; <code>SG-AWS</code> source; state <b>Off</b></li>
<li>Rerun keeps <b>one</b> row and same <code>object_id</code> (you verified separately)</li>
<li>Read <b>Dependent</b> rule with <b>Object ID</b> — <b>no</b> rule edits</li>
<li>Can explain open <b>nic</b>/<b>storage</b> partials under narrow Config scope</li>
</ul>

Next: [Lab 6 — ETL mappings]({{ '/labs/06-etl-mappings/' | relative_url }}) (read-only first)
