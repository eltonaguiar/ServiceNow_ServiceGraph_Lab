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
creates exactly the resources this lab needs, all tagged. **Clone the repo or download the file
first** ([Lab 0 §4]({{ '/labs/00-prerequisites/' | relative_url }})) — the command below assumes
you are in the repo root.

```bash
# from a machine with the AWS CLI configured, in your chosen region
aws cloudformation deploy \
  --template-file aws/lab-stack.yaml \
  --stack-name sgclab \
  --parameter-overrides LabOwner=yourname \
  --capabilities CAPABILITY_NAMED_IAM
```

### Option A in the console, step by step

Open the [CloudFormation console](https://us-east-2.console.aws.amazon.com/cloudformation/home?region=us-east-2)
(or replace `us-east-2` with whatever region you chose in Lab 0). The link opens in the AWS
account you are signed in to.

**Confirm the region in the console itself, not just the URL.** At the top right, next to your
account menu, is the region selector. Click it and choose **US East (Ohio) `us-east-2`**, or your
Lab 0 region. Check it again before each step below. The stack, the instance and the later import
all have to be in the same region.

1. **Create stack → With new resources (standard)**.
2. **Prepare template:** *Choose an existing template*. **Template source:** *Upload a template file* →
   **Choose file** → `aws/lab-stack.yaml` → **Next**.
3. **Specify stack details:**

   | Field | Value |
   |---|---|
   | Stack name | `sgclab` |
   | ApplicationTag | `payments` (default) |
   | InstanceType | `t3.micro` (default) |
   | LabOwner | your name or handle, e.g. `yourname` |
   | LatestAmazonLinuxAmi | leave the default `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64` |

   Click **Next**.

   ![Specify stack details page with the template parameters]({{ '/assets/img/lab01/cfn-specify-stack-details.png' | relative_url }})
   *Example: the Specify stack details page before you fill it in. Type `sgclab` in Stack name and
   change LabOwner from `labuser` to your own name. Leave the other values as they are.*

4. **Configure stack options:** leave every default → **Next**.
5. **Review and create:** check the stack name and parameters → **Submit**. This template only
   creates a VPC, a subnet, a security group and one EC2 instance, with no IAM resources, so
   no IAM-capabilities checkbox should appear. If one does, you are using a different template.

### Wait for CREATE_COMPLETE

- After Submit, the stack shows **CREATE_IN_PROGRESS**. That is normal and usually lasts 2–5 minutes.
- Open the **Events** tab and click the refresh button now and then.
- **The Events tab is a history, not a checklist.** Every resource writes a
  `CREATE_IN_PROGRESS` row when it starts and a separate `CREATE_COMPLETE` row when it finishes.
  The old in-progress rows stay in the list. Don't wait for every row to change.
- **The status to watch is the overall `sgclab` stack status**, shown in the stack list on the
  left and under **Stack info**. When it reads **CREATE_COMPLETE**, you are done. The newest
  event, at the top of Events, is the stack itself reaching `CREATE_COMPLETE`.

<ul class="check">
<li>The <code>sgclab</code> stack status is <strong>CREATE_COMPLETE</strong></li>
<li>The <strong>Resources</strong> tab lists LabVpc, LabSubnet, LabSecurityGroup and LabInstance</li>
</ul>

**If it fails:** a status such as `CREATE_FAILED`, `ROLLBACK_IN_PROGRESS` or `ROLLBACK_COMPLETE`
means the stack did not build. Don't go on to Lab 2. In **Events**, find the first
`CREATE_FAILED` row and read its **Status reason**. Common causes:

- Instance type not available in that region or Availability Zone: choose `t2.micro` or `t3.small`.
- A service quota or vCPU limit was hit.
- The account has not finished activating.

Delete the failed stack, fix the cause, then create it again with the same name.

### Record the IDs from the Resources tab

Open the `sgclab` stack → **Resources** tab. Each row has a **Logical ID**, the name from the
template, and a **Physical ID**, the real AWS ID:

| Logical ID | Physical ID looks like | Record as |
|---|---|---|
| `LabInstance` | `i-…` | Instance ID |
| `LabVpc` | `vpc-…` | VPC ID |

You can also open the **Outputs** tab, which lists `InstanceId`, `VpcId` and `Region` from the
template.

### Then stop (don't terminate) the instance

In the Resources tab, click the **Physical ID** link on the `LabInstance` row (`i-…`). That opens the
instance in the EC2 console, in the same region. Or go to **EC2 → Instances** and pick
`sgclab-app-01`. Then choose **Instance state → Stop instance**. Do **not** choose *Terminate*.

**Why stop it?**
- A stopped instance has no compute (per-hour instance) charge.
- The Service Graph Connector for AWS discovers resources through AWS APIs, not by logging in to
  the OS. A **stopped** instance and its tags still show up in the inventory.
- A **terminated** instance is deleted, so there is nothing to discover. That is why you stop it
  rather than terminate it.

- A stopped instance has no compute charge, but its EBS volume is still billed. Any public IPv4
  address or other attached resource may also cost money.
- `t3.micro` is only free-tier eligible for some accounts and periods. It may not be free in yours,
  so check Billing.
- [Lab 11]({{ '/labs/11-cleanup/' | relative_url }}) deletes the stack when you are finished.

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
   inventory and costs nothing for compute. Do this immediately, not "after the import".

## Why the tags matter

The connector maps AWS tags into CMDB fields and, in later labs, you will use `Application`
to attach CIs to a service. Tags are also how you will prove in Lab 4 that the data came from
AWS and not from you typing it.

## Record these values

| Value | Where |
|---|---|
| Instance ID (`i-…`) | CloudFormation → `sgclab` → Resources → `LabInstance` Physical ID (or Outputs → `InstanceId`) |
| VPC ID (`vpc-…`) | CloudFormation → `sgclab` → Resources → `LabVpc` Physical ID (or Outputs → `VpcId`) |
| Region | Region selector at the top right of the console (e.g. US East (Ohio) `us-east-2`), or Outputs → `Region` |
| Account ID | Account menu |

## Checkpoint

<ul class="check">
<li><code>aws cloudformation describe-stacks --stack-name sgclab</code> shows <code>CREATE_COMPLETE</code> (or the console shows the same)</li>
<li>One instance exists with the four tags above</li>
<li>You have written down the instance ID and VPC ID</li>
<li>Budget alarm is still in place</li>
</ul>

Next: [Lab 2 — install the connector]({{ '/labs/02-sgc-install/' | relative_url }})
