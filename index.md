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

Designed for a free **PDI** (Personal Developer Instance) and a **credit-based AWS account** (Lab 0).
AWS **Config**, **S3**, storage, and **stopped EC2** can still incur charges; the budget alarm
**alerts only** — it does not cap spend. No **MID Server**, no production account required.

<nav class="toc" aria-label="Contents">
  <div>
    <p class="toc-title">On this page</p>
    <ol class="toc-list">
      <li><a href="#why">Why this lab, vs ServiceNow's own courses</a></li>
      <li><a href="#primer">New to the vocabulary?</a></li>
      <li><a href="#labs">The lab sequence</a></li>
      <li><a href="#outcome">What you end up with</a></li>
      <li><a href="#paths">Two paths, same destination</a></li>
      <li><a href="#rules">Ground rules</a></li>
    </ol>
  </div>
  <div>
    <p class="toc-title">Start here</p>
    <ul class="toc-list">
      <li><a href="{{ '/labs/00-prerequisites/' | relative_url }}">Lab 0 — Prerequisites</a></li>
      <li><a href="{{ '/basics/' | relative_url }}">Primer — every term in plain English</a></li>
      <li><a href="{{ '/integration-methods/' | relative_url }}">Integration methods compared</a></li>
      <li><a href="{{ '/labs/fallback-ire-api/' | relative_url }}">No-Store fallback path</a></li>
      <li><a href="{{ '/labs/10-troubleshooting/' | relative_url }}">Troubleshooting matrix</a></li>
      <li><a href="https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab">Repo — scripts + CloudFormation</a></li>
    </ul>
  </div>
  <div class="toc-wide">
    <p class="toc-title">The 12 labs, in order</p>
    <ul class="toc-list toc-labs">
      <li><a href="{{ '/labs/00-prerequisites/' | relative_url }}"><b>0</b> Prerequisites</a></li>
      <li><a href="{{ '/labs/01-aws-inventory/' | relative_url }}"><b>1</b> AWS inventory</a></li>
      <li><a href="{{ '/labs/02-sgc-install/' | relative_url }}"><b>2</b> Connector install</a></li>
      <li><a href="{{ '/labs/03-iam-connection/' | relative_url }}"><b>3</b> IAM + connection</a></li>
      <li><a href="{{ '/labs/04-run-import/' | relative_url }}"><b>4</b> Run the import</a></li>
      <li><a href="{{ '/labs/05-ire/' | relative_url }}"><b>5</b> IRE results</a></li>
      <li><a href="{{ '/labs/06-etl-mappings/' | relative_url }}"><b>6</b> ETL mappings</a></li>
      <li><a href="{{ '/labs/07-csdm-graph/' | relative_url }}"><b>7</b> CSDM + service graph</a></li>
      <li><a href="{{ '/labs/08-multisource-azure/' | relative_url }}"><b>8</b> Multisource (Azure)</a></li>
      <li><a href="{{ '/labs/09-drift-monitoring/' | relative_url }}"><b>9</b> Drift + monitoring</a></li>
      <li><a href="{{ '/labs/10-troubleshooting/' | relative_url }}"><b>10</b> Troubleshooting</a></li>
      <li><a href="{{ '/labs/11-cleanup/' | relative_url }}"><b>11</b> Cleanup</a></li>
    </ul>
  </div>
</nav>

<div style="border: 2px solid #d73a49; border-radius: 6px; padding: 12px 16px; margin: 16px 0; background: #fff5f5; color: #24292e;">
<p style="margin: 0; font-weight: bold; color: #cb2431;">⚠️ Cost warning — read this before you spend</p>
<p style="margin: 8px 0 0 0; color: #24292e;"><strong>AWS policy depends on your account type — not on this website.</strong>
On the current <a href="https://aws.amazon.com/free/">credit-based Free Plan</a> (common for new accounts since mid‑2025),
Amazon Web Services states you are not billed for eligible usage while you remain on that plan and your
<a href="https://aws.amazon.com/free/terms/">Free Tier credits</a> cover it — unless you
<a href="https://docs.aws.amazon.com/accounts/latest/reference/upgrade-account.html">upgrade to a Paid plan</a>
or turn on paid‑only services. The Free Plan period ends when credits run out or at six months, whichever
comes first; after that AWS suspends access. You may have up to <strong>90 days</strong> to upgrade to a Paid
plan to restore the account; otherwise AWS can permanently close it and delete content (per
<a href="https://aws.amazon.com/free/terms/">Free Tier terms</a> and
<a href="https://aws.amazon.com/free/free-tier-faqs/">FAQs</a>). That automatic expiry is
<strong>not</strong> the same as <strong>you</strong>
<a href="https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-closing.html">choosing to close</a>
an account: voluntary closure has its own rules, bills for usage already consumed, and if you reopen within
90 days <strong>charges for services can restart</strong>. Closing or reopening is account management — not a
way to reset the lab or avoid paying for usage on a Paid plan.</p>
<p style="margin: 8px 0 0 0; color: #24292e;"><strong>What we saw while building this lab (text only — your console may differ).</strong>
On one Free Plan account the billing home showed <em>Free</em>, “no charges while on the free plan,”
<strong>amount due $0.00</strong>, roughly <strong>182 days</strong> left on the plan period (plan end
<strong>6 May 2027</strong> in that UI), <strong>$120.00</strong> in remaining Free Tier credits with usage
described as covered by those credits, and the original <strong>$100</strong> signup credit called out at
registration (we are not claiming where any additional credits came from). That snapshot supports
<strong>$0 due for that account at that time</strong> — it is <strong>not</strong> a promise that every
learner pays nothing.</p>
<p style="margin: 8px 0 0 0; color: #24292e;">Older accounts may still follow the
<a href="https://aws.amazon.com/free/terms/">legacy 12‑month free tier</a>; the
<a href="https://aws.amazon.com/free/free-tier-faqs/">FAQs</a> note signup experiences differ (including
changes in 2026). Optional Lab 8 uses <strong>Azure</strong>, which has its own billing. This lab
can still bill you if you: upgrade; join Organizations on a Free plan; exceed credit coverage; leave
<strong>AWS Config</strong>, <strong>S3</strong>, public IPv4, or disks running; or skip teardown.
Set the <strong>budget alarm</strong> in Lab 0 (it warns only), follow scoped Labs 1/3/11 cleanup, and
delete stacks when finished — details stay on those lab pages; this warning does not replace them.</p>
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

