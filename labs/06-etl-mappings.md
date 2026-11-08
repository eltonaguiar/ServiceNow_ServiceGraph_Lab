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
<p>The connector’s ETL is a recipe card: it says which AWS JSON fields fill which CMDB columns. Before the recipe runs, a <strong>data loader</strong> stage copies AWS JSON into a <strong>staging</strong> import-set table (often one wide JSON column). This lab you <strong>read</strong> the recipe and the loader story — you do <strong>not</strong> edit stock connector scripts or schedules to “test.”</p>
</div>

<nav class="toc" aria-label="Lab 6 contents">
  <p class="toc-title">Required path</p>
  <ul class="toc-list">
    <li><a href="#lab6-at-a-glance">At a glance</a></li>
    <li><a href="#lab6-hands-on-etl">Hands-on — ETL mapping</a></li>
    <li><a href="#lab6-data-loader">Loader ELI5 (Lab 9)</a></li>
    <li><a href="#lab6-part-b">Part B (optional)</a></li>
    <li><a href="#lab6-checkpoint">Checkpoint</a></li>
  </ul>
  <p class="toc-title">Appendix — further details (optional reading)</p>
  <ul class="toc-list">
    <li><a href="#lab6-appendix">Appendix overview</a></li>
    <li><a href="#lab6-datasource-types">Data source types</a></li>
    <li><a href="#lab6-parallel-vs-batch">Parallel / batch / transform</a></li>
    <li><a href="#lab6-staging-api">Staging API</a></li>
    <li><a href="#lab6-pitfalls">Pitfalls</a></li>
    <li><a href="#lab6-js-fundamentals">JS fundamentals</a></li>
    <li><a href="#lab6-parallel-script">Vendor scripts (annotated)</a></li>
    <li><a href="#lab6-etl-walkthrough">ec2Name script (full)</a></li>
    <li><a href="#lab6-teaching-examples">Toy examples (do not run)</a></li>
  </ul>
  <p class="toc-title">Reference</p>
  <ul class="toc-list">
    <li><a href="#lab6-sources">Sources</a></li>
  </ul>
</nav>

