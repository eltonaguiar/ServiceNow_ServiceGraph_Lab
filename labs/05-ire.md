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
- The human view: **Configuration → Identification and Reconciliation → IRE Results**, or the
  "IRE results" link from the import set.

Filter to your run by timestamp and by `data_source`.

If the menu path above does not exist on your release, go straight to the table:

```text
https://<your-instance>.service-now.com/cmdb_ire_output_item_list.do
https://<your-instance>.service-now.com/cmdb_ire_output_rule_list.do
```

Also useful: the import set's own record has an **IRE output** related list — that is the only
path that shows you *one run* without timestamp guessing.

## 2. Read the outcome

| Outcome | Meaning |
|---|---|
| **Inserted** | No match — a new CI was created |
| **Updated** | Matched an existing CI; attributes were merged |
| **Skipped / No change** | Matched, and nothing differed — the healthy steady state |
| **Rejected / Error** | Payload violated a rule (missing identifier, bad reference, duplicate items in one payload) |

A second import with no changes in AWS should produce **mostly "no change"**. If it produces
another insert, your identification is broken and you now have duplicates. That is the single
most common real-world failure.

## 3. Inspect the rules

**Configuration → Identification and Reconciliation → Identification Rules** (also reachable
from **CI Class Manager** → your class → Identification).

For `cmdb_ci_ec2_instance` you will typically find a rule keyed on the AWS instance
identifier — the record's `object_id` or a source-specific correlation attribute — with the
class's name as a search attribute, depending on the release.

Exercises:

1. Note the **search attributes**, the **identifier entry**, and whether the rule is
   **independent** or **dependent** on a parent CI.
2. Run the import a second time and confirm the outcome flips to "no change".
3. Deliberately break it: change the CI's identifier attribute by hand, re-run the import, and
   observe a duplicate appear. Then delete the duplicate and re-run to confirm the original is
   matched again.

> Doing (3) once is worth an hour of reading. It is exactly what happens in production when
> someone "cleans up" a CI by hand.

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
<li>You can name the identification rule that matched your EC2 CI</li>
<li>A second import produced "no change", not a second insert</li>
<li>You created a duplicate on purpose and cleaned it up</li>
<li>You can state the difference between Inserted, Updated and Rejected in one sentence each</li>
</ul>

Next: [Lab 6 — change an ETL mapping]({{ '/labs/06-etl-mappings/' | relative_url }})
