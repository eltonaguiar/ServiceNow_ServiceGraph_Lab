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
  Treat §1 as a lab identity only. ServiceNow's
  [Configure the AWS integration](https://www.servicenow.com/docs/r/servicenow-platform/service-graph-connectors/configure-aws-integration.html)
  page says a blank STS role field defaults to `SnowOrganizationAccountAccessRole`. That shows the
  connector expects an assumed role by default. It does **not** prove that direct IAM-user access is
  unsupported for a standalone account. This lab uses a custom assumed role (§0b).
- **Don't delete anything you already created.** Keep the existing user and policy until you have
  confirmed what replaces them.

> **Why we keep this standalone and narrow:** recording only **Elastic Compute Cloud (EC2)**
> instances, **virtual private cloud (VPC)** networks, subnets and security groups primarily
> conserves eligible **AWS Free plan** credits. It does **not** extend the six-month limit or cap
> usage. Do **not** create or join **AWS Organizations** or configure **AWS Control Tower** merely
> because a connector script or role name mentions organizations: those actions can trigger a paid
> upgrade and loss of Free Tier credit benefits. The custom same-account **Security Token Service
> (STS)** role is **not** organization enrollment. Keep the current recording scope unchanged while
> debugging partial import results.

### Safe next checkpoint: check AWS Config in your region (no changes)

1. In the console search bar at the top, type `AWS Config`. Under **Services**, choose **AWS Config**
   (Track Resource Inventory and Changes).

   ![AWS console search showing AWS Config under Services]({{ '/assets/img/lab03/console-search-aws-config.png' | relative_url }})
   *Choose the **AWS Config** service under Services. The search box may suggest extra words such as
   "Rules"; you only need the service result.*
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
   | Snapshot delivery frequency | `24hours` (default). This only sets how often a configuration *snapshot* is delivered to the bucket. It doesn't change how changes are recorded (the template doesn't set periodic recording), so don't expect the lower daily-recording price. |
   | Configuration delivery channel name, SNS topic name, Notification Email | leave the defaults |

3. **Configure stack options:** leave the defaults → **Next**.
4. **Review:** the template creates an IAM role (the Config recorder role), so tick the
   acknowledgement that CloudFormation might create IAM resources. Then click **Submit**.
5. Wait for the overall stack status to show **CREATE_COMPLETE**. Then check **AWS Config → Settings**:
   recording should be on, and only those four types should be recorded.

This step only turns on recording. It does **not** give the ServiceNow identity permission to read
Config. That permission comes from the connector's identity setup (§0). Don't start imports until
the identity is settled and the Diagnostic Tool passes. Imports are Lab 4.

### Already submitted the default template? Narrow the existing stack

If `sg-aws-config` is already **CREATE_COMPLETE** with the defaults (all resource types), update it.
Don't create a second stack.

1. CloudFormation → select **`sg-aws-config`**, not `sgclab`. Open **Update stack** →
   **Make a direct update** → **Use existing template** → **Next**.
2. Change only these three parameters:
   - **Support all resource types** = `False`.
   - **Include global resource types** = `False`.
   - **List of resource types** = `AWS::EC2::Instance,AWS::EC2::VPC,AWS::EC2::Subnet,AWS::EC2::SecurityGroup`.

   Leave all other parameters and options unchanged → **Next**.
3. On the review page, tick the IAM acknowledgement only if it appears. Then click **Submit**
   (or **Update stack**).
4. Wait for the overall stack status to show **UPDATE_COMPLETE**.
5. Search the console for `AWS Config`, open the service, and confirm the region is **US East (Ohio)
   `us-east-2`**. Under **Settings**, check that recording is **On** (continuous) and limited to those
   four types. If it doesn't match, stop. Don't change IAM and don't run imports.

**ELI5:** you're telling AWS Config to keep notes on only four kinds of things: EC2 instances,
VPCs, subnets and security groups. Fewer kinds of notes means fewer recorded changes and lower
cost.
- **Narrowing deletes nothing.** It also doesn't cap spending.
- **"Global" types such as IAM are left out,** because this lab doesn't need them. Add more types
  later if a lab needs them.
- **Snapshot delivery frequency (`24hours`)** only controls how often snapshots are delivered.
  Recording itself stays continuous.
- **The recorder starts on its own.** AWS's
  [ConfigurationRecorder reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-config-configurationrecorder.html)
  says: "AWS CloudFormation starts the recorder as soon as the delivery channel is available."
- **Changing the recording group causes no interruption.** It only affects what is recorded from
  then on, and doesn't undo costs already incurred.
- **Budget alerts only warn you.** They don't cap spending.

## 0b. Connector STS role: custom lab template

