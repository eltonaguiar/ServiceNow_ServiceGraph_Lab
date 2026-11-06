---
layout: default
title: CSDM and the service graph
lab: 7
time: 30 min
level: CSDM
order: 7
permalink: /labs/07-csdm-graph/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>A pile of servers is not a service. This lab groups the real EC2 machine under an application service so you can ask "what breaks if this dies?"</p>
</div>

## Objective

Turn a pile of discovered CIs (Configuration Items) into a service you can look at: an application service whose
service instance points at your real EC2 instance, following the CSDM shape.

## The CSDM (Common Service Data Model) shape you are building

```
Business Service (optional)
  └─ Application Service            cmdb_ci_service_auto
       └─ Service Instance          cmdb_ci_service_instance
            └─ Application / Runtime
                 └─ Hosted on → EC2 instance   cmdb_ci_ec2_instance
```

The exact class names vary slightly by CSDM version, but the chain
*business → application service → service instance → CI* is stable.

## 1. Create the application service

1. **Configuration → CMDB → Services → Application Services → New** (or
   `cmdb_ci_service_auto.do`).
2. Name: `Payments (lab)`. Environment: `lab`. Owned by: your admin user.
3. Save.

## 2. Create the service instance

1. On the service record, **Service Instances → New**.
2. Name: `payments-prod-01`. Install status: Installed.
3. Save.

## 3. Attach the real CI

Create the relationship rather than filling a "runs on" text field:

1. On the service instance, open **Related Items → CI relations** (or use
   **CI Relationship Builder**).
2. Add: **Service Instance** `payments-prod-01` — `Hosted on` / `Runs on` → **EC2 instance**
   from Lab 4.

If you prefer the API:

```bash
python3 scripts/link_ci.py --citype "Hosted on::cmdb_ci_ec2_instance" --parent payments-prod-01
```

## 4. Look at the graph

Open **Service Graph / Dependency Views** for the service instance:

- **Dependency Views**: `Configuration → CMDB → Dependency Views`
- **Service Graph Data Visualizer** (newer releases, inside CMDB Workspace)

You should see the service instance connected down to the EC2 CI that AWS told you about.
That view is the product of three labs: connector → IRE → relationship.

## 5. Tag-driven alternative

Because Lab 1 tagged the instance with `Application = payments`, you can also attach CIs by
query: build a filter on `cmdb_ci_ec2_instance` where `Application` contains `payments`, and
use it as a **dynamic CI group** attached to the service. Then a new EC2 instance with that tag
joins the service on the next import — no manual step. Try it: launch a second tagged instance,
re-run the import, and watch the group grow.

## Checkpoint

<ul class="check">
<li>An application service and service instance exist</li>
<li>The service instance is related to your real EC2 CI</li>
<li>Dependency Views renders the chain</li>
<li>Optional: a dynamic CI group adds a second instance automatically</li>
</ul>

Next: [Lab 8 — multisource CMDB with Azure]({{ '/labs/08-multisource-azure/' | relative_url }})
