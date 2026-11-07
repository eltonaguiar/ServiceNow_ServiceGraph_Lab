---
layout: default
title: Primer — every term, in plain English
order: -2
permalink: /basics/
---

<div class="eli5">
<span class="label">Start here if none of the words mean anything yet</span>
<p>This lab has one job: <strong>make a company's list of its computers trustworthy, automatically</strong>.</p>
<p>Today that list (the "CMDB") is usually a spreadsheet someone updates by hand, so it is wrong.
The fix is to let the cloud provider tell ServiceNow what exists, and let ServiceNow decide
whether each thing is new, already known, or out of date. Everything below is that story with
the jargon peeled off.</p>
</div>

## The one-minute story

1. Your company runs servers in **AWS** (Amazon's cloud) and maybe **Azure** (Microsoft's cloud).
2. Those clouds know exactly what you own at any moment. They can tell you via an API.
3. **ServiceNow** holds a database of "everything we own and how it fits together" — the **CMDB**.
4. A **Service Graph Connector** is a ready-made pipe from the cloud's API into the CMDB.
5. The **IRE** engine decides, for each item, "have I seen this before? create, update, or skip?"
6. You then relate those items into a **service** so you can answer "what breaks if this server dies?"

That is the entire lab. The rest is detail.

## What is AWS?

**Amazon Web Services** — Amazon's rent-a-computer business. You create an account, and instead
of buying a server you rent one by the hour (an **EC2 instance**), plus networking (a **VPC**),
storage (an **S3 bucket**), and so on. You pay for what runs.

What it means for this lab: AWS is the **data source**. Nothing about this lab is AWS-specific
in principle — Azure would work the same way — but AWS has the cleanest free tier and the most
complete connector.

Terms you will meet on the AWS side:

| AWS term | What it actually is | Why the lab cares |
|---|---|---|
| **EC2 instance** | A rented virtual server | Becomes a CI in the CMDB — the main thing you will look at |
| **VPC** | A private network inside AWS (Virtual Private Cloud) | Becomes a CI, and the EC2 instance is related to it |
| **Subnet** | A slice of that network | Inventoried; shows how relationships get built |
| **Security group** | A firewall rule set | Another network CI |
| **IAM** | Identity and Access Management — who may call which AWS API | You create a **read-only** user so the connector can look but never change anything |
| **Access key** | A username/password pair for programs (not humans) | What the connector authenticates with |
| **Region** | A geographic cluster of datacenters (`ca-central-1` = Canada) | You pick one and stay in it |
| **Account ID** | Your 12-digit AWS account number | Tells the connector which account to read |
| **CloudFormation** | "Infrastructure as code" — a file that creates resources | Lab 1 uses one so you do not click 20 screens |
| **Tag** | A key/value label on a resource (`Environment: lab`) | The most important idea in the lab: tags are how human meaning gets into the CMDB |

## What is Azure?

**Microsoft Azure** — the same idea as AWS, Microsoft's version. Its equivalents:

| Azure term | AWS equivalent | Lab use |
|---|---|---|
| Virtual Machine (VM) | EC2 instance | Becomes a CI |
| Resource group | (roughly) a folder of resources | Where you put the lab VM |
| Subscription | Account | Scope for permissions |
| **Entra ID** (formerly Azure Active Directory) | IAM | Where you register the app |
| **App registration / service principal** | IAM user + access key | How ServiceNow authenticates — a client ID + secret instead of a key pair |
| **Reader** role | ReadOnlyAccess policy | Grants look-but-not-touch |

Lab 8 adds Azure so you can see **two sources describing the same kind of thing**, which is
where a CMDB gets genuinely hard.

## What is a CMDB, and what is a CI?

- **CMDB** = Configuration Management Database. A database of the things an IT organisation
  owns and how they depend on each other.
- **CI** = Configuration Item. One entry in that database: a server, a database, a load
  balancer, a SaaS application, a network device — anything you need to track.
- **CI class** = the *type* of a CI, like a table in a database. All EC2 instances share a class;
  all databases share another.

Why a class matters: the class decides which fields exist, which identification rule applies,
and who owns the data. Put a server in the wrong class and everything downstream (reports,
dashboards, service maps, approvals) is subtly wrong.

### CI classes you will actually touch

