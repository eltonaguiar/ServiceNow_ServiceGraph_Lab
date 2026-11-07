---
layout: default
title: Service Graph Lab
order: -3
permalink: /
---

<p class="hero">Put real cloud infrastructure into a real CMDB</p>

A hands-on lab that takes you from an empty free-tier **AWS** (Amazon Web Services) account to
EC2 servers, VPC networks and a working service model inside a ServiceNow **CMDB**
(Configuration Management Database) — reconciled by **IRE** (Identification and Reconciliation
Engine).

Everything runs on a free **PDI** (Personal Developer Instance) and a free-tier AWS account.
No **MID Server** (the on-premises agent ServiceNow normally needs), no paid licence, no private
infrastructure.

<div style="border: 2px solid #d73a49; border-radius: 6px; padding: 12px 16px; margin: 16px 0; background: #fff5f5; color: #24292e;">
<p style="margin: 0; font-weight: bold; color: #cb2431;">⚠️ Cost warning — this lab may not be completely free</p>
<p style="margin: 8px 0 0 0; color: #24292e;">AWS and Azure can charge by the hour for a running VM, a public IP, and a disk. On a new account these amounts are usually only cents to a dollar for a short lab, and are often covered by free-tier credits — but they are not guaranteed to be zero. Set the budget alarm immediately, stop or deallocate resources the same day, and delete the stack when you finish. See the <a href="{{ '/labs/00-prerequisites/' | relative_url }}">Prerequisites</a> page for the full cost breakdown.</p>
</div>

<div class="eli5">
<span class="label">ELI5 — what is this lab actually about?</span>
<p>Companies keep a list of every computer they own and what depends on what. That list is
usually maintained by hand, so it is out of date and nobody trusts it.</p>
<p>This lab fixes that for a cloud account: AWS is asked what exists, the answer is loaded into
ServiceNow automatically, ServiceNow decides which items are new versus already known, and you
group them into a "service" so you can answer <em>"if this server dies, what breaks?"</em></p>
<p>That is it. Every term is explained in the <a href="{{ '/basics/' | relative_url }}">Primer</a>
if any of the words above are unfamiliar.</p>
</div>

## Why this lab exists — and how it differs from ServiceNow's own Learning content

ServiceNow's official training is organised as **courses**: you watch a module, answer a check,
and move on. That teaches the vocabulary well, but it deliberately keeps the environment abstract —
the examples are shared, nothing you build survives the module, and the hands-on pieces run in a
provided simulation or a licensed lab instance that you do not control.

The gap this lab fills is the one between *"I understand what a CMDB is"* and *"I have a CMDB that
found my servers by itself."* Everything here is built to be **run**, on your own free PDI, in one
sitting.

| | ServiceNow Learning course | This lab |
|---|---|---|
| **Starting point** | A module outline and a shared demo instance | Empty PDI plus one CloudFormation stack that creates real, tagged EC2 + VPC resources for something to discover |
| **What you type** | Follow-along steps that get reset | A read-only IAM policy, a credentials record, and a schedule — then you check the result with numbers |
| **Artifacts you keep** | Notes | The CloudFormation template, tagging plan, least-privilege IAM JSON, ETL mapping diffs and verification queries, all in [the repo](https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab) |
| **Proof it worked** | A multiple-choice check | Record counts before/after, an IRE outcome table (inserted vs updated vs skipped) you read and explain yourself, and a drift experiment where you terminate an instance and watch the CMDB react |
| **When it breaks** | Search the community forum | [Lab 10]({{ '/labs/10-troubleshooting/' | relative_url }}) is a matrix of every failure mode this lab actually hits — store install, IAM, connection test, empty import, duplicate CIs — each with the fix |
| **Time to first CI** | Hours of modules before a CMDB appears | **~40 minutes** (Labs 0–4), or ~1 hour on the no-Store fallback |
| **How far it goes** | Stops when the import runs | Continues into IRE identification rules, a CSDM application service over real CIs, AWS-vs-Azure source precedence, and drift monitoring |
| **Cost** | Depends on the lab entitlement | Free-tier AWS only; nothing chargeable is left running after Lab 11 |

Two things this lab is **not**: it is not exam prep, and it is not a reference architecture. The
free-tier AWS account is a teaching environment, not a production design — the point is that you
finish with a working pattern you have personally operated end to end, so the product documentation
and the certification material have something concrete to attach to.

## New to the vocabulary?

Two pages exist so you never have to guess:

