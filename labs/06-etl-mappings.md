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
<p>The connector’s ETL is a recipe card: it says which AWS JSON fields fill which CMDB columns. This lab you <strong>read</strong> the recipe for your lab VM’s <strong>Name</strong> — you do not edit the stock card unless you later choose Part B on your own PDI.</p>
</div>

## Prerequisites

Lab 5 minimum: one **`cmdb_ci_vm_instance`** (e.g. list **Name** `sgclab-app-01`, discovery source **SG-AWS**).

## Where to open (read-only)

1. **All** → **IntegrationHub ETL** → **Configuration → IntegrationHub ETL**.
2. **CMDB Application: SG-AWS** → definition **`SG-AWS-EC2-Instance`** (ETL name, not the **`SG-AWS-EC2`** schedule).
3. **Map Data to CMDB** → **Virtual Machine Instance** card → **View Mapping**.

**Transform Map Assistant:** with no sample import set, mappings stay **read-only**. Do **not** pick **Select a Sample Import Set** or flip controls to edit for the minimum bar.

## Minimum checkpoint (verified)

These are **configured** destinations in the ETL — what the connector is set up to write. They are **not** a runtime execution trace (no import-set preview required for this bar).

| CMDB target (`cmdb_ci_vm_instance`) | Source column on `object` |
|---|---|
| **Name** | **`ec2Name`** (via script — see below) |
| **Object ID** | **`resourceId`** |
| **Source native key** | **`ec2SourceNativeKey`** |

**`ec2Name` is not a CMDB column.** It is a **transform output** that feeds **Name** on the VM table — your list shows **`sgclab-app-01`** in **Name**, not a field literally called `ec2Name`.

### Why `ec2Name` inputs look like `resourceId|tagsStr`

On the **Name** row, ServiceNow shows transform type **Multiple Input Script** with inputs **`resourceId`** and **`tagsStr`**. The script also receives a combined **`input`** string (`resourceId|tagsStr`), but the walkthrough script **does not read** `input` — it uses **`resourceId`** and **`tagsStr`** separately. That unused `input` variable is normal; it does **not** mean the transform is a no-op.

**`ec2SourceNativeKey`** uses a separate **concatenate** transform: `connection_alias_id`, `accountId`, `awsRegion`, `resourceId` with **`|`** delimiter.

![Name maps to object.ec2Name (configured mapping)]({{ '/assets/img/lab06/etl-vm-name-mapping.png' | relative_url }})
*Screenshot: **Target Name** ← **`object.ec2Name`**. Verifies **configuration** on this definition; not proof of a single import-row debug run.*

## What’s next for this lab

| You are here | Next step |
|---|---|
| **Part A done** (navigation + Name / Object ID / native key observed, read-only) | Continue to **[Lab 7 — CSDM and service graph]({{ '/labs/07-csdm-graph/' | relative_url }})** and link **`cmdb_ci_vm_instance`** under an application service |
| Want to **edit** a mapping | **Part B** below — own PDI, clone/customize only if your release supports it, one string field, **rollback** |

Part B remains **optional**; the curriculum does not require changing stock **`SG-AWS-EC2-Instance`** mappings.

## Part B — Optional edit (own PDI only)

| Do | Don't |
|---|---|
| Clone/customize only if supported | Edit production stock definitions |
| One string field, re-import, revert | Break **Name** mapping “to learn” |
| Confirm VM list still **one** row | Leave experimental mappings on a shared instance |

---

<details>
<summary><strong>ELI5 code walkthrough — how <code>ec2Name</code> becomes <code>Name</code> (read-only reference)</strong></summary>

ServiceNow runs a small script **per import row** in the batch. The UI may show the script with `replaceAll("\\", "")` — in the **stored JSON**, that is often serialized as `replaceAll("\\\\", "")` (two backslashes inside quotes = remove one literal backslash in the tag string). Below is the walkthrough shape; line up backslashes with what your PDI displays.

```javascript
(function(batch, output) {
   for (var i = 0; i < batch.length; i++) {
      var input = batch[i].input; // Combined resourceId|tagsStr — assigned but NOT used below.
      var ec2Name = batch[i].resourceId;
      if(!gs.nil(batch[i].tagsStr)){
         try{
            var str = batch[i].tagsStr.replaceAll("\\", "");
            str = str.replaceAll('""', '"');
            str = str.replaceAll(':"}', ':""}');
            var tags = JSON.parse(str);
            if(!gs.nil(tags) && tags.length >0){
               for(var t=0; t < tags.length; t++){
                  var tag = tags[t];
                  if(tag.key.toUpperCase() === 'NAME'){
                     ec2Name = tag.value.trim();
                  }
               }
            }
         }catch(err){ ec2Name = batch[i].resourceId; }
      }
      output[i] = ec2Name;
   }
})(batch, output);
```

**How to read it (beginner):**

1. **IIFE** — `(function…)(batch, output)` defines a function, then ServiceNow calls it with the real **`batch`** and **`output`** arrays.
2. **Outer loop `i`** — one pass per row in the batch (your lab VM is one of those rows).
3. **Start at `resourceId`** — default display name is the AWS resource id (e.g. a placeholder like `i-EXAMPLE` in training examples, **not** pasted here from your account).
4. **`tagsStr` present** — try to parse AWS tags JSON. **`gs.nil`** / **length** skip empty work.
5. **String cleanup** — three `replaceAll` fixes are **import-set-specific** escapes, not general JSON repair.
6. **Inner loop `t`** — walk tags; if key is **`NAME`** (case-insensitive), **`trim`** and use that value.
7. **`output[i] = ec2Name`** — this value is what the ETL attaches to **`object.ec2Name`**, which the **Name** row maps into **`cmdb_ci_vm_instance.name`** (`sgclab-app-01` in the lab).
8. **`catch`** — on parse failure, fall back to **`resourceId`**.
9. **Edge cases** — empty **Name** tag → empty string; several **Name** tags → **last** match in the array wins.

This script does **not** prove tags always exist in AWS; it only shows how the connector **would** prefer a **Name** tag over the raw id when parsing succeeds.

</details>

## Checkpoint

<ul class="check">
<li>Opened <code>SG-AWS-EC2-Instance</code> read-only; <b>Virtual Machine Instance</b> → <b>View Mapping</b></li>
<li>Can point to <b>Name</b> ← <code>object.ec2Name</code>, <b>Object ID</b> ← <code>resourceId</code>, native key ← <code>ec2SourceNativeKey</code></li>
<li>Understand <code>ec2Name</code> is transform output, not a CMDB column; list <b>Name</b> is what landed on the VM</li>
</ul>

Next: [Lab 7 — CSDM and the service graph]({{ '/labs/07-csdm-graph/' | relative_url }})