| CI class (table) | What it represents | Typical real-world use |
|---|---|---|
| `cmdb_ci_vm_instance` | Virtual machine (AWS EC2 on Service Graph, Azure, VMware) | **AWS Service Graph EC2 lands here** — open this list after `SG-AWS-EC2` |
| `cmdb_ci_ec2_instance` | EC2-specific class (older or alternate mappings) | Often **empty** when the AWS connector uses `cmdb_ci_vm_instance` |
| `cmdb_ci_server` / `cmdb_ci_linux_server` | A physical or logical server | OS patching, vulnerability management |
| `cmdb_ci_cloud_service_account` | A cloud account/subscription itself | "Which accounts do we own?" — the root of cloud governance |
| `cmdb_ci_vpc` | A virtual private network | Network impact analysis, segmentation checks |
| `cmdb_ci_database` | A database instance | Data-flow and dependency mapping |
| `cmdb_ci_service_auto` | An application service (CSDM) | The thing the business talks about: "Payments" |
| `cmdb_ci_service_instance` | One deployment of that service in one environment | "Payments in production, in Canada" |

> Rule of thumb: a **CI** is a noun you would put in an inventory. A **service** is a capability
> the business would notice if it stopped.

## What is IRE?

**IRE** = **Identification and Reconciliation Engine**. It is the bouncer at the CMDB door.

Every piece of data — from any connector, any discovery tool, any CSV — goes through IRE, and
IRE answers three questions per record:

1. **Identification:** is this the same thing I already have? (It matches on identifiers —
   for an EC2 instance, the AWS instance ID `i-…`.)
2. **Reconciliation:** if two sources disagree about a field, whose value wins?
3. **Write:** insert a new CI, update the existing one, or do nothing because nothing changed.

<div class="eli5">
<span class="label">ELI5</span>
<p>Think of a contact list on your phone. When a new number texts you, the phone asks: "do I
already have this person?" If yes, it updates the name; if no, it adds a contact. If two apps
both sync contacts and disagree about the spelling, something has to decide which wins.</p>
<p>IRE is that logic, for servers, with an audit trail. "Identification" is the phone deciding
it is the same person; "reconciliation" is deciding which spelling wins.</p>
</div>

**Why you care:** almost every "the CMDB is full of duplicates" or "the import ran but nothing
showed up" problem is an IRE problem, not a connector problem. Lab 5 is dedicated to it.

## What is IntegrationHub?

**IntegrationHub** is ServiceNow's integration and automation platform — the engine that runs
**flows** (automations) and **Spokes** (prebuilt connectors). When a Service Graph Connector
talks to AWS, the thing doing the talking is an IntegrationHub flow: call the AWS API, receive
JSON, transform it, hand it to IRE.

Two pieces inside it matter here:

- **REST step / spoke action** — performs the API call to AWS.
- **ETL** = **Extract, Transform, Load**. Extract = pull the data; Transform = map AWS fields to
  CMDB fields; Load = submit to IRE.

<div class="warn">
<span class="label">Does this tutorial cover "IntegrationHub IRE"?</span>
<p>They are two different things, and this lab covers <strong>both but separately</strong>:</p>
<ul>
<li><strong>IRE</strong> is a CMDB engine that exists with or without IntegrationHub. Labs 4, 5,
7 and the fallback Lab 12 use it directly.</li>
<li><strong>IntegrationHub</strong> is the transport/ETL layer the Service Graph Connector runs on.
Labs 2, 4 and 6 exercise it (checking it is installed, watching its import sets, editing its ETL
mappings).</li>
</ul>
<p>See <a href="{{ '/integration-methods/' | relative_url }}">Integration methods compared</a> for
which lab proves which layer, and what you would build if you had to do it without the connector.</p>
</div>

## What is CSDM?

**CSDM** = **Common Service Data Model**. ServiceNow's opinionated, standard way to model
services — so that "the business service", "the application", "the servers under it" and "the
CIs" line up the same way in every company.

Without it, ten teams invent ten ways to attach a server to an app. With it, Service Mapping,
impact analysis and reporting all work. Lab 7 builds the smallest useful slice:
application service → service instance → the real EC2 CI.

## What is a Service Graph Connector?

A **Service Graph Connector (SGC)** is a packaged, vendor-supported integration for one
third-party system (AWS, Azure, GCP, VMware, Intune, CrowdStrike…) that pulls its inventory into
the CMDB through IntegrationHub ETL and IRE, with maintained mappings, schedules, and Guided
Setup.

The point: it is **maintained by ServiceNow**, so when AWS adds a field, you get an update
instead of a broken script. It also means "no MID Server" for cloud sources — the instance calls
the vendor's API over the internet.

