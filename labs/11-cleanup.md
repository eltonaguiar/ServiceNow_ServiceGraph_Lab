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

Leave with no live keys, cloud resources torn down **where you can verify**, and billing checked in
the console. This lab does **not** guarantee a zero balance — especially if **AWS Config** or a
**retained S3 bucket** from `sg-aws-config` still exists ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }})).

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