## Prerequisites
{: #lab6-prerequisites}

Lab 5 minimum: one **`cmdb_ci_vm_instance`** (e.g. list **Name** `sgclab-app-01`, discovery source **SG-AWS**).

## At a glance — observed config and your next step
{: #lab6-at-a-glance}

| | |
|---|---|
| **Your next hands-on step** | Open ETL definition **`SG-AWS-EC2-Instance`** → **Virtual Machine Instance** → **View Mapping** ([below](#lab6-hands-on-etl)) |
| **Data source (load)** | **`SG-AWS-EC2`** — Type **Custom (Load by Script)** |
| **Staging table** | `sn_aws_integ_sg_aws_ec2`, column **`u_data`** (single-column JSON) |
| **Parallel loading** | **Enabled** on observed export — **do not change** for Lab 9; see [appendix pitfalls](#lab6-pitfalls) |
| **Batch import** | **Off** — batch size **1000** on form is **inactive** while off |
| **Incremental / last run** | **`use_last_run_datetime` = false** — no incremental claim from XML |
| **ETL (transform)** | **`SG-AWS-EC2-Instance`** — separate record from data source |
| **Lab 9 drift** | Re-run **`SG-AWS-EC2`** only — [Lab 9]({{ '/labs/09-drift-monitoring/' | relative_url }}) |

**Do not** edit vendor loader scripts or hardcoded `connection_alias_id` / `data_source_id` values to “switch” EC2 vs S3 or accounts — use supported **connection / schedule** configuration.

## Hands-on — read ETL mapping (Part A)
{: #lab6-hands-on-etl}

1. **All** → **IntegrationHub ETL** → **Configuration → IntegrationHub ETL**.
2. **CMDB Application: SG-AWS** → definition **`SG-AWS-EC2-Instance`** (ETL name, not the **`SG-AWS-EC2`** schedule).
3. **Map Data to CMDB** → **Virtual Machine Instance** card → **View Mapping**.

**Transform Map Assistant:** with no sample import set, mappings stay **read-only**. Do **not** pick **Select a Sample Import Set** or flip controls to edit for the minimum bar. **Add Attribute** (and similar edit controls) stay **greyed out** in this mode — that is **expected** without a sample import set, not proof you lack permissions.

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

**The final `ec2Name` value (and thus CMDB Name) is not `resourceId|tagsStr`.** It is the **Name** tag value **`trim`med** when parse succeeds, otherwise **`resourceId`** as fallback (empty **Name** tag can yield an empty string; multiple **Name** tags → last wins).

**`ec2SourceNativeKey`** uses a separate **concatenate** transform: `connection_alias_id`, `accountId`, `awsRegion`, `resourceId` with **`|`** delimiter.

![Name maps to object.ec2Name (configured mapping)]({{ '/assets/img/lab06/etl-vm-name-mapping.png' | relative_url }})
*Screenshot: **Target Name** ← **`object.ec2Name`**. Verifies **configuration** on this definition; not proof of a single import-row debug run.*

## What’s next for this lab

| You are here | Next step |
|---|---|
| **Part A done** (navigation + Name / Object ID / native key observed, read-only) | Continue to **[Lab 7 — CSDM and service graph]({{ '/labs/07-csdm-graph/' | relative_url }})** and link **`cmdb_ci_vm_instance`** under an application service |
| Want to **edit** a mapping | **Part B** below — own PDI, clone/customize only if your release supports it, one string field, **rollback** |

Part B remains **optional**; the curriculum does not require changing stock **`SG-AWS-EC2-Instance`** mappings.

---

## Loader ELI5 — required for [Lab 9]({{ '/labs/09-drift-monitoring/' | relative_url }})
{: #lab6-data-loader}

**Read-only.** Completing Lab 9 does **not** require changing parallel/batch/single-column settings, editing loader scripts, or running appendix toy code.

| Stage | ELI5 |
|---|---|
| **Load** | **`SG-AWS-EC2`** Custom script → staging table `sn_aws_integ_sg_aws_ec2`, column **`u_data`** |
| **Transform** | ETL **`SG-AWS-EC2-Instance`** (the mapping you opened above) |
| **Reconcile** | IRE |

| Observed on `SG-AWS-EC2` | Value |
|---|---|
| **Type** | Custom (Load by Script) |
| **Data in single column** | true |
| **Parallel loading** | true |
| **Use batch import** | false |
| **Use last run datetime** | false |

Deeper explanations, vendor script line tables, and **Optional — beyond this lab** examples: [Appendix](#lab6-appendix).

---

## Part B — Optional edit (own PDI only)
{: #lab6-part-b}

| Do | Don't |
|---|---|
| Clone/customize only if supported | Edit production stock definitions |
| One string field, re-import, revert | Break **Name** mapping “to learn” |
| Confirm VM list still **one** row | Leave experimental mappings on a shared instance |

## Checkpoint
{: #lab6-checkpoint}

<ul class="check">
<li>Opened <code>SG-AWS-EC2-Instance</code> read-only; <b>Virtual Machine Instance</b> → <b>View Mapping</b></li>
<li>Can point to <b>Name</b> ← <code>object.ec2Name</code>, <b>Object ID</b> ← <code>resourceId</code>, native key ← <code>ec2SourceNativeKey</code></li>
<li>Understand <code>ec2Name</code> is transform output, not a CMDB column; list <b>Name</b> is what landed on the VM</li>
<li><b>Add Attribute</b> greyed out without sample import set — expected for read-only observation</li>
<li>For Lab 9: know load → staging → ETL → IRE ([above](#lab6-data-loader)) — optional appendix only if curious</li>
</ul>

---

## Further details and alternative configurations
{: #lab6-appendix}

**Optional — beyond this lab.** Nothing here is required to complete Lab 6 or Lab 9. Do **not** toggle batch/parallel/single-column settings or paste toy scripts into **`SG-AWS-EC2`**.

### Observed data source field snapshot
{: #lab6-datasource-matrix}

| Field | Observed | Short note |
|---|---|---|
| **Name** | `SG-AWS-EC2` | Loader schedule — **not** ETL name |
| **Import set table** | `sn_aws_integ_sg_aws_ec2` | Staging **persists** until transform/cleanup |
| **Type** | Custom (Load by Script) | |
| **Data in single column** | true | **`u_data`** |
| **Enable parallel loading** | true | |
| **Use batch import** | false | Batch size **1000** on form ≠ active batching |
| **Use last run datetime** | false | No incremental load claim |
| **Imports** | `u_data` | |

### Data source Type dropdown
{: #lab6-datasource-types}

<details markdown="1">
<summary><strong>Beginner guide — why Custom (Load by Script) for SG-AWS-EC2</strong></summary>

On the data source form, **Type** chooses how rows enter staging. You may see:

| Type (UI) | Beginner meaning | SG-AWS EC2? |
|---|---|---|
| **None** | Placeholder / unset | No |
| **File** | Read a file | No |
| **JDBC** | Database query | No |
| **LDAP** | Directory | No |
| **OIDC** | Token/OIDC flow | No |
| **REST** | REST message | No |
| **IntegrationHub** | IntegrationHub spoke | No |
| **Data Stream** | Streaming integration | No |
| **Custom (Load by Script)** | Your JavaScript uses **`import_set_table`** APIs | **Yes** — `SG-AWS-EC2` |

Types are **not** interchangeable. The connector ships **Custom** loaders — do not flip to **File/REST** to “test” AWS.

</details>

### Parallel loading vs batch import vs concurrent transform
{: #lab6-parallel-vs-batch}

<details markdown="1">
<summary><strong>Three mechanisms — do not conflate</strong></summary>

| Mechanism | Product intent ([Custom Load by Script](https://www.servicenow.com/docs/r/zurich/integrate-applications/system-import-sets/custom-type-data-source.html)) | Not the same as |
|---|---|---|
| **Parallel loading** | Partition script → **`parallel_job_loader.add(...)`** → multiple Data Loader runs with **`partition_info`**; needs concurrent import + **Custom size** partition method | Guaranteed faster imports; proven “volume split” |
| **Use batch import** | How rows are chunked **into the import set** on load ( **`glide.import_set_load_usebatch`** may override UI) | Parallel partitions |
| **Concurrent import / transform** | **Concurrent Import Sets** jobs run transforms | One simultaneous write to **all** CMDB tables |

**Typical order (overlap possible):** schedule start → optional partition enqueue → Data Loader writes staging → transform → IRE.

**Checkbox UI:** Unchecking **Enable parallel loading** **hides** the parallel script field; it does **not** auto-delete stored script text.

</details>

### Staging API (`import_set_table`)
{: #lab6-staging-api}

<details markdown="1">
<summary><strong>Platform writer object (not GlideRecord)</strong></summary>

**`import_set_table`** is a **platform-provided writer API** for the loader — **not** a `GlideRecord` you query by hand.

Documented methods ([Zurich doc](https://www.servicenow.com/docs/r/zurich/integrate-applications/system-import-sets/custom-type-data-source.html)):

| Method | What it does |
|---|---|
| **`addJSONColumn(label, maxLength?)`** | Registers a JSON column on the **staging writer for this load** — aligns with **Data in single column** on the data source; **not** “create a brand-new physical DB table column every run” in everyday terms |
| **`addColumn`** | String column on staging writer |
| **`insert(rowData)`** | One staging row map |
| **`getMaximumRows()`** | **20** for “Test load 20 records”; otherwise **-1** |

There is **no** documented **`addRow`**. Use **`insert`**.

**Single-column JSON:** With **Data in single column** = true, vendor script calls `addJSONColumn('u_data')` then helper code inserts JSON — exact **`maxLength`** on observed script omitted; confirm on your release ([create custom data source](https://www.servicenow.com/docs/r/xanadu/integrate-applications/system-import-sets/create-custom-type-data-source.html)).

</details>

### Pitfalls — do not assume
{: #lab6-pitfalls}

<details markdown="1">
<summary><strong>Common over-claims when reading vendor loaders</strong></summary>

| Claim | Safer reading |
|---|---|
| **`getAccountPartitions()` splits by volume for speed** | **Not proven** here — vendor helper; may be account-scoped or connector-specific |
| **`connection_alias_id` in script = AWS account ID** | **No** — ServiceNow **connection alias** sys_id from **your** export; **one-account** not guaranteed by script text |
| **Change hardcoded IDs / swap helper class → EC2 vs S3** | **Do not** — use supported connector connections & schedules |
| **`last_success_import_time` + XML `use_last_run_datetime: false`** | **No incremental load claim**; parameter **unused** in observed parallel script |
| **`!gs.nil(partitions)` means non-empty array** | **`gs.nil([])`** is often **false** in Rhino — **`[]`** → loop runs **0** times; **not** same as explicit `.length` check |
| **`throw '…'` in parallel script** | **`catch` logs `gs.error` only — no rethrow** → scheduler may **not** mark run failed |
| **`SgAwsEC2InstanceDataSourceUtils.loadData`** | **Source not in repo** — do **not** claim “direct AWS API” vs **AWS Config** vs connector HTTP |
| **`partition_info` shape** | Must match what **`parallel_job_loader.add`** queued — **verify** compatibility on PDI |

</details>

### JavaScript fundamentals
{: #lab6-js-fundamentals}

<details markdown="1">
<summary><strong>IIFE, gs.nil, and unused parameters</strong></summary>

| Idea | In these scripts |
|---|---|
| **IIFE** | `(function …)(args)` — platform calls immediately with injected parameters |
| **`new Scope.Class(args)`** | Vendor classes in **`sn_aws_integ`** package |
| **`JSON.stringify` for `add`** | Observed string partition payload — match platform expectations for **`partition_info`** |
| **`gs.nil(x)`** | Null/empty guard — see [pitfalls](#lab6-pitfalls) for arrays |
| **Unused formals** | `data_source`, `import_log`, `last_success_import_time` passed but unused in parallel snippet |

</details>

### Vendor scripts — observed export (do not edit)
{: #lab6-parallel-script}

Exact text as observed. **Teaching comments** are for reading only — **not** a vendor patch.

<details markdown="1">
<summary><strong>Parallel loading script — readable comments + line table</strong></summary>

```javascript
(function loadTasks(parallel_job_loader, data_source, import_log, last_success_import_time) {
  // IIFE: platform passes parallel_job_loader, data_source, import_log, last_success_import_time.
  // last_success_import_time is unused here; data source XML has use_last_run_datetime = false.
  try {
    var args = {
      connection_alias_id: 'c3f0b8c453b32010c23bddeeff7b12ee', // YOUR instance's alias sys_id — not AWS account id
      data_source_id: 'f4879d5253203010a3e4ddeeff7b122c'       // THIS data source record sys_id
    };
    var sgAwsParallelLoading = new sn_aws_integ.SgAwsParallelLoading(args); // vendor helper — internals unknown
    var partitions = sgAwsParallelLoading.getAccountPartitions(); // NOT proven: count/volume/speed guarantees
    if (!gs.nil(partitions)) { // NOT the same as partitions.length > 0 — see pitfalls
      for (var partIndex = 0; partIndex < partitions.length; partIndex++) {
        parallel_job_loader.add(JSON.stringify(partitions[partIndex])); // doc: add(partitionInfo); string observed
      }
    } else {
      throw 'Parallel loading partition is empty'; // string throw — caught below, not rethrown
    }
  } catch (ex) {
    gs.error('SG-AWS-EC2 : Parallel loading script error: ' + ex); // log only — run may still look "OK" in UI
  }
})(parallel_job_loader, data_source, import_log, last_success_import_time);
```

| Line / block | Verified fact | Do not assume |
|---|---|---|
| **`args` IDs** | Instance-specific export | Swapping IDs retargets connection/source safely without admin |
| **`getAccountPartitions`** | Called once per parallel script run | Always >1 partition; faster than single load |
| **`parallel_job_loader.add(JSON.stringify(...))`** | Observed pattern | Always object, never string |
| **`catch`** | Writes **`gs.error`** | Scheduler always fails the job |

</details>

<details markdown="1">
<summary><strong>Data Loader script — readable comments + line table</strong></summary>

```javascript
(function loadData(import_set_table, partition_info) {
  // import_set_table = platform staging writer API (not GlideRecord).
  import_set_table.addJSONColumn('u_data'); // declare JSON staging column for this load (see product doc)
  var args = {
    connection_alias_id: 'c3f0b8c453b32010c23bddeeff7b12ee',
    data_source_id: 'f4879d5253203010a3e4ddeeff7b122c',
    partition_info: partition_info // set when invoked from a parallel partition job
  };
  new SgAwsEC2InstanceDataSourceUtils(args).loadData(import_set_table); // vendor — AWS path not verified in repo
})(import_set_table, partition_info);
```

| Line | Verified | Not in this snippet |
|---|---|---|
| **`addJSONColumn('u_data')`** | Matches **Data in single column** / **Imports** | CMDB **`cmdb_key_value`** mapping |
| **`loadData(...)`** | Writes staging rows | ETL transform |

</details>

### Optional — beyond this lab: toy examples (never paste into SG-AWS-EC2)
{: #lab6-teaching-examples}

**Not required** for Lab 6 or Lab 9. **Do not execute** against connector data sources.

<details markdown="1">
<summary><strong>Minimal pattern from product documentation (synthetic data)</strong></summary>

Illustrates **`insert`** after **`addJSONColumn`** — from [Custom (Load by Script)](https://www.servicenow.com/docs/r/zurich/integrate-applications/system-import-sets/custom-type-data-source.html), **not** connector code.

```javascript
(function loadData(import_set_table) {
  import_set_table.addJSONColumn('u_data', 64000);
  import_set_table.insert({ u_data: JSON.stringify({ labOnly: true }) });
})(import_set_table);
```

</details>

<details markdown="1">
<summary><strong>Optional — beyond this lab: defensive partition sketch (not vendor code)</strong></summary>

Shows explicit empty-array handling — **do not** replace installed connector scripts.

```javascript
(function loadTasks(parallel_job_loader) {
  var partitions = []; // placeholder — real code uses vendor helper
  if (gs.nil(partitions) || partitions.length === 0) {
    gs.error('Example: no partitions');
    return;
  }
  for (var i = 0; i < partitions.length; i++) {
    parallel_job_loader.add(partitions[i]); // product doc example often uses object — verify your release
  }
})(parallel_job_loader);
```

</details>

**Mapping trace:** **`tagsStr`** vs **`tags`** on ETL — **pending** import-row evidence ([Lab 9]({{ '/labs/09-drift-monitoring/' | relative_url }})).

### ec2Name transform — full script walkthrough
{: #lab6-etl-walkthrough}

<details markdown="1">
<summary><strong>Optional — beyond this lab: how <code>ec2Name</code> becomes CMDB <code>Name</code></strong></summary>

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

---

## Sources
{: #lab6-sources}

| Topic | URL |
|---|---|
| Custom (Load by Script) — Data Loader & parallel | https://www.servicenow.com/docs/r/zurich/integrate-applications/system-import-sets/custom-type-data-source.html |
| Create Custom data source fields (batch / parallel) | https://www.servicenow.com/docs/r/xanadu/integrate-applications/system-import-sets/create-custom-type-data-source.html |

---

Next: [Lab 7 — CSDM and the service graph]({{ '/labs/07-csdm-graph/' | relative_url }}) · Drift: [Lab 9]({{ '/labs/09-drift-monitoring/' | relative_url }}) (skips optional Lab 8)
