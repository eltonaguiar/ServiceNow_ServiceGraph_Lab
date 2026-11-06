---
layout: default
title: Build a real AWS inventory
lab: 1
time: 20 min
level: AWS
order: 1
permalink: /labs/01-aws-inventory/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>Before you install an inventory tool, put some furniture in the house. If AWS is empty, the connector has nothing to find and you learn nothing.</p>
</div>

## Objective

Give the connector something real to discover: a VPC (Virtual Private Cloud), a subnet, a security group and one
tagged EC2 (Elastic Compute Cloud) instance. An empty AWS account works for the account-level import, but it produces
almost no CIs — you want hardware records.

## Option A — CloudFormation (recommended)

The template at
[`aws/lab-stack.yaml`](https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab/blob/main/aws/lab-stack.yaml)
creates exactly the resources this lab needs, all tagged:

```bash
# from a machine with the AWS CLI configured, in your chosen region
aws cloudformation deploy \
  --template-file aws/lab-stack.yaml \
  --stack-name sgclab \
  --parameter-overrides LabOwner=yourname \
  --capabilities CAPABILITY_NAMED_IAM
```

Or use the console: **CloudFormation → Create stack → With new resources → Upload a template
file**, then step through the defaults.

## Option B — Console clicks

1. **VPC → Create VPC** → "VPC and more", 1 AZ, 1 public subnet. Accept the default CIDR.
2. **EC2 → Launch instance**:
   - AMI (Amazon Machine Image): Amazon Linux 2023
   - Type: `t3.micro` (free-tier eligible in a new account)
   - Network: the VPC from step 1
   - **Tags** (this is the part that matters):
     | Key | Value |
     |---|---|
     | Name | sgclab-app-01 |
     | Environment | lab |
     | Owner | yourname |
     | Application | payments |
   - Security group: no inbound rules needed; do not open SSH to the world.
3. Launch, then **stop** the instance once it exists — a stopped instance still appears in
   inventory and costs nothing for compute.

## Why the tags matter

The connector maps AWS tags into CMDB fields and, in later labs, you will use `Application`
to attach CIs to a service. Tags are also how you will prove in Lab 4 that the data came from
AWS and not from you typing it.

## Record these values

| Value | Where |
|---|---|
| Instance ID (`i-…`) | EC2 → Instances |
| VPC ID (`vpc-…`) | VPC console |
| Region | Console URL |
| Account ID | Account menu |

## Checkpoint

<ul class="check">
<li><code>aws cloudformation describe-stacks --stack-name sgclab</code> shows <code>CREATE_COMPLETE</code> (or the console shows the same)</li>
<li>One instance exists with the four tags above</li>
<li>You have written down the instance ID and VPC ID</li>
<li>Budget alarm is still in place</li>
</ul>

Next: [Lab 2 — install the connector]({{ '/labs/02-sgc-install/' | relative_url }})