<h2 id="why">Why this lab exists — and how it differs from ServiceNow's own Learning content</h2>

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
| **Cost** | Depends on the lab entitlement | Lab 0 + Lab 11 minimize spend; verify billing — Config/S3 buckets may remain (see Lab 3/11) |

Two things this lab is **not**: it is not exam prep, and it is not a reference architecture. The
free-tier AWS account is a teaching environment, not a production design — the point is that you
finish with a working pattern you have personally operated end to end, so the product documentation
and the certification material have something concrete to attach to.

<h2 id="primer">New to the vocabulary?</h2>

Two pages exist so you never have to guess:

<div class="grid">
  <a class="card" href="{{ '/basics/' | relative_url }}"><b>Primer — every term in plain English</b><span>What AWS, Azure, a CMDB, a CI, a CI class, IRE, ETL, CSDM and a Service Graph Connector are — plus a full abbreviation glossary</span></a>
  <a class="card" href="{{ '/integration-methods/' | relative_url }}"><b>Integration methods compared</b><span>Does this cover IntegrationHub and IRE? Why use a Service Graph Connector? What else could you use instead?</span></a>
</div>

<h2 id="labs">The lab sequence</h2>

<div class="grid">
  <a class="card" href="{{ '/labs/00-prerequisites/' | relative_url }}"><b>0 · Prerequisites</b><span>PDI, AWS account, budget alarm — 15 min</span></a>
  <a class="card" href="{{ '/labs/01-aws-inventory/' | relative_url }}"><b>1 · Real AWS inventory</b><span>Tagged EC2 + VPC via CloudFormation — 20 min</span></a>
  <a class="card" href="{{ '/labs/02-sgc-install/' | relative_url }}"><b>2 · Install the connector</b><span>Service Graph Connector for AWS — 20 min</span></a>
  <a class="card" href="{{ '/labs/03-iam-connection/' | relative_url }}"><b>3 · Read-only IAM + connection</b><span>Access key, credentials record, test — 20 min</span></a>
  <a class="card" href="{{ '/labs/04-run-import/' | relative_url }}"><b>4 · Run the import</b><span>Schedules, VPC evidence + basic PoC map — 45 min</span></a>
  <a class="card" href="{{ '/labs/05-ire/' | relative_url }}"><b>5 · IRE results</b><span>Observational minimum — one VM, partials — 25 min</span></a>
  <a class="card" href="{{ '/labs/06-etl-mappings/' | relative_url }}"><b>6 · ETL mappings</b><span>Read mappings first; optional edit — 30 min</span></a>
  <a class="card" href="{{ '/labs/07-csdm-graph/' | relative_url }}"><b>7 · CSDM + service graph</b><span>Application service over real CIs — 30 min</span></a>
  <a class="card" href="{{ '/labs/08-multisource-azure/' | relative_url }}"><b>8 · Multisource CMDB</b><span>Add Azure, force a reconciliation decision — 40 min</span></a>
  <a class="card" href="{{ '/labs/09-drift-monitoring/' | relative_url }}"><b>9 · Drift + monitoring</b><span>Terminate an instance, watch the CMDB react — 25 min</span></a>
  <a class="card" href="{{ '/labs/10-troubleshooting/' | relative_url }}"><b>10 · Troubleshooting</b><span>Every failure mode this lab hits — reference</span></a>
  <a class="card" href="{{ '/labs/11-cleanup/' | relative_url }}"><b>11 · Cleanup</b><span>Revoke keys, delete stacks, verify billing</span></a>
</div>

<h2 id="outcome">What you end up with</h2>

- `cmdb_ci_vm_instance` for your lab EC2 (AWS connector path) — `object_id` is the real `i-…` id
- Account, datacenter, **cloud network** (VPC), subnet, and security-group CIs from scheduled imports
- Relationships between the instance, the VPC and your application service
- An IRE result set you can read and explain: inserted vs updated vs skipped, and why
- A reconciliation precedence rule that decides which source wins when AWS and Azure disagree

<h2 id="paths">Two paths, same destination</h2>

| Path | Use when | Time |
|---|---|---|
| **A — Service Graph Connector for AWS** (Labs 2–9) | The Store app installs on your PDI. This is the real product experience. | ~3.5 h |
| **B — Fallback via the IRE REST API** ([no-Store fallback]({{ '/labs/fallback-ire-api/' | relative_url }})) | Your PDI cannot install the Store app, or IntegrationHub is not entitled. Same CIs, same IRE, hand-fed. | ~1 h |

Start with Lab 0 either way. If the install fails at Lab 2, take the fallback and come back —
the IRE concepts in Labs 5–7 are identical.

<h2 id="rules">Ground rules</h2>

- **Costs are not zero by default.** Running or **stopped** EC2, **AWS Config** recording,
  **S3** delivery buckets (often **retained** after stack delete), EBS, and public IPv4 can bill.
  Credits may cover small labs — check **Cost Explorer** and [Lab 11]({{ '/labs/11-cleanup/' | relative_url }}).
- Set a **budget alarm** in Lab 0; it **warns**, it does **not** stop charges.
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
