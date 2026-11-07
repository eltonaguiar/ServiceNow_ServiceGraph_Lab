---
layout: default
title: CSDM and the service graph
lab: 7
time: 45 min
level: CSDM
order: 7
permalink: /labs/07-csdm-graph/
---

<div class="eli5">
<span class="label">ELI5 — this lab in plain English</span>
<p>Labs 1–6 collected facts. "There is a computer in Amazon's cloud, and its ID is
<code>i-0abc123…</code>." Facts are not answers. A fact cannot answer the question a manager
actually asks: <em>"if that computer dies at 3am, what breaks, and who do we wake up?"</em></p>
<p><strong>CSDM</strong> (Common Service Data Model) is ServiceNow's standard <em>shape</em> for
turning facts into that answer. It says: a <em>service</em> — something people use, like
"Payments" — sits on top of an <em>application</em>, which sits on top of <em>computers and
software</em>. Each layer points at the layer below it. Nothing is invented; it is a filing
convention, agreed in advance, so every team's data fits together.</p>
<p>In this lab you build that shape once, by hand, over your one EC2 instance. You do it
manually on purpose: a human who has built the thing once can tell whether the automated
version is lying to them.</p>
</div>

This page explains much more than it asks you to click, because the clicking is the easy part.
If "EC2", "AWS" or "CI" are still fuzzy words, the next three sections are for you — read them
before touching the instance.

**Six questions, answered below, in this order:**

1. What is AWS, and what on earth is an EC2 instance?
2. Which AWS things turn into CIs, and what do they represent?
3. What is CSDM, and why would a company bother?
4. How mature must a CMDB be before CSDM is worth doing?
5. Is CSDM automatic, manual, or both?
6. How is CSDM "run" — is it ServiceNow Discovery? And hardware, software, or neither?

## 1. What is AWS, and what is an EC2 instance?

**AWS** is Amazon Web Services: Amazon's business of renting out computers. That is the whole
idea. Instead of buying a server, racking it, powering it and replacing it in four years, you
create an account, pick a size, and rent a slice of a machine by the hour. When you are done, you
delete it and the bill stops.

A useful mental model is a **hotel**, not a house:

| Hotel | AWS |
|---|---|
| A room you rent for the night | An **instance** — a running virtual computer |
| The floor and hallway your room is on | A **VPC** — your private network inside AWS |
| The door lock that only some key cards open | A **security group** — the firewall rules |
| The hotel's front desk that checks your ID | **IAM** — who is allowed to call which AWS API |
| The hotel building itself, in one city | A **region** — a geographic cluster of datacenters (`ca-central-1` = Canada) |
| Your booking reference | The **account ID** — your 12-digit AWS number |
| Checking out | **Terminating** the instance — it stops existing |

**EC2** stands for *Elastic Compute Cloud*. It is AWS's virtual-server product, and an **EC2
instance** is one running copy of it. "Elastic" just means "resizable": you can pick 1 CPU or 96,
add disk, stop it and start it again.

Two things about EC2 that matter for this lab specifically:

- **You never see the hardware.** There is no serial number to read off a sticker, no asset tag,
  no delivery note. That physical reality exists somewhere in an Amazon datacenter you will
  never visit.
- **AWS identifies it with a string**, not a serial number: an instance ID like `i-08c9f0…`.
  That string is the most important object in this entire lab. It is how ServiceNow can say
  "this is the same server as yesterday" instead of creating a duplicate every night.

<div class="note">
<span class="label">Why not just type the server into a spreadsheet?</span>
<p>Because nobody updates spreadsheets. The value of the cloud is also the problem: instances
appear and disappear in seconds. The only trustworthy witness of what exists in an AWS account
is AWS itself, which is why every lab here starts by asking it rather than by asking a human.</p>
</div>

## 2. Which AWS things become CIs?

