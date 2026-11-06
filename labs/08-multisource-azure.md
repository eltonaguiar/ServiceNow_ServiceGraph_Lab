---
layout: default
title: Multisource CMDB with Azure
lab: 8
time: 40 min
level: Advanced
order: 8
permalink: /labs/08-multisource-azure/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>Two cloud providers describe the same kind of thing. Something has to decide whose answer wins — that something is a reconciliation rule, and you get to set it.</p>
</div>

## Objective

Add a second cloud source describing the same class of CI (Configuration Item), then decide — explicitly — which
source's data wins. This is the difference between a CMDB and a spreadsheet.

## 1. Azure side: service principal

1. Azure Portal → **Microsoft Entra ID → App registrations → New registration**
   → name `servicenow-sgc-lab`, single tenant.
2. Note **Application (client) ID** and **Directory (tenant) ID**.
3. **Certificates & secrets → New client secret** → copy the **value** immediately.
4. **Subscriptions → your subscription → Access control (IAM) → Add role assignment**
   → role **Reader** → assign to the app registration.

Optionally create one small free-tier-eligible VM (`B1s`) in one resource group so there is
real data. Deallocate it when done.

## 2. ServiceNow side: install and connect

1. **System Applications → All Available Applications** → search **Service Graph Connector for
   Microsoft Azure** (plugin id like `sn_sg_azure_integ`). Install with dependencies.
2. Open its **Guided Setup** (or SGC Central).
3. Create the hardware connection:

| Field | Value |
|---|---|
| Tenant ID | from step 1.2 |
| Client ID | from step 1.2 |
| Client secret | from step 1.3 |
| Connection URL | usually pre-filled (`https://management.azure.com`) |

4. **Test connection**, then **Execute Now** on the Azure hardware schedule.
5. Confirm Azure CIs exist — Azure VMs land in `cmdb_ci_vm_instance` or a cloud-specific
   subclass.

## 3. Force the interesting case

Both connectors can describe the same logical thing (a VM). The questions to answer:

1. Open **Configuration → CMDB → Multisource → CMDB 360** (or **CMDB 360** / **Multisource
   CMDB** module on your release).
2. Pick a CI class where you have data from more than one source and open a record's
   **source-by-source attribute view**. You will see AWS and Azure disagreeing about, for
   example, the name or environment.
3. Find **Reconciliation rules** (CI Class Manager → class → **Reconciliation**, or
   **CMDB → Reconciliation Rules**): note which data source has precedence and whether the
   rule is per class, per attribute, or per source order.
4. Change the precedence so the other source wins for one attribute, re-run both imports, and
   confirm the CMDB value changed to match the new rule.

## 4. What "good" looks like

| Symptom | Diagnosis |
|---|---|
| Two separate CIs for one VM | Identification did not match — different identifiers per cloud, works as designed for distinct assets |
| One CI, attributes flickering between runs | Both sources update the same attribute and precedence is unstable |
| Azure CIs absent | Service principal lacks Reader, or the connector's schedules never ran |

For genuinely shared assets, the correct pattern is a shared identifier (asset tag, FQDN, or a
CMDB-managed correlation id) plus an explicit precedence rule — not hoping IRE guesses.

## Checkpoint

<ul class="check">
<li>Azure connection test passes and CIs were imported</li>
<li>You can show a multisource attribute view with both sources</li>
<li>You changed a reconciliation precedence and proved the CI value followed it</li>
</ul>

Next: [Lab 9 — drift and monitoring]({{ '/labs/09-drift-monitoring/' | relative_url }})
