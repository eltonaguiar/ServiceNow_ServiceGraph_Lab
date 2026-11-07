---
layout: default
title: Cleanup
lab: 11
time: 15 min
level: Wrap-up
order: 11
permalink: /labs/11-cleanup/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>Leave with no live keys and no surprise bill. Kill the credentials <em>first</em>, so nothing keeps calling AWS after you delete resources — then verify billing yourself.</p>
</div>

## Objective

Leave with no live keys, cloud resources torn down **where you can verify**, and usage and credits
checked in the **correct** account. On a confirmed **AWS Free plan**, cleanup mainly prevents
unnecessary credit consumption; it does **not** extend the six-month plan limit. On **Paid** or
legacy accounts it also prevents continuing out-of-pocket charges. Retained **AWS Config** /
**Simple Storage Service (S3)** resources can continue metered usage. Do **not** rely on eventual Free
plan suspension as your cleanup procedure or data backup ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }})).

## 1. Revoke the credentials first

1. AWS → **IAM → Users → servicenow-sgc-lab → Security credentials** → **Deactivate**, then
   **Delete** the access key.
2. Delete the IAM user (or at least remove its policies).
3. In ServiceNow, delete or disable the connection / credential record the connector created
   (SGC Central → connection → delete; or the alias record it references).
4. Azure: **App registrations → your app → Certificates & secrets** → delete the client secret,
   then remove the Reader role assignment.

Order matters: kill the keys before deleting the resources, so a leftover schedule cannot keep
calling AWS with a live token.

## 2. Delete the cloud resources

```bash
aws cloudformation delete-stack --stack-name sgclab
aws cloudformation wait stack-delete-complete --stack-name sgclab
```

If you built by hand: terminate the EC2 instance, delete the VPC (this removes subnets, route
tables, security groups), then confirm nothing is left in **EC2 → Instances**, **VPC**, and
**Elastic IPs**.

Azure: delete the resource group you created, then verify in **Cost Management**.

## 3. Stop the schedules

**System Scheduler → Scheduled Jobs** → deactivate the AWS and Azure import jobs. A PDI that
keeps calling a deleted account generates nothing but errors.

## 4. Confirm the bill

- AWS **Billing → Cost Explorer**, group by service, last 7 days
- **Budgets** — confirm the alarm still exists (the alarm itself is not a spend cap)
- If you ran **AWS Config** (Lab 3): open **AWS Config → Settings** and **S3** — empty and delete
  any delivery bucket CloudFormation **retained** after stack delete
- Azure **Cost Management → Cost analysis** (if you ran Lab 8)

**Stopped EC2 is not free** (EBS and related charges can continue). Do not treat “instance stopped”
as “lab paid for.” Read what Cost Explorer shows for your account; credits may mask small amounts.

Check **Current plan**, remaining credits and expiry as well as costs. Free plan expiry or credit
exhaustion closes or suspends access rather than automatically rolling into **Paid**. Data recovery
during the **90-day** retention period requires a paid upgrade; save evidence before expiry. Do **not**
upgrade or create an organization as part of cleanup.

## 5. What to keep

<ul class="check">
<li>Your notes on the IRE rule that matched, and the reconciliation precedence you changed</li>
<li>The verifier output from Lab 4 (before) and Lab 9 (after drift)</li>
<li>Screenshots of Dependency Views for the service instance — that is the artifact worth showing</li>
</ul>

## Where to take this next

| Next step | Why it matters |
|---|---|
| Discovery (agentless) against the same VPC | Second source for the same CIs — real multisource reconciliation |
| Service Mapping on the application | Top-down map instead of bottom-up CIs |
| CMDB Health / data certification | Measure completeness and correctness, not just existence |
| Scheduled freshness job using `verify_cmdb.py` | Catch a silently broken connector |
| Now Assist / AIOps on top of the CMDB | Only meaningful once the CMDB is actually right |

Back to the [overview]({{ '/' | relative_url }}).
