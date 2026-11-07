---
layout: default
title: Install the connector
lab: 2
time: 20 min
level: ServiceNow
order: 2
permalink: /labs/02-sgc-install/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>This is an app install. A free ServiceNow instance may refuse it — that is normal, and Lab 12 is the backup plan. What matters is knowing which layer you are missing.</p>
</div>

## Objective

Get the Service Graph Connector (SGC) for AWS onto the instance and confirm its dependencies,
or decide cleanly that this PDI cannot run it and switch to the fallback path.

## 1. Check what your PDI already has

1. Filter Navigator → **System Applications → All Available Applications → All**.
2. Search for **Service Graph Connector for AWS**.

The ServiceNow-built connector ships under a plugin id like `sn_aws_integ`; the UI shows the
friendly name, so search by name rather than id. You may also see it under
**System Applications → Plugins** on older releases.

### Confirm the exact plugin id on your release

Do not trust any id in this lab — ids and display names differ between releases. On **your**
instance:

1. Filter Navigator → type `sys_store_app.list` → search `aws`.
   This is the Store application list: it tells you whether the app is **known**, not whether
   you may install it.
2. Filter Navigator → type `v_plugin.list` → search `sn_aws` or `integration`. This is the
   plugin list: `Active` means installed, a visible row with no install option means the plugin
   exists but is not entitled.
3. Or simply open the app record and read **Dependencies** — it names every plugin it needs,
   which is the authority for your version.

Write down what you find; it makes the decision below mechanical instead of guesswork.

## 2. Install it and its dependencies

1. Open the app → **Install** (accept the terms).
2. If prompted about dependencies, install them. The usual ones are:
   - **Integration Commons for CMDB**
   - **CMDB Identification and Reconciliation** (present on every instance, but the version matters)
   - **IntegrationHub** (ServiceNow's integration and automation platform) — required for the cloud-to-cloud REST (Representational State Transfer) flow
3. Wait for the install to finish, then **reload the UI** (the module tree caches).

### Decision tree — what you see, what you do

Beginners lose the most time here, so decide by symptom rather than by hope:

| What you see | What it means | Do this |
|---|---|---|
| App shows **Install** and it completes; **Installed** afterwards | Entitled | Continue to §3 |
| App is listed, **Install is greyed out** or errors with entitlement/licence | Not entitled on this PDI | [Fallback]({{ '/labs/fallback-ire-api/' | relative_url }}), then rejoin at Lab 5 |
| App is **absent** from All Available Applications, and `v_plugin.list` has no `sn_aws` row | This release does not expose it | Fallback |
| Install starts then fails on a **dependency** (Integration Commons, IntegrationHub) | Dependency missing or already half-installed | Install dependencies one at a time, reload, retry; check **System Applications → Installed** for half-finished rows |
| Install succeeds but the module tree is empty after reload | UI cache | Hard-reload the browser, log out and back in |

> An entitlement failure is **not** a setup mistake and there is nothing to fix. Free PDIs are
> not licensed for every Store app. Switch to the fallback, which produces the same CMDB
> records through `POST /api/now/identifyreconcile`.

## 3. Confirm IntegrationHub

1. Filter Navigator → **Process Automation → Flow Designer**. If it opens, IntegrationHub is
   active.
2. If Flow Designer is missing, the cloud REST flow cannot run — go to the fallback path.

## 4. Open the setup experience

Two possibilities, in order of preference:

| What you see | Use it |
|---|---|
| **AWS → Setup** module, or a Guided Setup card | Guided Setup — the steps map to Labs 3–4 |
| **SGC Central** in CMDB Workspace (newer releases) | SGC Central — create and monitor the connection there |

Both paths ask for the same four things: account ID, region, access key, secret. The difference
is only where the screens live — so do not hunt for the "right" one:

- **Guided Setup** (if you see *AWS → Setup* or a guided-setup card in the app) walks a
  numbered checklist: prerequisites → credential → connection → schedule. Follow the numbers,
  not this lab's numbers.
- **SGC Central** (CMDB Workspace) is a list of connections you create yourself: *New
  connection → AWS*, then the same four fields plus a schedule picker. Monitoring lives here
  afterwards.

If both exist, use Guided Setup once (it creates the credential record for you) and then use
SGC Central for monitoring. If only one exists, that is the supported path for your release.

> **Before Lab 3:** in Guided Setup, run **Download the scripts** and keep the ZIP. Lab 3 §0
> explains why AWS Config, set up with `EnableAWSConfig.yml`, is required.

## Checkpoint

<ul class="check">
<li>The connector app shows <b>Installed</b></li>
<li>Flow Designer opens</li>
<li>You can see either <b>AWS → Setup</b>, a Guided Setup card, or <b>SGC Central</b></li>
<li>You have decided: connector path, or fallback path</li>
</ul>

Next: [Lab 3 — read-only IAM and the connection]({{ '/labs/03-iam-connection/' | relative_url }})
