---
layout: default
title: Integration methods compared
order: -1
permalink: /integration-methods/
---

<div class="eli5">
<span class="label">Short answer to "does this tutorial cover IntegrationHub IRE?"</span>
<p>There is no single product called "IntegrationHub IRE" — they are two layers, and this lab
covers both, but you should know which is which:</p>
<ul>
<li><strong>IRE</strong> (Identification and Reconciliation Engine) is a CMDB engine. It exists
whether or not IntegrationHub is installed. <strong>Covered in Labs 4, 5, 7, 12.</strong></li>
<li><strong>IntegrationHub</strong> is the transport + ETL platform the Service Graph Connector
runs on. <strong>Covered in Labs 2, 4, 6</strong> — install check, import sets, ETL mappings.</li>
</ul>
<p>So: yes, IntegrationHub is covered (as the plumbing), and yes, IRE is covered (as the
decision maker). Lab 12 deliberately uses IRE <em>without</em> IntegrationHub, which is the
cleanest way to see that they are separable.</p>
</div>

## Which layer is which

| Layer | What it does | Where you see it in this lab |
|---|---|---|
| **AWS API** | The source of truth: what exists right now | Lab 1 (you create it), Lab 4 (payloads) |
| **IntegrationHub** | Runs the flow: calls AWS, receives JSON, transforms fields | Labs 2, 4, 6 |
| **ETL mapping** | Field-by-field: AWS `InstanceId` → CMDB `object_id` | Lab 6 |
| **IRE** | Identifies, reconciles conflicts, inserts/updates/skips | Labs 4, 5, 7, 12 |
| **CSDM + relationships** | Turns CIs into a service you can reason about | Lab 7 |
| **SGC Central / schedules** | Runs it daily and tells you when it breaks | Labs 4, 9 |

## Why use a Service Graph Connector at all?

You could hand-write an IntegrationHub flow that calls AWS and posts to IRE — that is exactly
what Lab 12 does with a Python script. So why pay for a connector?

| Benefit | What it means in practice |
|---|---|
| **Maintained mappings** | ServiceNow keeps the AWS→CMDB field map current. AWS adds a resource type, the connector adds it; you do not chase JSON changes. |
| **Guided Setup** | A checklist that ends in a working connection, instead of reading API docs and guessing at IAM permissions. |
| **No MID Server** | Cloud-to-cloud over the internet. Nothing to install inside your network — the single biggest operational saving for cloud sources. |
| **Prebuilt identification rules** | IRE rules for each CI class ship with it, so you do not invent identifiers and end up with duplicates. |
| **Schedules + retries** | Imports run on a cadence with error handling; a transient AWS throttle does not become a broken CMDB. |
| **SGC Central monitoring** | One screen showing every connection's last run, duration and errors (release-dependent). |
| **Relationship building** | VPC → subnet → instance edges are produced for you, which is what makes the service graph useful. |
| **Upgrade-safe** | Store-delivered updates instead of a bespoke script nobody owns after the author leaves. |
| **Software inventory (optional)** | With SSM enabled you also get installed-software data, feeding SAM/ITAM use cases. |

The honest counterweight: a connector only covers **its** source, and it needs entitlement.
A PDI may not offer it — hence Lab 12.

## The alternatives, and when each is right

| Method | How it works | MID Server? | Best for | Lab |
|---|---|---|---|---|
| **Service Graph Connector** | Store app: IntegrationHub flow → ETL → IRE | No | Standard cloud/SaaS inventory, long-term ownership | 2–9 |
| **Custom IntegrationHub flow + IRE** | You build the flow, map fields, call IRE | No | A source with no connector, but you want scheduling and supportability | — (Lab 6 teaches the ETL half) |
| **REST API → `/api/now/identifyreconcile`** | Your script posts records straight to IRE | No | PDIs without entitlement, one-off migrations, CI/CD seeding | 12 |
| **Import sets / CSV** | Load a spreadsheet, transform map, IRE on load | No | One-time baseline load, data from a team that has no API | not covered (deliberate) |
| **Discovery (agentless)** | Scans the network with credentials, builds CIs top-down | **Yes** | On-prem servers, network devices, "what is actually running" | not covered |
| **Agent Client Collector** | Small agent on each host reports itself | No (agent instead) | Endpoints and hosts you cannot scan, near-real-time | not covered |
| **Cloud provider export (e.g. AWS Config → S3)** | Provider dumps inventory; you ingest the files | No | Audit/compliance retention, very large accounts | not covered |
| **Third-party CMDB sync tools** | Commercial products that map source → CMDB | Varies | Multi-vendor estates, heavy customisation | not covered |

<div class="warn">
<span class="label">What this lab does not teach</span>
<p>Discovery with a MID Server, Service Mapping, and Agent Client Collector are deliberately
out of scope — each is its own multi-day lab, and none is required to understand the
connector → IRE → CSDM chain. The <a href="{{ '/labs/11-cleanup/' | relative_url }}">cleanup
page</a> lists them as next steps.</p>
</div>

## They combine — that is the real lesson

Production CMDBs are almost never single-source:

- **SGC for AWS** says "this EC2 instance exists and is `t3.micro` in `ca-central-1`".
- **Discovery** says "this host answers on 10.42.1.15, runs Amazon Linux 2023, has these open ports".
- **Agent Client Collector** says "this host has these patches and this software".

Three statements, one CI. IRE identifies it as the same thing, reconciliation decides which
source wins for each field. Lab 8 makes you do exactly this with AWS + Azure, and it is the
only way to see why precedence rules exist.

## Pick your path

| Your situation | Do this |
|---|---|
| PDI installs the Store app | Labs 2–9. The real product experience. |
| PDI cannot install it (no entitlement) | Lab 12, then Labs 6–7, then read Lab 5. |
| You will own this in production | Labs 0–11 in order, then add Discovery as a second source. |
| You only need to explain it to someone | Read the [Primer]({{ '/basics/' | relative_url }}) and this page. |

Start with [Lab 0]({{ '/labs/00-prerequisites/' | relative_url }}).
