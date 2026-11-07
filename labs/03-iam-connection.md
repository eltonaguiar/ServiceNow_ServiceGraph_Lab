---
layout: default
title: Read-only IAM and the connection
lab: 3
time: 20 min
level: AWS + ServiceNow
order: 3
permalink: /labs/03-iam-connection/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>Give the connector a key that can <em>look</em> at AWS but never <em>touch</em> it, then prove the key works before running anything.</p>
</div>

## Objective

Create the least-privilege identity the connector uses, then wire it into ServiceNow and prove
the connection works.

## 0. Read first: AWS Config is required, and this lab's policy is not the connector's official setup

ServiceNow's public docs say the connector needs **AWS Config with a configuration recorder**
turned on in every account and region you import from
([AWS resources used by the connector](https://www.servicenow.com/docs/r/servicenow-platform/service-graph-connectors/sgc-cmdb-aws-concepts.html)).
The connector ships CloudFormation scripts for this. Download them from the **Download the scripts**
task in Guided Setup. The scripts are described in
[Executing scripts required for setting up AWS](https://www.servicenow.com/docs/r/australia/servicenow-platform/service-graph-connectors/sgc-cmdb-aws-script-op.html).

What the downloaded bundle (scripts v2.13, Feb 2026) actually contains:

- **`EnableAWSConfig.yml`** creates:
  - an S3 delivery bucket. Its `DeletionPolicy` is *Retain*, so deleting the stack leaves the bucket.
  - a bucket policy.
  - a recorder role using the AWS managed `AWS_ConfigRole` policy.
  - the configuration recorder and a delivery channel.
  - by default, a new SNS topic.

  It has these parameters:
  - `AllSupported` (`True`/`False`, default `True`).
  - `IncludeGlobalResourceTypes` (`True`/`False`, default `True`).
  - `ResourceTypes`, which is only used when `AllSupported` is `False`.
  - `Frequency` (`1hour`–`24hours`, default `24hours`).
  - `TopicArn` and `NotificationEmail`.
- **The ServiceNow identity scripts are built for AWS Organizations.**
  - `CreateServiceNowUser.yml` creates a user, whose name must be **6–15 characters**, so
    `servicenow-sgc-lab` (18) won't fit. It also creates the group `SnowMemberAccountAccessGroup`,
    which may `sts:AssumeRole` a named role in *any* account. The user can rotate its own access key.
  - The connector's read permissions, including `config:ListDiscoveredResources`,
    `config:SelectResourceConfig` and `config:BatchGetResourceConfig`, live in the
    **role** created by `CreateSnowOrganizationAccountAccessRoleInMemberAccount.yml`. That role
    asks for a management/designated account ID, the user name and an S3 bucket for
    SSM `SendCommand` output.
- **SSM and deep-discovery scripts** are optional. They only matter for software inventory from a
  **running** instance with an SSM instance profile. This lab's `sgclab` stack creates no
  instance profile, and its instance is stopped.

What this means for this lab:

- **The custom policy in §1 has no `config:` actions.** On its own it is probably not enough for
  the connector's Config-based import. Don't fix it by adding permissions one by one from error
  messages, and don't fall back to `ReadOnlyAccess`.
- **This lab has not verified a single-account (non-Organizations) setup.** That includes whether a
  plain IAM user with Config read actions, and no assume-role, works on your connector release.
  Treat §1 as a lab identity only. Follow your release's Guided Setup for the official identity,
  and if it requires the Organizations role, use that role.
- **Don't delete anything you already created.** Keep the existing user and policy until you have
  confirmed what replaces them.

### Safe next checkpoint: check AWS Config in your region (no changes)

1. In the console search bar at the top, type `Config`. Under **Services**, choose **AWS Config**.
2. Confirm the region selector at the top right shows **US East (Ohio) `us-east-2`**, or your Lab 0
   region.
3. Open **Settings**, or the getting-started page if Config has never been set up, and only *read* it:
   - **Recorder already exists:** don't run `EnableAWSConfig.yml`. AWS allows only one customer-managed
     recorder per account and region, so the stack would conflict with it. Never delete a recorder someone else
     created.
   - **No recorder:** running `EnableAWSConfig.yml` will start billing. Read the costs below first.
     For this lab, consider `AllSupported` = `False`,
     `ResourceTypes` = `AWS::EC2::Instance,AWS::EC2::VPC,AWS::EC2::Subnet,AWS::EC2::SecurityGroup`
     and `IncludeGlobalResourceTypes` = `False`. Leave the other defaults.

### If there is no recorder: create the `sg-aws-config` stack

Do this only after reading the costs below. Stay in your Lab 0 region.

1. CloudFormation → **Create stack → With new resources (standard)** → **Upload a template file** →
   `EnableAWSConfig.yml` from the downloaded ZIP → **Next**.
2. **Stack name:** `sg-aws-config`. Change these parameters from their defaults:

   | Parameter | Value |
   |---|---|
   | Support all resource types (`AllSupported`) | `False` |
   | Include global resource types (`IncludeGlobalResourceTypes`) | `False` |
   | List of resource types (`ResourceTypes`) | `AWS::EC2::Instance,AWS::EC2::VPC,AWS::EC2::Subnet,AWS::EC2::SecurityGroup` |
   | Snapshot delivery frequency | `24hours` (default) |
   | Configuration delivery channel name, SNS topic name, Notification Email | leave the defaults |

3. **Configure stack options:** leave the defaults → **Next**.
4. **Review:** the template creates an IAM role (the Config recorder role), so tick the
   acknowledgement that CloudFormation might create IAM resources. Then click **Submit**.
5. Wait for the overall stack status to show **CREATE_COMPLETE**. Then check **AWS Config → Settings**:
   recording should be on, and only those four types should be recorded.

This step only turns on recording. It does **not** give the ServiceNow identity permission to read
Config. That permission comes from the connector's identity setup (§0). Don't start imports until
the identity is settled and the Diagnostic Tool passes. Imports are Lab 4.

### Costs (not free)

- **AWS Config:** billed per configuration item recorded, plus rule evaluations if you add rules
  ([AWS Config pricing](https://aws.amazon.com/config/pricing/)). It is not part of a free tier.
  Recording only a few resource types keeps it small.
- **S3 and SNS:** the delivery bucket and SNS topic bill at their standard rates.
- **After deleting the stack:** the retained bucket is still there. Empty and delete it yourself
  in [Lab 11]({{ '/labs/11-cleanup/' | relative_url }}).
- **Cleanup:** stop or delete the recorder when the lab is finished. Keep the Lab 0 budget alert on.

Optional Guided Setup groups (aggregator, SSM, key rotation, email notification) are for
multi-account, deep-discovery or production use. Only mark a group skipped after your release's
Guided Setup confirms it is optional. Run the connector's **Diagnostic Tool** before scheduling
imports.

## 1. Create a dedicated IAM (Identity and Access Management) user

1. AWS console → **IAM → Users → Create user** → name `servicenow-sgc-lab`.
2. **Do not** enable console access. This identity only calls APIs.
3. Permissions → **Attach policies directly** → **Create policy** → **JSON**, and paste
   [`aws/iam-readonly-lab-policy.json`](https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab/blob/main/aws/iam-readonly-lab-policy.json)
   (from the cloned repo — see [Lab 0 §4]({{ '/labs/00-prerequisites/' | relative_url }})).

   It grants only describe/list/get shapes: `ec2:Describe*`, `s3:ListAllMyBuckets`,
   `s3:GetBucketLocation`, `ssm:Describe*`, `organizations:Describe*`, `iam:Get*`/`List*`,
   `tag:Get*`. Nothing in it can create, modify or delete a resource — which is the property
   that matters when you hand a key to a cloud service.

   **Start here, not with `ReadOnlyAccess`.** The managed `ReadOnlyAccess` policy also works,
   and you may fall back to it if you cannot tell which action is missing, but understand what
   you are handing over: read access to **every service in the account**, including billing
   data, all S3 object listings and every secret-adjacent describe call. For a throwaway lab
   account that is tolerable; it is not a pattern to carry into work, and the shadow it casts
   is exactly why least privilege exists.
   **Finish creating the policy.** *Create policy* usually opens in a new browser tab:
   1. After pasting the JSON, click **Next** at the bottom right of *Specify permissions*. Seeing
      no errors in the policy editor only means the JSON is valid. It is not a full security review.
   2. On **Review and create**, set **Policy name** to `ServiceNowSGCLabReadOnly`. This is just the
      lab's naming convention, and any clear name works. **Description:** `Read-only AWS inventory
      permissions for the ServiceNow Service Graph lab.` Leave **Tags** empty.
   3. Review the permissions summary. It should list read-only actions (Describe/List/Get) for
      EC2, S3, SSM, Organizations, IAM and Tagging only. Then click **Create policy** and wait for
      the success banner.
   4. Go back to the *Create user* tab. Click the refresh button on the policy list, search for
      `ServiceNowSGCLabReadOnly`, tick its checkbox, and attach only that policy. Do not add
      `AdministratorAccess` or other managed policies. Click **Next**, review that the user is `servicenow-sgc-lab` with no console access, then
      **Create user**.
   5. Already created the user without the policy? Open **IAM → Users → `servicenow-sgc-lab` →
      Permissions → Add permissions → Attach policies directly**. Select `ServiceNowSGCLabReadOnly`,
      then **Next → Add permissions**.
4. Open the user, go to **Security credentials → Create access key → Application running
   outside AWS**.
5. Copy the **Access key ID** and **Secret access key** now. The secret is shown once.

## 2. Enter the credentials in ServiceNow

Use whichever setup surface you found in Lab 2.

| Field | Value |
|---|---|
| AWS Account ID | your 12-digit account ID |
| Region(s) | the one region you chose in Lab 0 |
| Access key ID | `AKIA…` |
| Secret access key | the secret from step 1.5 |

> The **exact** action list the connector calls changes between connector versions. The
> authoritative list for your version ships with the connector itself: **Guided Setup →
> prerequisites** links a downloadable CloudFormation template (and a ServiceNow KB article)
> whose embedded policy is the current minimum. If a `Describe*` call fails on a newer release,
> take the action name from the import-set error and add it to your custom policy — do not
> switch wholesale to `ReadOnlyAccess` just because it is easier.

Notes that save time:

- The connector stores these in a **credential record it manages** (a connection & credential
  alias). You never paste keys into a ticket, a description field, or a git repo.
- If your release asks for a **MID Server** (the agent ServiceNow runs inside your own network), you have opened the discovery integration rather
  than the Service Graph Connector. The SGC path is cloud-to-cloud and needs no MID.
- If the release offers **"Use IAM role"** instead of keys, you can skip the access key — but
  only when ServiceNow can assume the role, which a PDI cannot. Use keys here.

## 3. Test the connection

Click **Test connection** (Guided Setup) or **Validate** (SGC Central).

| Result | Meaning | Do this |
|---|---|---|
| Green / "Connection successful" | Credentials and region are correct | Continue |
| `InvalidClientTokenId` | Key ID wrong or deleted | Recreate the access key |
| `SignatureDoesNotMatch` | Secret typo, or trailing whitespace when pasted | Re-enter the secret |
| `AccessDenied` on `ec2:DescribeInstances` | Policy not attached, or attached to the wrong user | Recheck the user's policies |
| `AccessDenied` on a `config:` action, or an empty import | Config not enabled in the region, or the identity has no Config read access | Go back to §0. Don't add permissions by trial and error. |
| Timeout / 403 from ServiceNow | Outbound REST blocked or proxy in the way | See [Troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }}) |

## Checkpoint

<ul class="check">
<li>A dedicated IAM user exists with read-only permissions and no console access</li>
<li>One access key exists, and ServiceNow's test returns success</li>
<li>Keys are in ServiceNow only — not in a file, chat, or commit</li>
</ul>

Next: [Lab 4 — run the import]({{ '/labs/04-run-import/' | relative_url }})
