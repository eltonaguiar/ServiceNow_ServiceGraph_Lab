---
layout: default
title: Read the IRE results
lab: 5
time: 30 min
level: CMDB
order: 5
permalink: /labs/05-ire/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>IRE is the bouncer at the CMDB door: for every record it asks "have I seen this before?" and then creates, updates, or skips. Reading its answers is the single most useful CMDB skill.</p>
</div>

## Before you start

If [Lab 4]({{ '/labs/04-run-import/' | relative_url }}) §8 already gave you a **VM in
`cmdb_ci_vm_instance`**, that is **import evidence**, not this lab finished. Here you learn to read
IRE and partial **row Comments** (EC2 can show **inserted 1 / updated 1** while `storage_volume`,
`nic`, and `relations` partials remain).

## Objective

Explain, per record, why IRE inserted, updated or skipped it — and fix one identification
problem on purpose.

## Why this is the heart of the lab

The Identification and Reconciliation Engine (**IRE**) is what turns a pile of payloads into a single
CMDB. Every connector, every discovery source and every manual import ends up in the same
queue. If you cannot read IRE (Identification and Reconciliation Engine) output, "the import didn't work" is unknowable.

## 1. Find the results

Two useful surfaces (menu paths move between releases — the direct URLs do not):

- **IRE result tables**: `cmdb_ire_output_item` (one row per processed payload) and
  `cmdb_ire_output_rule` / `cmdb_ire_output_rule_item` (which rule matched).
- **`cmdb_ire_partial_payloads`** — payloads parked when a **dependency** could not be resolved
  (verified example: VPC before datacenter, reason `MISSING_MATCHING_ATTRIBUTES`, lookup key
  `<connection>|<account>|<region>`).
- The human view: **Configuration → Identification and Reconciliation → IRE Results**, or the
  "IRE results" link from the import set.

Filter to your run by timestamp and by `data_source`.

If the menu path above does not exist on your release, go straight to the table:

```text
https://<your-instance>.service-now.com/cmdb_ire_output_item_list.do
https://<your-instance>.service-now.com/cmdb_ire_output_rule_list.do
https://<your-instance>.service-now.com/cmdb_ire_partial_payloads_list.do
```

Also useful: the import set's own record has an **IRE output** related list — that is the only
path that shows you *one run* without timestamp guessing.

### When transforms look "fine" but lists are empty

On the verified VPC-before-datacenter run:

- Transform Histories showed **Processed = 2**, **Errors = 0**, **Inserts = 0**.
- **`cmdb_ci_network`** and **`cmdb_ci_vpc`** were both empty.
- Import Set row **Comments** carried partial/warning text (not a green success story).
- **Import Log** was empty; syslog export had no helpful warning — **`cmdb_ire_partial_payloads`**
  export had the exact JSON reason.

That combination means **dependency partial**, not "IRE is broken" and not "credentials are wrong."

## 2. Read the outcome

| Outcome | Meaning |
|---|---|
| **Inserted** | No match — a new CI was created |
| **Updated** | Matched an existing CI; attributes were merged |
| **Skipped / No change** | Matched, and nothing differed — the healthy steady state |
| **Rejected / Error** | Payload violated a rule (missing identifier, bad reference, duplicate items in one payload) |
| **Partial / parked** (`cmdb_ire_partial_payloads`) | Waiting on another CI (e.g. datacenter for region) — fix order, rerun the **same** schedule |

### One source row ≠ one CI

A single import row can create **many** inserts (tags, relations, supporting records). That is why
a VPC rerun can show **15 inserts** and **2 processed** source rows — not fifteen VPCs. Always open
the **target class** you care about (`cmdb_ci_network` for VPC in Lab 4).

A second import with no changes in AWS should produce **mostly "no change"**. If it produces
another insert, your identification is broken and you now have duplicates. That is the single
most common real-world failure.

## 3. Inspect the rules

**Configuration → Identification and Reconciliation → Identification Rules** (also reachable
from **CI Class Manager** → your class → Identification).

For AWS EC2 on the Service Graph Connector, open identification on **`cmdb_ci_vm_instance`**
(not `cmdb_ci_ec2_instance`). Rules typically key on the AWS instance id in `object_id`.

### Default (observational — enough for basic PoC)

On **`cmdb_ci_vm_instance`** (your lab VM, e.g. `sgclab-app-01`):

1. Read the identification rule: search attributes, identifier, dependent vs independent.
2. Open **IRE output** or import row **Comments** from the last `SG-AWS-EC2` run (insert vs partial).
3. Re-run **`SG-AWS-EC2`** and confirm the list stays at **one** row with the **same** `object_id`.

You do **not** need step 4 below to complete the basic PoC.

### Optional exercise 4 — duplicate on purpose (throwaway PDI only)

**Only** on your **own** lab PDI, on the **single throwaway VM** this lab created — **never** on a
shared, production, or non-lab CMDB.

1. **Before editing:** copy the VM's **`object_id`** and any identification fields to your notes.
2. Change **only** that identifier on the **one** lab record (simulate a bad manual edit).
3. Re-run **`SG-AWS-EC2`**: expect a **second** row (duplicate).
4. **Clean up:** delete **only** the duplicate **you** caused; restore the **original**
   `object_id` on the surviving record; re-import once; verify **one** row again.

Skip this entirely if you are not on a private throwaway instance.

## 4. Reconcile duplicates

**Configuration → Identification and Reconciliation → Duplicate CIs** (or CI Class Manager →
class → Duplicate audit) lists candidate duplicates with a match score. Review one, then use
**De-duplicate** to merge, keeping the record with the connector's discovery source.

## 5. Verify from the API

```bash
python3 scripts/verify_cmdb.py --ire
```

That prints the IRE output counts for the last 24 h grouped by outcome, so you can see the
insert/update/no-change split without opening the UI.

## Checkpoint

<ul class="check">
<li>You opened <code>cmdb_ire_partial_payloads</code> or row Comments and can explain a <code>MISSING_MATCHING_ATTRIBUTES</code> partial</li>
<li>You know VPC maps to <code>cmdb_ci_network</code> on the verified connector path</li>
<li>You can state the difference between Inserted, Updated, Rejected, and Partial in one sentence each</li>
<li>You used <code>cmdb_ci_vm_instance</code> for AWS EC2 identification, not <code>cmdb_ci_ec2_instance</code></li>
<li>You can name at least one EC2 row-comment partial still open (e.g. <code>nic</code> / <code>relations</code>) without calling the graph “done”</li>
</ul>

Next: [Lab 6 — change an ETL mapping]({{ '/labs/06-etl-mappings/' | relative_url }})