The connector assumes an IAM role through STS. That is **not** the same thing as an EC2/SSM
instance role. The official `CreateSnowOrganizationAccountAccessRoleInMemberAccount.yml` also
grants SSM `SendCommand`, S3 read/delete and access-key changes, and it needs an S3 bucket and
an account ID. This repo provides
[`aws/sgc-lab-inventory-role.yml`](https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab/blob/main/aws/sgc-lab-inventory-role.yml).

**What it is:**
- A **custom derivative**, not an official ServiceNow template, and not tested end to end. It
  passes `cfn-lint`, and one lab deployment reached CREATE_COMPLETE.
- It creates `SnowOrganizationAccountAccessRole` in **this** account.
- The role is trusted only by the IAM user you name, which defaults to `servicenow-sgc-lab`.
- It grants the bundle's inventory read actions: Organizations, Config, Config aggregator, EC2,
  SSM inventory and Tagging.
- It drops SendCommand, S3 and key-rotation permissions. What remains is broad read access, not
  strict least privilege.

**Create the role stack:**
1. Download `aws/sgc-lab-inventory-role.yml` from the repo.
2. CloudFormation (Ohio) → **Create stack → With new resources (standard)** → **Upload a template
   file** → choose the file → **Next**.
3. **Stack name:** `sg-aws-snow-role`. **ServiceNowUserName:** `servicenow-sgc-lab`, or your own
   user name → **Next**.
4. **Configure stack options:** leave the defaults, including the rollback behaviour → **Next**.
5. **Review:** tick the acknowledgement that CloudFormation might create IAM resources with custom
   names → **Submit**.
6. Wait for **CREATE_COMPLETE**. The **Outputs** tab shows the role name to enter in the
   ServiceNow STS Role field.

![CloudFormation stack list with sg-aws-snow-role CREATE_COMPLETE]({{ '/assets/img/lab03/role-stack-success.png' | relative_url }})
*Example: `sg-aws-snow-role` is CREATE_COMPLETE, alongside `sg-aws-config` (UPDATE_COMPLETE after
narrowing) and `sgclab`.*

**Next: let the user assume the role (inline policy).**
1. IAM → **Users** → `servicenow-sgc-lab` → **Permissions** → **Add permissions** → **Create inline
   policy** → **JSON**.
