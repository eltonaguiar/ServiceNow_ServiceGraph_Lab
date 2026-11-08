---
layout: default
title: Drift and monitoring
lab: 9
time: 45 min
level: Operations
order: 9
permalink: /labs/09-drift-monitoring/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>Your lab server in <strong>Amazon Web Services (AWS)</strong> is like a labeled folder in the cloud. The <strong>Service Graph Connector</strong> copies that folder’s <strong>labels and facts</strong> into ServiceNow’s <strong>CMDB</strong> (a catalog of “what exists”). <strong>Drift</strong> means you changed the real label in AWS and ask: did ServiceNow’s copy catch up? This lab changes one tag on purpose, runs <strong>one</strong> EC2 import, and inspects results — it does <strong>not</strong> prove perfect graphs, notifications, or that every field updates.</p>
</div>

<nav class="toc" aria-label="Lab 9 contents">
  <p class="toc-title">Required path</p>
  <ul class="toc-list">
    <li><a href="#lab9-prerequisites">Prerequisites & path</a></li>
    <li><a href="#lab9-loaders">Loader ELI5 (Lab 6)</a></li>
    <li><a href="#lab9-schedule-context">SG-AWS schedules (observed names)</a></li>
    <li><a href="#lab9-observed-experiment">Observed experiment (t608)</a></li>
    <li><a href="#lab9-tag-drift-lesson">Tag vs VM field drift</a></li>
    <li><a href="#lab9-rollback">Rollback (observed t637)</a></li>
    <li><a href="#lab9-freshness">Freshness filter (observed t637)</a></li>
    <li><a href="#lab9-screenshots">Screenshots (not in repo)</a></li>
    <li><a href="#lab9-checkpoint">Checkpoint</a></li>
    <li><a href="#lab9-glossary">Glossary</a></li>
    <li><a href="#lab9-sources">Sources</a></li>
  </ul>
  <p class="toc-title">Deep dive (optional)</p>
  <ul class="toc-list">
    <li><a href="{{ '/labs/06-etl-mappings/' | relative_url }}#lab6-appendix">Lab 6 appendix — loaders & scripts</a></li>
  </ul>
</nav>

