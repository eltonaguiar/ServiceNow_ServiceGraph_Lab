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

<div class="note">
<span class="label">Read this before you start</span>
<p>This lab is <strong>optional and deliberately lighter than the AWS track</strong>. Labs 1–7
built an AWS inventory step by step, with a verifier, an IRE deep-dive and an ETL edit. Azure
gets one page, because by now you already know what a connector does — the only new idea here
is <em>two sources disagreeing</em>, and that idea takes ten minutes, not two hours.</p>
<p>You can skip it entirely and the lab still teaches its core lesson. If you do run it, treat
Labs 1–4 as your reference for where each screen lives; do not expect a parallel Lab 1–7.</p>
</div>

## 1. Azure side: service principal

1. Azure Portal → **Microsoft Entra ID → App registrations → New registration**
   → name `servicenow-sgc-lab`, single tenant.
2. Note **Application (client) ID** and **Directory (tenant) ID**.
3. **Certificates & secrets → New client secret** → copy the **value** immediately.
4. **Subscriptions → your subscription → Access control (IAM) → Add role assignment**
   → role **Reader** → assign to the app registration.

### If you want real Azure data

An empty subscription still imports account-level CIs, which is enough to see multisource
behaviour — but a VM makes the disagreement visible:

1. **Virtual machines → Create** → image **Ubuntu Server 24.04 LTS**, size **`B1s`** (the
   smallest, cheapest burstable size).
2. Create a new resource group in a region near you; tags: `Environment=lab`, `Owner=yourname`.
3. Inbound ports: **None**. No public IP.
4. After it exists, **Stop (deallocate)** it — a deallocated VM still exists as an inventory
   object and stops compute billing. "Stopped" without deallocation keeps paying for the disk
   and IP.
5. Delete the resource group in [Lab 11]({{ '/labs/11-cleanup/' | relative_url }}).

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

### Azure connection failures, specifically

Azure fails differently from AWS, and the error text is unhelpful:

| Error / symptom | Cause | Fix |
|---|---|---|
| `AuthorizationFailed` | Role assigned to the **app registration** instead of the **enterprise application** service principal, or assigned at the wrong scope | Re-assign **Reader** at the **subscription** scope to the enterprise application |
| `InvalidAuthenticationToken` / `AADSTS…` | Wrong **tenant ID**, or the app is single-tenant but the credential points at another directory | Copy the tenant ID from **Entra ID → Overview**, not from the app blade |
| Authentication fails although the secret is "correct" | You copied the **Secret ID** instead of the **Value** | The value is only visible once, at creation. Create a new secret |
| Secret worked, then stopped | Client secrets **expire** (12–24 months) | Note the expiry date; create a second secret before it lapses |
| Test passes but zero CIs | Subscription has no resources, or the connector's schedule was never executed | Create the `B1s` VM above, then **Execute Now** |
| Only some resource types appear | Connector version covers a subset of Azure resource types | Read the app's **Dependencies**/documentation; this is not a config error |

For genuinely shared assets, the correct pattern is a shared identifier (asset tag, FQDN, or a
CMDB-managed correlation id) plus an explicit precedence rule — not hoping IRE guesses.

## Checkpoint

<ul class="check">
<li>Azure connection test passes and CIs were imported</li>
<li>You can show a multisource attribute view with both sources</li>
<li>You changed a reconciliation precedence and proved the CI value followed it</li>
</ul>

Next: [Lab 9 — drift and monitoring]({{ '/labs/09-drift-monitoring/' | relative_url }})