A **CI** (Configuration Item) is one row in the CMDB: one thing you track. AWS has hundreds of
resource types; the connector imports the ones that describe infrastructure you would raise a
ticket about. These are the ones you will actually see:

| AWS thing | Plain English | CI class it lands in | Why the lab cares |
|---|---|---|---|
| Account | Your AWS account itself | `cmdb_ci_cloud_service_account` | The root of cloud governance: "which accounts do we own?" |
| EC2 instance | A rented virtual server | `cmdb_ci_vm_instance` (the AWS connector's class — see the note below) | The CI you attach to a service in this lab |
| VPC | Your private network in AWS | `cmdb_ci_vpc` | The instance is *hosted in* it, so a working relationship already exists |
| Subnet | A slice of that network | `cmdb_ci_subnet` | Where the instance's IP lives |
| Security group | Firewall rules around the instance | network CI (`cmdb_ci_compute_security_group`) | Answers "what could reach this server?" |
| EBS volume | The instance's virtual disk | storage CI | Impact analysis for storage failures |
| S3 bucket | File/object storage | `cmdb_ci_cloud_object_storage` | Classic shadow-IT asset: who owns this data? |
| Tag | A key/value label (`Application: payments`) | `cmdb_key_value` | **The bridge between machine facts and human meaning** — see below |
| IAM user / role | The login the connector uses | not usually a CI | It is the key, not the asset. Keep it read-only (Lab 3) |

<div class="warn">
<span class="label">EC2 is not <code>cmdb_ci_ec2_instance</code> on this connector path</span>
<p>A dedicated <code>cmdb_ci_ec2_instance</code> class exists, and plenty of older guides assume
EC2 lands there. The Service Graph Connector for AWS writes EC2 instances into the generic
<code>cmdb_ci_vm_instance</code> instead — deliberately, because the same class holds Azure VMs
and two clouds then become comparable. Always open <strong>Virtual Machine Instance</strong> /
<code>cmdb_ci_vm_instance</code>, as Labs 4–6 of this site do. If your own instance genuinely
produced a different class, use that name in step 3; nothing else changes.</p>
</div>

### The one AWS concept that carries real meaning: tags

An EC2 instance is a machine. "Payments" is a *meaning*. Tags are how a human's meaning gets
attached to a machine's facts, because no API can tell you what an instance is *for*.

Lab 1 tagged your instance with `Application = payments`. That tag flowed through the connector
into the CMDB. In step 5 of this lab, that tag is what lets you attach CIs to a service
automatically instead of pointing at them one by one. Tags are, in practice, the cheapest
automation in the whole CMDB.

<div class="eli5">
<span class="label">ELI5</span>
<p>A tag is a sticky note on a cardboard box. The box is real and the note is not, but the note
is the only reason anyone knows which box to open when the boss asks for the invoices.</p>
</div>

## 3. What is CSDM, and why would a company bother?

**CSDM** = **Common Service Data Model**. It is ServiceNow's published, opinionated standard for
how to model services and tie them to the infrastructure underneath, plus the tables that
implement it. It ships with the platform (you will find it under **All → CSDM**) and is documented
as a set of *implementation stages* rather than a product you install.

It is not software that does something. It is a **shape**.

### The restaurant analogy

Your CMDB after Lab 4 is a well-stocked fridge: ingredients, accurately counted, each labelled.
Now a customer orders "the burger". Can you answer?

- Which ingredients does a burger need? (That mapping is not in the fridge.)
- If the lettuce supplier fails, which menu items are affected?
- Which chef owns the burger?

A fridge cannot answer those. **A menu can.** CSDM is the menu: it defines the dishes (services),
what each dish consumes (applications and CIs), and therefore what is at risk when an ingredient
disappears. Your EC2 instance is a very expensive piece of lettuce.

### The USB-C analogy

Before standards, every phone had its own charger. CSDM is the agreed plug shape. ServiceNow's
own modules — Incident, Change, Service Mapping, Enterprise Architecture/APM, cost reporting,
the AI agents — all expect the same plug. Without CSDM, each module gets its own hand-made
adapter, and the numbers on two dashboards quietly disagree.

### What breaks without it

- **Incident impact is a guess.** An EC2 instance is down; nobody can name the business service
  affected, so nobody knows whether to wake a director.
- **Change risk is unmeasured.** "Low risk" means "we could not see what depends on it".
- **Costs cannot be attributed.** You know what the account costs, not what *Payments* costs.
- **Reporting contradicts itself.** Each team modelled "service" differently, so every report
  has a different denominator.

### What CSDM gives you

1. **Impact:** "what breaks if this dies?" — answered by following relationships downward.
2. **Risk:** which CIs a change touches, and which services those CIs support.
3. **Prioritisation:** a production service is not the same as a lab box, even if both are EC2.
4. **Money:** cost per service, showback, and rationalisation ("we pay for three things doing
   one job").
5. **Audit and AI readiness:** regulations and AI agents both require unambiguous, machine-
   readable definitions of what a thing *is*. Vague data makes both fail.

## 4. How mature must you be before CSDM is worth doing?

CSDM is a ladder, not a switch. ServiceNow implements it in five named stages, and you can see
your own position on the **CSDM Data Foundations dashboard**
(**All → CSDM → Configuration → CSDM Data Foundations Dashboard** — the path shifts slightly by
release). Its tabs are the stages; red percentages mean "this part of the model is still
missing".

| Stage | The idea | What must already be true | Can you do this lab? |
|---|---|---|---|
| **Foundation** | The reference data everything else points at: company, locations, users, groups, and product models (hardware/software/service models) | Naming conventions, one company record, groups that can own things | No — there are no CIs to attach to yet |
| **Crawl** | Base CMDB populated for ITSM: the CIs you raise incidents against (servers, laptops, network gear) | CIs arriving automatically, with **identification rules** so they do not duplicate | Barely — your service would hang off nothing real |
| **Walk** | Technical CIs plus the applications your teams run; network infrastructure | Inventory flowing from cloud and on-prem without humans typing rows | **Yes — this lab lives here** |
| **Run** | Technology is tied to the business: service offerings, consumers, cost, SLAs | Named service owners, defined offerings, customers identified | Yes, plus you would model the offering and its consumers |
| **Fly** | Broadly complete model: capabilities, information objects, APM/SPM/CSM in use | All of the above, maintained continuously, with metrics watched | Beyond this lab |

**The direct answer:** you do not need to be mature to *use* CSDM. You need three things:

1. **Foundation data** — a company, a location, and a group that can own a service (all of it
   already exists in a stock PDI).
2. **At least one real CI with an identifier** — Lab 4 gave you that (`i-…` is the identifier).
3. **A human decision about what the service is and who owns it** — the part nobody can automate
   (see the next section).

What you do *not* need: every application modelled, the whole estate discovered, or a
CMDB-perfect organisation. Attempting "all of CSDM at once" is the single most common way these
programmes fail — teams spend a year on taxonomy and never attach one real server. The working
pattern is the opposite of that: **one service, real CIs, then repeat.**

The useful maturity question is not "are we at Fly?" but "does each new service we add still have
an owner and still point at live CIs?"

## 5. Is CSDM automatic, manual, or both?

**Both — and knowing exactly which half is which is the actual skill.** Roughly:

| Task | Who does it | Notes |
|---|---|---|
| Read AWS and create/update the CI | **Automatic** | Connector + ETL + IRE (Labs 2–6) |
| Recognise today's instance as yesterday's instance | **Automatic** | IRE identification rules on the instance ID |
| Record relationships AWS can see (instance hosted in VPC) | **Automatic** | Comes with the import |
| Keep attributes fresh on a schedule | **Automatic** | Scheduled imports |
| Promote install-base lifecycle (IBI) data to CIs and assets | **Automated jobs** | Business rules on a schedule |
| Group CIs into a service *by rule* | **Semi** | A human writes the tag query or dynamic CI group; the group then maintains itself |
| Discover an application's full dependency map top-down | **Automatic — if you own Service Mapping** | Requires Service Mapping plus a MID Server; produces application services for you |
| Decide **"Payments is a service"** | **Human** | No API knows your business. This is judgement |
| Decide who owns it and how critical it is | **Human** | Owns the pager, owns the record |
| Decide which CIs belong when tags are missing or wrong | **Human** | The permanent maintenance tax |
| Model business services → offerings → catalog items | **Human** | A commercial decision, not a technical fact |

<div class="eli5">
<span class="label">ELI5 — the one-line rule</span>
<p><strong>Machines fill the bottom of the model. Humans define the top. Automation keeps the
seam between them honest.</strong> If you point at a service record and cannot name a human who
decided it exists, you are looking at an accident, not a model.</p>
</div>

This is also why "can we just turn CSDM on?" has no useful answer. There is no switch. There is a
model, a connector that can fill its lower half, and a conversation you have to have with the
people who own the service.

## 6. How is CSDM "run"? Is it Discovery?

This deserves a blunt answer, because it is the question beginners get stuck on.

**Nothing "runs" CSDM.** There is no CSDM job that walks your estate and produces services. CSDM
is the target shape; other things write data into it. Five things can do that writing:

| Writer | How it works | Creates service-layer records? |
|---|---|---|
| **Horizontal Discovery** | MID Server scans the network in four phases (below) | **No** — infrastructure and software CIs only |
| **Service Mapping (top-down Discovery)** | Follows traffic into an application and maps tiers | **Yes** — application services, if licensed |
| **Service Graph Connector** (this lab) | Calls the vendor's API, ETL-transforms, submits to IRE. No MID Server | No — CIs and their relationships |
| **Import sets / CSV / scripts** | Anything you can point at the CMDB | Only if you script it |
| **A human clicking New** | For the parts a machine cannot know | Yes — this is what you do in step 1 |

<div class="warn">
<span class="label">The fact that surprises people</span>
<p>ServiceNow's own documentation notes that <em>application, service, and software class
instance CIs are not created through Discovery</em>. Discovery is very good at "what machine is
running here and what is installed on it". It will not tell you "this is the Payments service,
owned by the payments team, in production". If your plan is "run Discovery and the CSDM will
appear", that plan does not work — the service layer needs Service Mapping, tags with a rule
behind them, or a human. <strong>In this lab it is a human.</strong></p>
</div>

### Does this lab use Discovery at all?

**No.** There is no MID Server anywhere in this lab, and nothing is port-scanned. The connector
calls AWS's API, receives JSON, transforms it, and hands it to IRE. That is why the whole thing
works on a laptop-adjacent free account in under an hour.

But there is a bridge worth understanding: **Discovery's third phase and this lab's import both
rely on IRE identifying rules.** Same engine, same identifier, different transport. Learning IRE
here transfers directly to on-prem Discovery.

### If you *did* use Discovery, which phase would your EC2 instance appear in?

Horizontal Discovery has four phases. Probes and sensors drive the first two; patterns (or
probes on older setups) drive the last two:

| Phase | What it does | What would happen to your instance |
|---|---|---|
| **1. Scanning** | Sends the Shazzam probe: knocks on common TCP ports to see what answers | Often **nothing**. Cloud instances usually sit in private subnets, and your Lab 1 security group allows no inbound. This is the practical reason cloud inventories come from APIs, not scans |
| **2. Classification** | Sends a classify probe to decide *what kind of thing* answered, then picks the matching classifier | If SSH had answered: "a Linux machine" → the Linux classifier |
| **3. Identification** | Runs identifier probes, then applies identifier/IRE rules: is this already known? create, update, or skip? | Would match on the same `i-…` value and **update** the existing CI rather than duplicating it |
| **4. Exploration** | Gathers the detail: CPU, memory, disks, drivers, installed software, running processes — and builds relationships | Would fill in hardware/OS attributes and add relations, e.g. software running on the server |

Two further distinctions that matter later:

- **Horizontal Discovery** scans IP ranges and populates the CMDB bottom-up (that is the table
  above). **Top-down Discovery (Service Mapping)** starts from an entry point *into* an
  application and maps the path through it, producing application services and their
  relationships — the automated version of what this lab does by hand.
- Discovery in your own datacenter needs a **MID Server** (an agent inside your network) and the
  ITOM Discovery plugin. Check your PDI before planning a Discovery exercise; this lab
  deliberately avoids the dependency.

## 7. Hardware, software, or both?

**Both — plus a third layer that is neither, which is usually the confusing one.**

| | Hardware CIs | Software CIs | Service layer |
|---|---|---|---|
| **Examples** | EC2 instance, VM, physical server, router, firewall, disk volume | Installed application, software model, running process, database instance | Application service, service instance, business service, offering |
| **Looks like a thing you could touch?** | Yes, in principle | Sort of — installed somewhere you can see | **No.** It is an agreement, a grouping, a responsibility |
| **Discovery can create it?** | Yes | Yes (with credentials, or via SSM/SAM inventory) | **No** — needs Service Mapping, a tag rule, or a human |
| **In this lab** | Your EC2 instance, its VPC and security group | Nothing yet (Lab 2's optional SSM inventory can add some) | The application service **you** create in step 1 |

<div class="note">
<span class="label">Why "EC2 is hardware" is not a typo</span>
<p>An EC2 instance is really software pretending to be a computer — one physical server chopped
into slices by a hypervisor. But in CMDB terms the CI is filed under <strong>hardware</strong>,
because what it represents behaves like a server: it has an OS, a CPU count, a patching
lifecycle. Lab 4 opens <code>cmdb_ci_vm_instance.list</code> — <em>Virtual Machine Instance</em>,
filed under Hardware. That mismatch between "what it is" and "how it is filed" is normal, and it
is also the reason
the service layer exists: hardware and software records alone cannot express "the thing
customers notice".</p>
</div>

## The CSDM shape you are building

Everything above collapses into one small picture. This is the whole of Lab 7:

```
Business Service (optional, step 5 territory)
  └─ Application Service            cmdb_ci_service_auto        ← you create this (human)
       └─ Service Instance          cmdb_ci_service_instance    ← you create this (human)
            └─ Application / Runtime                            ← nothing in this lab
                 └─ Hosted on → VM (AWS EC2)  cmdb_ci_vm_instance   ← Lab 4 (machine)
```

Read it bottom-up: a machine exists because AWS said so; you assert that a *deployment* of an
application runs on it; you assert that the deployment is part of a *service*; and optionally
that humans consume that service.

Two naming warnings, because documentation and reality drift here:

- **Table names are stable, labels are not.** In CSDM 4 the middle layer is labelled *Application
  Service*; newer CSDM 5 documentation relabels much of it *Service Instance* while keeping the
  same `cmdb_ci_service_auto` table. Use the label your instance shows; trust the table name.
- **Do not invent a new modelling scheme.** If your instance offers an out-of-the-box way to
  create the service, use it. Hand-rolled custom tables are how organisations end up with CSDM
  in name only.

## Hands-on: build the shape, then look at it

The reading is over. Below is the part you click — about 15 minutes if Labs 1–6 went well.

### 1. Create the application service

1. **Configuration → CMDB → Services → Application Services → New** (or
   `cmdb_ci_service_auto.do`; on CSDM 5 instances look under
   **CSDM → Manage Technology Management Services → Application Service**, where the list is
   labelled *Service Instance*).
2. Name: `Payments (lab)`. Environment: `lab`. Owned by: your admin user.
3. Save.

Nothing here is discoverable. The name is a decision, and now it has an owner.

### 2. Create the service instance

1. On the service record, **Service Instances → New**.
2. Name: `payments-prod-01`. Install status: Installed.
3. Save.

This record means "the Payments service, deployed once, in an environment". Two environments
would be two instances of the same service — which is exactly the level of detail CSDM is for.

### 3. Attach the real CI

Create a **relationship**, not a text field. A comment saying "runs on i-08c9f0" is a note;
a relationship is a graph edge that impact analysis can follow.

1. On the service instance, open **Related Items → CI relations** (or use the
   **CI Relationship Builder**).
2. Add: **Service Instance** `payments-prod-01` — `Hosted on` / `Runs on` → the VM from Lab 4
   (class `cmdb_ci_vm_instance`, named `sgclab-app-01`).

If you prefer the API:

```bash
python3 scripts/link_ci.py \
  --parent payments-prod-01 --parent-table cmdb_ci_service_instance \
  --child sgclab-app-01 --child-table cmdb_ci_vm_instance
```

`--child` accepts either the CI's name or its `i-…` identifier. Run
`python3 scripts/link_ci.py --list-types` first if you want to choose a different relationship
label than the default `Hosted on`.

### 4. Look at the graph — and read it honestly

Open **Service Graph / Dependency Views** for the service instance:

- **Dependency Views**: `Configuration → CMDB → Dependency Views`
- **Service Graph Data Visualizer** (newer releases, inside CMDB Workspace)

You should see the service instance connected down to the EC2 CI that AWS told you about. That
picture is the product of four labs' worth of machinery: connector → ETL → IRE → relationship.

<div class="warn">
<span class="label">What the graph does not prove</span>
<p>A clean graph proves your <em>relationships</em> are clean, nothing more. If you forgot a
dependency, the view is confidently wrong — it will show a service with one server where reality
has three. Impact analysis inherits that error silently. This is why step 5 matters: rules that
keep adding CIs are more trustworthy than pictures that look tidy.</p>
</div>

### 5. Tag-driven alternative (the semi-automatic path)

Because Lab 1 tagged the instance with `Application = payments`, you can attach CIs by rule
instead of by hand:

1. Build a filter on `cmdb_ci_vm_instance` where `Application` contains `payments`.
2. Attach it to the service as a **dynamic CI group**.

A new EC2 instance with that tag then joins the service on the next import — no human step.
Try it: launch a second tagged instance, re-run the import, and watch the group grow.

<div class="note">
<span class="label">Tag-based vs dynamic CI group</span>
<p>Out-of-the-box, ServiceNow also offers a <strong>Tags</strong> population method that reads cloud
tags directly — but that option appears only when <strong>Service Mapping</strong> is installed. The
<strong>dynamic CI group</strong> used here works without it, which is why this lab teaches that
path. Either
way the principle is identical: a human writes the rule once, the machine applies it forever.</p>
</div>

## Checkpoint

<ul class="check">
<li>An application service and a service instance exist, and you can name their owner</li>
<li>The service instance is related to your real EC2 CI — a relationship, not a text note</li>
<li>Dependency Views renders the chain from service down to the instance</li>
<li>You can explain, without notes, which parts of that chain a machine produced and which you decided</li>
<li>Optional: a dynamic CI group adds a second tagged instance automatically on re-import</li>
<li>Optional: you opened the CSDM Data Foundations dashboard and found which stage is still red</li>
</ul>

## Where this goes next

A single service is a demonstration; the model becomes valuable when every service a team runs
looks the same way. Lab 8 attacks the harder half of the problem — a second source (Azure)
describing the same kinds of CI — where CSDM stops being a naming convention and starts being
the thing that decides which source's answer wins.

Next: [Lab 8 — multisource CMDB with Azure]({{ '/labs/08-multisource-azure/' | relative_url }})
