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
  <a class="card" href="{{ '/labs/04-run-import/' | relative_url }}"><b>4 · Run the import</b><span>Schedules, first CIs, verify with numbers — 20 min</span></a>
  <a class="card" href="{{ '/labs/05-ire/' | relative_url }}"><b>5 · IRE results</b><span>Identification rules, duplicates, outcomes — 30 min</span></a>
  <a class="card" href="{{ '/labs/06-etl-mappings/' | relative_url }}"><b>6 · ETL mappings</b><span>Change a mapping, add a field, re-import — 30 min</span></a>
  <a class="card" href="{{ '/labs/07-csdm-graph/' | relative_url }}"><b>7 · CSDM + service graph</b><span>Application service over real CIs — 30 min</span></a>
  <a class="card" href="{{ '/labs/08-multisource-azure/' | relative_url }}"><b>8 · Multisource CMDB</b><span>Add Azure, force a reconciliation decision — 40 min</span></a>
  <a class="card" href="{{ '/labs/09-drift-monitoring/' | relative_url }}"><b>9 · Drift + monitoring</b><span>Terminate an instance, watch the CMDB react — 25 min</span></a>
  <a class="card" href="{{ '/labs/10-troubleshooting/' | relative_url }}"><b>10 · Troubleshooting</b><span>Every failure mode this lab hits — reference</span></a>
  <a class="card" href="{{ '/labs/11-cleanup/' | relative_url }}"><b>11 · Cleanup</b><span>Revoke keys, delete the stack, cost = $0</span></a>
</div>

## What you end up with

- `cmdb_ci_ec2_instance` records created by the **Service Graph Connector** — each identified by
  its real AWS instance ID (`i-…`), not typed in by hand
- A `cmdb_ci_cloud_service_account` for your AWS account, plus VPC records the connector found
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