## Prerequisites and curriculum path
{: #lab9-prerequisites}

| Item | Requirement |
|---|---|
| **Labs 1–7** | Connector, IRE, ETL read, CSDM stack |
| **Lab 6** | **[Data loader fundamentals]({{ '/labs/06-etl-mappings/' | relative_url }}#lab6-data-loader)** — **read before** this lab |
| **Lab 8 (Azure multisource)** | **Skipped** is OK — this lab uses **AWS only** |
| **AWS** | Lab stack still present; **`sgclab-app-01`** may be **stopped** — valid for tag drift |

**Do not** modify vendor loader scripts, parallel flags, or parent schedules just to test drift.

## Read loaders first (canonical)
{: #lab9-loaders}

Drift experiments fail when you only stare at **`cmdb_ci_vm_instance`**. The connector path is:

**Execute Now** on **`SG-AWS-EC2`** → staging **`u_data`** → ETL **`SG-AWS-EC2-Instance`** → **IRE** → CMDB.

| Required reading | Optional |
|---|---|
| [Lab 6 — Loader ELI5]({{ '/labs/06-etl-mappings/' | relative_url }}#lab6-data-loader) (short table + observed flags) | [Lab 6 appendix]({{ '/labs/06-etl-mappings/' | relative_url }}#lab6-appendix) — vendor scripts, pitfalls, **toy examples (do not run)** |

**Lab 9 does not require** changing parallel/batch/single-column settings, editing loader scripts, or running appendix sample code.

---

## SG-AWS schedules — observed sibling names (not “hardware import”)
{: #lab9-schedule-context}

On one PDI, **Organization** parent and siblings (release/order may differ):

| Schedule / source (observed) | Notes |
|---|---|
| **`SG-AWS-Organization`** | **Inactive** — left inactive; **do not** enable parent chain for this experiment |
| **`SG-AWS-Tags`** | Order **320** |
| **GenericTags** (name as shown) | Order **390** |
| **`SG-AWS-EC2`** | Order **180** — **only** schedule executed in observed run |
| **Hardware-Type** (name as shown) | Order **200** |

**Wording fix:** Older drafts said “hardware import” — use the **exact** schedule names on **your** instance.

**For tag-only drift on one VM:** Observed run needed **`SG-AWS-EC2` Execute Now** only — **no** separate **Tags** run for the **`Environment`** tag update on **`cmdb_key_value`**.

---

## Observed drift experiment (t608 / t636)
{: #lab9-observed-experiment}

**AWS change (one-time):** EC2 **`sgclab-app-01`** remained **stopped**; tag **`Environment`** changed **`lab` → `drift-test`**; all else unchanged per parent report.

**ServiceNow action:** **Execute Now** on data source / schedule **`SG-AWS-EC2`** only.

### Execution identifiers (observed)

| Artifact | Value |
|---|---|
| **Execution** | **EXE00001018** |
| **Concurrent import / sets** | Parent **CISET0010011**; children **ISET0010034** (one row), **ISET0010035** (empty) — **both** processed |
| **Histories** | Complete, **0 errors**; summary **total 1**, **inserts 0**, **updates 2** |

### Transform / CMDB counters (summary line — read with care)

| Target | Observed summary |
|---|---|
| **`cmdb_ci_vm_instance`** | unchanged **2** |
| **`cmdb_ci_os_template`** | updated **1** |
| **`cmdb_key_value`** | unchanged **7**, **updated 1** |
| **Storage** | warnings **1**, partial **1** |
| **Relationships** | warnings **3**, partial **3** |
| **NIC** | warnings **2**, partial **2** |
| Other classes | unchanged |

### Import-set payload (one row — teaching facts)

| Field in payload | Observed |
|---|---|
| **`tags`** | Includes **`Environment` = `drift-test`** |
| **`resourceId`** | `i-0c9860cc1569c41a4` (lab instance) |
| **`cpuState`** | **stopped** |

**Empty Target record** on an import row: **normal** on multi-target transforms — **not** proof the run failed.

### CMDB verification (observed — screenshot not in repo)

**`cmdb_key_value`** for CI **`sgclab-app-01`**: **Key** **Environment**, **Value** **`drift-test`**. **t636** transform summary on the observed run: **`cmdb_key_value`** **unchanged 7**, **updated 1**. User-verified on the PDI; no Lab 9 PNG is published yet ([note](#lab9-screenshots)).

---

## Tag drift lesson — key/value vs VM column
{: #lab9-tag-drift-lesson}

| Question | Observed answer |
|---|---|
| Did **`Environment: drift-test`** appear in CMDB? | **Yes** — on **`cmdb_key_value`** linked to **`sgclab-app-01`** |
| Did **`cmdb_ci_vm_instance`** gain a new **Environment** column value? | **Unchanged** count on VM class in summary — do not assume a VM scalar field moved |
| Do you need **`SG-AWS-Tags`** for this observation? | **No** for this run — EC2 load carried tag JSON in **`u_data`** |
| Does ETL **`ec2Name` / `tagsStr`** proof exist here? | **Pending** — open **ETL map** [`SG-AWS-EC2-Instance`]({{ '/labs/06-etl-mappings/' | relative_url }}#lab6-read-mappings); do not assert **`tagsStr`** vs **`tags`** until import-row evidence is captured |

**Honest scope:** One tag change + one EC2 import **does not** prove full staleness monitoring, notifications, or clean NIC/storage graphs.

---

## Rollback to lab tags (observed t637)
{: #lab9-rollback}

On the reported PDI (**t637**): AWS tag **`Environment`** returned to **`lab`**, **`SG-AWS-EC2`** was run again, and **`cmdb_key_value`** was re-verified. **Rollback is complete** on that instance — do not treat older **t608-only** notes as “rollback still pending.”

---

## Freshness filter and run monitoring (observed t637)
{: #lab9-freshness}

On the reported PDI (**t637**): a **source-aware** personal saved filter for stale connector CIs was saved (**`last_discovered` > 7 days** plus discovery-source constraints — exact query varies by instance).

Habits you may still extend on your own PDI:

- **`scripts/verify_cmdb.py --stale-days 7`**
- **Concurrent Import Sets** / **Transform Histories** when reviewing imports ([Lab 4]({{ '/labs/04-run-import/' | relative_url }}))

---

## Screenshots (not in repo)
{: #lab9-screenshots}

This lab has **no** published PNGs under `assets/img/lab09/` ([live page](https://eltonaguiar.github.io/ServiceNow_ServiceGraph_Lab/labs/09-drift-monitoring/) is text and tables only). Drift, rollback, execution history, and the saved freshness filter were **verified in the UI** on the reported PDI; **missing screenshots are a publishing gap, not proof those steps were skipped.**

---

## Checkpoint
{: #lab9-checkpoint}

<ul class="check">
<li><b>Done (t608 / t636):</b> AWS tag <code>lab</code> → <code>drift-test</code>; <b>SG-AWS-EC2</b> only; <code>cmdb_key_value</code> <b>updated 1</b>; run <b>0 errors</b></li>
<li><b>Done (t637):</b> Rollback <code>drift-test</code> → <code>lab</code>; CMDB re-verified</li>
<li><b>Done (t637):</b> Source-aware <b>7-day</b> stale-CI filter saved</li>
<li><b>Done (reading):</b> Loader → staging → ETL → IRE via <a href="{{ '/labs/06-etl-mappings/' | relative_url }}#lab6-data-loader">Lab 6</a></li>
<li><b>Optional depth:</b> ETL / <code>tagsStr</code> mapping trace on your instance</li>
</ul>

**Screenshots** for the steps above are still **not** in the repo — add privacy-reviewed captures when available; do not substitute other labs’ PNGs.

Next: [Lab 10 — troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }}) (when checkpoints above are honest for you)

---

## Glossary
{: #lab9-glossary}

| Term | Meaning |
|---|---|
| **AWS** | Amazon Web Services — cloud provider for the lab VM |
| **CMDB** | Configuration Management Database — ServiceNow inventory tables |
| **Data Loader** | Script that writes **import set** staging rows ([Lab 6]({{ '/labs/06-etl-mappings/' | relative_url }}#lab6-data-loader)) |
| **Drift** | Real infrastructure changed; CMDB may lag or partially update |
| **ETL** | Extract–Transform–Load — connector maps staging → CMDB columns |
| **IRE** | Identification and Reconciliation Engine — insert/update decisions |
| **Import set** | Staging table (e.g. `sn_aws_integ_sg_aws_ec2`) before CMDB commit |
| **SGC** | Service Graph Connector — ServiceNow AWS integration product |
| **`cmdb_key_value`** | Table storing tag-like key/value pairs attached to CIs |
| **`u_data`** | JSON column on EC2 import set rows |

---

## Sources
{: #lab9-sources}

| Topic | URL |
|---|---|
| Custom (Load by Script) / parallel loading | https://www.servicenow.com/docs/r/zurich/integrate-applications/system-import-sets/custom-type-data-source.html |
| Data source field definitions (batch import) | https://www.servicenow.com/docs/r/xanadu/integrate-applications/system-import-sets/create-custom-type-data-source.html |
| Lab 6 loader section (canonical) | {{ '/labs/06-etl-mappings/' | relative_url }}#lab6-data-loader |