## Abbreviation glossary

Every abbreviation used on this site, expanded once, alphabetically.

<details class="glossary"><summary>A–C</summary>
<ul>
<li><strong>AMI</strong> — Amazon Machine Image: the disk snapshot a new EC2 instance boots from.</li>
<li><strong>API</strong> — Application Programming Interface: the way one program asks another for data.</li>
<li><strong>AZ</strong> — Availability Zone: an isolated datacenter inside an AWS region.</li>
<li><strong>AWS</strong> — Amazon Web Services: Amazon's cloud platform.</li>
<li><strong>CI</strong> — Configuration Item: one tracked thing in the CMDB (a server, a database, a service).</li>
<li><strong>CMDB</strong> — Configuration Management Database: the inventory of CIs and their relationships.</li>
<li><strong>CMDB 360</strong> — ServiceNow's multisource view: one CI, several contributing sources, per-attribute history.</li>
<li><strong>CSDM</strong> — Common Service Data Model: ServiceNow's standard way to model services and their CIs.</li>
</ul>
</details>

<details class="glossary"><summary>D–I</summary>
<ul>
<li><strong>EC2</strong> — Elastic Compute Cloud: AWS's virtual server product.</li>
<li><strong>ELI5</strong> — "Explain Like I'm 5": a deliberately simple explanation.</li>
<li><strong>ETL</strong> — Extract, Transform, Load: pull data, map it, write it.</li>
<li><strong>FQDN</strong> — Fully Qualified Domain Name: a complete hostname like <code>app01.example.com</code>.</li>
<li><strong>GCP</strong> — Google Cloud Platform.</li>
<li><strong>GUI</strong> — Graphical User Interface: clicking, as opposed to typing commands.</li>
<li><strong>IAM</strong> — Identity and Access Management: who may call which AWS API, and with what permissions.</li>
<li><strong>ID</strong> — Identifier: the unique value used to recognise a record.</li>
<li><strong>IntegrationHub</strong> — ServiceNow's integration and automation platform (flows, spokes, REST steps).</li>
<li><strong>IRE</strong> — Identification and Reconciliation Engine: decides create/update/skip and who wins a conflict.</li>
<li><strong>ITOM</strong> — IT Operations Management: the ServiceNow product family for discovery, health and event management.</li>
<li><strong>ITSM</strong> — IT Service Management: incidents, changes, requests — the classic service desk product.</li>
</ul>
</details>

<details class="glossary"><summary>J–R</summary>
<ul>
<li><strong>JSON</strong> — JavaScript Object Notation: the text format APIs return data in.</li>
<li><strong>MID Server</strong> — Management, Instrumentation and Discovery Server: a small agent ServiceNow runs inside your network to reach systems that are not on the internet. Cloud connectors do <em>not</em> need one.</li>
<li><strong>PDI</strong> — Personal Developer Instance: a free, temporary ServiceNow instance for learning.</li>
<li><strong>REST</strong> — Representational State Transfer: the common style of web API (GET/POST over HTTPS).</li>
<li><strong>RBAC</strong> — Role-Based Access Control: permissions granted by role rather than per person.</li>
</ul>
</details>

<details class="glossary"><summary>S–Z</summary>
<ul>
<li><strong>S3</strong> — Simple Storage Service: AWS's file/object storage.</li>
<li><strong>SaaS</strong> — Software as a Service: software you rent rather than install.</li>
<li><strong>SGC</strong> — Service Graph Connector: a packaged integration that loads a vendor's inventory into the CMDB.</li>
<li><strong>SG</strong> — Security Group: AWS's firewall rules for a resource.</li>
<li><strong>SSM</strong> — AWS Systems Manager: used here for optional software inventory data.</li>
<li><strong>SSO</strong> — Single Sign-On: one login for many systems.</li>
<li><strong>UI</strong> — User Interface.</li>
<li><strong>VM</strong> — Virtual Machine: a computer simulated in software.</li>
<li><strong>VPC</strong> — Virtual Private Cloud: your private network inside AWS.</li>
</ul>
</details>

## What you need before starting

Only three things: a browser, a free ServiceNow developer instance, and a free AWS account.
[Lab 0]({{ '/labs/00-prerequisites/' | relative_url }}) walks through both, including the budget
alarm that keeps the lab at zero cost.

Then: [Lab 1 — build a real AWS inventory]({{ '/labs/01-aws-inventory/' | relative_url }})
