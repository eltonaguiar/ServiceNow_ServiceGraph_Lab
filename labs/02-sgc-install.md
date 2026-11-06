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

## 2. Install it and its dependencies

1. Open the app → **Install** (accept the terms).
2. If prompted about dependencies, install them. The usual ones are:
   - **Integration Commons for CMDB**
   - **CMDB Identification and Reconciliation** (present on every instance, but the version matters)
   - **IntegrationHub** (ServiceNow's integration and automation platform) — required for the cloud-to-cloud REST (Representational State Transfer) flow
3. Wait for the install to finish, then **reload the UI** (the module tree caches).

> If the app is listed but not installable, or the install fails with a licensing or
> entitlement error, your PDI release does not include it. This is normal and not a dead end:
> use the [IRE REST fallback]({{ '/labs/fallback-ire-api/' | relative_url }}) to load the same
> AWS data into the same CMDB tables, then rejoin at Lab 5.

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
is only where the screens live.

## Checkpoint

<ul class="check">
<li>The connector app shows <b>Installed</b></li>
<li>Flow Designer opens</li>
<li>You can see either <b>AWS → Setup</b>, a Guided Setup card, or <b>SGC Central</b></li>
<li>You have decided: connector path, or fallback path</li>
</ul>

Next: [Lab 3 — read-only IAM and the connection]({{ '/labs/03-iam-connection/' | relative_url }})
