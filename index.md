---
layout: default
title: Service Graph Lab
order: -1
permalink: /
---

# Put real AWS infrastructure into a real CMDB

A hands-on lab that takes you from an empty free-tier AWS account to EC2 instances,
VPCs and a service instance living in a ServiceNow CMDB — reconciled by the
Identification and Reconciliation Engine (IRE) and visible in a Service Graph.

Everything here runs on a **free Personal Developer Instance (PDI)** and a **free-tier
AWS account**. No MID Server, no paid licence, no private infrastructure.

<div class="grid">
  <a class="card" href="{{ '/labs/00-prerequisites/' | relative_url }}"><b>0 · Prerequisites</b><span>PDI, AWS account, browser tabs — 15 min</span></a>
  <a class="card" href="{{ '/labs/01-aws-inventory/' | relative_url }}"><b>1 · Real AWS inventory</b><span>Build tagged EC2 + VPC with CloudFormation — 20 min</span></a>
  <a class="card" href="{{ '/labs/02-sgc-install/' | relative_url }}"><b>2 · Install SGC for AWS</b><span>Store app, plugins, entitlement check — 20 min</span></a>
  <a class="card" href="{{ '/labs/03-iam-connection/' | relative_url }}"><b>3 · Read-only IAM + connection</b><span>Access key, credentials record, test — 20 min</span></a>
  <a class="card" href="{{ '/labs/04-run-import/' | relative_url }}"><b>4 · Run the import</b><span>Schedules, first CIs, check the payload — 20 min</span></a>
  <a class="card" href="{{ '/labs/05-ire/' | relative_url }}"><b>5 · IRE results</b><span>Identification rules, duplicates, verify with API — 30 min</span></a>
  <a class="card" href="{{ '/labs/06-etl-mappings/' | relative_url }}"><b>6 · ETL mappings</b><span>Change a mapping, add a field, re-import — 30 min</span></a>
  <a class="card" href="{{ '/labs/07-csdm-graph/' | relative_url }}"><b>7 · CSDM + service graph</b><span>Application service over real CIs — 30 min</span></a>
  <a class="card" href="{{ '/labs/08-multisource-azure/' | relative_url }}"><b>8 · Multisource CMDB</b><span>Add Azure, force a reconciliation decision — 40 min</span></a>
  <a class="card" href="{{ '/labs/09-drift-monitoring/' | relative_url }}"><b>9 · Drift + monitoring</b><span>Terminate an instance, watch CMDB react — 25 min</span></a>
  <a class="card" href="{{ '/labs/10-troubleshooting/' | relative_url }}"><b>10 · Troubleshooting</b><span>Every failure mode this lab hits — reference</span></a>
  <a class="card" href="{{ '/labs/11-cleanup/' | relative_url }}"><b>11 · Cleanup</b><span>Revoke keys, delete the stack, cost = $0</span></a>
</div>

## What you end up with

- `cmdb_ci_ec2_instance` records created by the **Service Graph Connector for AWS**, each identified by its real AWS instance ID — not typed in by hand
- A `cmdb_ci_cloud_service_account` for your AWS account, and VPC records the connector discovered
- Relationships between the instance, the VPC and your application service
- An IRE result set you can read and explain: inserted vs updated vs skipped, and why
- A reconciliation precedence rule that decides which source wins when AWS and Azure both describe the same CI

## Two paths, same destination

| Path | Use when | Time |
|---|---|---|
| **A — Service Graph Connector for AWS** (Labs 2–9) | The Store app installs on your PDI. This is the real product experience. | ~3.5 h |
| **B — Fallback via IRE REST API** ([no-Store fallback]({{ '/labs/fallback-ire-api/' | relative_url }})) | Your PDI cannot install the Store app, or IntegrationHub is not entitled. Same CIs, same IRE, hand-fed. | ~1 h |

Start with Lab 0 either way. If Store install fails at Lab 2, jump to the fallback and
come back — the IRE concepts in Labs 5–7 are identical.

## Ground rules

- Everything is **free tier**. The only chargeable item is the EC2 instance you create in
  Lab 1, and `t3.micro` is free-tier eligible for 750 h/month in a new account. Lab 11
  deletes it.
- **Never commit AWS keys.** The lab creates them, uses them in one ServiceNow form, and
  revokes them in Lab 11.
- A PDI hibernates after inactivity and its URL changes. Re-wake it at
  [developer.servicenow.com](https://developer.servicenow.com) and update your notes.