<div class="grid">
  <a class="card" href="{{ '/basics/' | relative_url }}"><b>Primer — every term in plain English</b><span>What AWS, Azure, a CMDB, a CI, a CI class, IRE, ETL, CSDM and a Service Graph Connector are — plus a full abbreviation glossary</span></a>
  <a class="card" href="{{ '/integration-methods/' | relative_url }}"><b>Integration methods compared</b><span>Does this cover IntegrationHub and IRE? Why use a Service Graph Connector? What else could you use instead?</span></a>
</div>

## The lab sequence

<div class="grid">
  <a class="card" href="{{ '/labs/00-prerequisites/' | relative_url }}"><b>0 · Prerequisites</b><span>PDI, AWS account, budget alarm — 15 min</span></a>
  <a class="card" href="{{ '/labs/01-aws-inventory/' | relative_url }}"><b>1 · Real AWS inventory</b><span>Tagged EC2 + VPC via CloudFormation — 20 min</span></a>
  <a class="card" href="{{ '/labs/02-sgc-install/' | relative_url }}"><b>2 · Install the connector</b><span>Service Graph Connector for AWS — 20 min</span></a>
  <a class="card" href="{{ '/labs/03-iam-connection/' | relative_url }}"><b>3 · Read-only IAM + connection</b><span>Access key, credentials record, test — 20 min</span></a>
  <a class="card" href="{{ '/labs/04-run-import/' | relative_url }}"><b>4 · Run the import</b><span>Schedules, VPC evidence + basic PoC map — 45 min</span></a>
  <a class="card" href="{{ '/labs/05-ire/' | relative_url }}"><b>5 · IRE results</b><span>Identification rules, duplicates, outcomes — 30 min</span></a>
  <a class="card" href="{{ '/labs/06-etl-mappings/' | relative_url }}"><b>6 · ETL mappings</b><span>Change a mapping, add a field, re-import — 30 min</span></a>
  <a class="card" href="{{ '/labs/07-csdm-graph/' | relative_url }}"><b>7 · CSDM + service graph</b><span>Application service over real CIs — 30 min</span></a>
  <a class="card" href="{{ '/labs/08-multisource-azure/' | relative_url }}"><b>8 · Multisource CMDB</b><span>Add Azure, force a reconciliation decision — 40 min</span></a>
  <a class="card" href="{{ '/labs/09-drift-monitoring/' | relative_url }}"><b>9 · Drift + monitoring</b><span>Terminate an instance, watch the CMDB react — 25 min</span></a>
  <a class="card" href="{{ '/labs/10-troubleshooting/' | relative_url }}"><b>10 · Troubleshooting</b><span>Every failure mode this lab hits — reference</span></a>
  <a class="card" href="{{ '/labs/11-cleanup/' | relative_url }}"><b>11 · Cleanup</b><span>Revoke keys, delete the stack, cost = $0</span></a>
</div>

## What you end up with

- `cmdb_ci_vm_instance` for your lab EC2 (AWS connector path) — `object_id` is the real `i-…` id
- Account, datacenter, **cloud network** (VPC), subnet, and security-group CIs from scheduled imports
- Relationships between the instance, the VPC and your application service
- An IRE result set you can read and explain: inserted vs updated vs skipped, and why
- A reconciliation precedence rule that decides which source wins when AWS and Azure disagree

## Two paths, same destination

| Path | Use when | Time |
|---|---|---|
| **A — Service Graph Connector for AWS** (Labs 2–9) | The Store app installs on your PDI. This is the real product experience. | ~3.5 h |
| **B — Fallback via the IRE REST API** ([no-Store fallback]({{ '/labs/fallback-ire-api/' | relative_url }})) | Your PDI cannot install the Store app, or IntegrationHub is not entitled. Same CIs, same IRE, hand-fed. | ~1 h |

Start with Lab 0 either way. If the install fails at Lab 2, take the fallback and come back —
the IRE concepts in Labs 5–7 are identical.

## Ground rules

- Everything is **free tier**. The only chargeable item is the EC2 instance from Lab 1, and
  `t3.micro` is free-tier eligible for a limited monthly allowance in a new account. Lab 11
  deletes it.
- **Never commit AWS keys.** The lab creates them, uses them in one ServiceNow form, and
  revokes them in Lab 11.
- A PDI hibernates after inactivity and its URL can change. Re-wake it at
  [developer.servicenow.com](https://developer.servicenow.com) and update your notes. Mid-lab
  recovery steps are in [Lab 0]({{ '/labs/00-prerequisites/' | relative_url }}).
- The AWS track assumes a **reasonably recent PDI release** where the Service Graph Connector
  for AWS is exposed. Older instances may only offer the fallback — that is expected, not a
  mistake in your setup.
- The site is documentation; the scripts and the CloudFormation template live in the
  [repo](https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab). Clone it once in Lab 0.
- Stuck in the first hour? The [Troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }})
  page opens with the four failures that stop most people.