2. Click inside the editor, press **Ctrl+A** so that only the editor text is selected, and replace
   *all* the starter text with:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowAssumeSnowRoleSameAccount",
         "Effect": "Allow",
         "Action": "sts:AssumeRole",
         "Resource": "arn:aws:iam::ACCOUNT_ID:role/SnowOrganizationAccountAccessRole"
       }
     ]
   }
   ```

   Replace `ACCOUNT_ID` with your own 12-digit ID. The same JSON is in
   [`aws/sgc-lab-assume-role-policy.json`](https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab/blob/main/aws/sgc-lab-assume-role-policy.json).
3. **Next** → **Policy name:** `SnowAssumeRole` → **Create policy**, and wait for the success banner.
4. Keep `ServiceNowSGCLabReadOnly` attached. The user's **Permissions** tab should now list both
   `ServiceNowSGCLabReadOnly` and `SnowAssumeRole`.

<ul class="check">
<li>The user has both policies, and the role stack is CREATE_COMPLETE</li>
</ul>

## 0c. ServiceNow Guided Setup, in order

1. **Download the scripts** → mark complete.
2. **AWS Setup Instructions** is just an instructions page. Marking it complete only unlocks the
   next task; it validates nothing.
3. **Credentials:**
   - Make sure the application scope is **Service Graph Connector for AWS** → **Configure**.
   - Open the existing **SG-AWS-CredentialAlias-Org** → **Edit**.
   - Use no MID Server. Enter the real IAM user's access key and secret **only in ServiceNow**,
     never in chat or a file.
   - Leave GovCloud off.
   - Save, then mark the credentials task complete.
4. **Configure the instance before testing.** This is a tentative checkpoint the lab hasn't verified yet:

   | Field | Value |
   |---|---|
   | Credential alias | `SG-AWS-CredentialAlias-Org` |
   | STS Role | `SnowOrganizationAccountAccessRole`. Enter the role **name** only, not the ARN. |
   | Regions | `us-east-2` |
   | Standalone Account ID | your own 12-digit ID (required) |
   | Management account, Aggregator, S3 bucket | blank |
   | Key rotation, GovCloud | unchecked |
   | SSM documents | leave unchanged |
   | Organization Account / Name | if the form shows literal placeholders such as `<ORG_ID>` or `<ORG_NAME>`, clear them and leave the fields blank |

   - **Account ID may be hidden.** A filled-in account ID can appear masked or blank in the form or
     in a screenshot, so don't assume it's missing. Check the field itself.
   - **Save once,** after the Standalone Account ID is entered. On a verified standalone run,
     **blank** Management account, Aggregator, and Organization Account / Name fields were
     **accepted** after clearing literal placeholders such as `<ORG_ID>` / `<ORG_NAME>`.
     If ServiceNow rejects the save, note the exact error and stop — don't invent org values.
   - **Only after Save succeeds,** click **Test Connection**. On a verified standalone instance
     the UI showed the exact message **`Test Connection feature not available for Standalone Account`**.
     That is **not** an authentication failure — it only means this button is unsupported in
     standalone mode. Absence of credential errors in the Import Log is likewise **not** proof
     that AWS calls will succeed; the first real proof is Lab 4's scheduled imports and CI lists.

   Verified on a standalone walkthrough: credential alias saved, instance saved with
   `SnowOrganizationAccountAccessRole`, region `us-east-2`, Standalone Account ID populated,
   org/aggregator fields blank. Imports are Lab 4.
5. **Diagnostic Tool:** skip SSM setup, SSM Deep Discovery and EKS. A green connection test on
   its own doesn't show that imports will work, so run the diagnostics before any import (Lab 4).

### Metered usage and credit conservation

- **AWS Config:** usage is metered per configuration item recorded, with additional evaluations if
  rules are configured. Narrow recording reduces metered usage and eligible credit consumption; it is
  **not** a guarantee of zero cost or a spend cap. Check [current Config pricing](https://aws.amazon.com/config/pricing/)
  and your account’s credit coverage before deployment.
- **Simple Storage Service (S3)** and **Simple Notification Service (SNS):** metered usage may
  consume eligible credits; on Paid or legacy accounts uncovered usage can be charged. Check actual
  billing. A genuine Free plan expiring does **not** by itself roll into Paid.
- **After deleting the stack:** the retained bucket is still there. Empty and delete it yourself
  in [Lab 11]({{ '/labs/11-cleanup/' | relative_url }}).
- **Cleanup:** deleting the `sg-aws-config` stack removes the recorder, delivery channel, role and topic. Afterwards, check that **AWS Config → Settings** shows no recorder still on. If you created a recorder another way, stop it there. The retained S3 bucket stays and keeps its objects until you empty and delete it. Keep the Lab 0 budget alert on.

Optional Guided Setup groups (aggregator, SSM, key rotation, email notification) are for
multi-account, deep-discovery or production use. Only mark a group skipped after your release's
Guided Setup confirms it is optional. Run the connector's **Diagnostic Tool** before scheduling
imports.

## 1. Create a dedicated IAM (Identity and Access Management) user

> **Lab identity, not verified as sufficient.** The user and policy in this section have no AWS
> Config read access, and they are not the connector's official identity setup (§0). You can create
> them, but **don't treat §2–§3 as complete, and don't run imports (Lab 4)**, until your release's
> identity prerequisites are confirmed. Keep anything you created; don't delete it.

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

> **Stop here until the identity is settled.** Only enter credentials once your release's Guided
> Setup has confirmed which identity it needs: this lab user, or the connector's user and role
> from §0. Don't schedule or run imports yet.

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
| **`Test Connection feature not available for Standalone Account`** (verbatim on one verified run) | Standalone instance profile — **not** a failed auth test | Continue to Lab 4; prove connectivity with scheduled imports |
| `InvalidClientTokenId` | Key ID wrong or deleted | Recreate the access key |
| `SignatureDoesNotMatch` | Secret typo, or trailing whitespace when pasted | Re-enter the secret |
| `AccessDenied` on `ec2:DescribeInstances` | Policy not attached, or attached to the wrong user | Recheck the user's policies |
| `AccessDenied` on a `config:` action, or an empty import | Config not enabled in the region, or the identity has no Config read access | Go back to §0. Don't add permissions by trial and error. |
| Timeout / 403 from ServiceNow | Outbound REST blocked or proxy in the way | See [Troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }}) |

## Checkpoint

<ul class="check">
<li>A dedicated IAM user exists with read-only permissions and no console access, and you know it is <b>not yet confirmed</b> for Config-based imports (§0)</li>
<li>AWS Config recording is on in your region, or you know why not</li>
<li>One access key exists; instance settings saved (standalone account ID, STS role, region). A green or unavailable Test Connection does <b>not</b> prove imports work — Lab 4 does.</li>
<li>Keys are in ServiceNow only — not in a file, chat, or commit</li>
</ul>

Next: [Lab 4 — run the import]({{ '/labs/04-run-import/' | relative_url }})
