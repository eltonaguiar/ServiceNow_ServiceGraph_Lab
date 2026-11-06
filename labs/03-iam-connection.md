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
4. Create the user, then **Security credentials → Create access key → Application running
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
| Timeout / 403 from ServiceNow | Outbound REST blocked or proxy in the way | See [Troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }}) |

## Checkpoint

<ul class="check">
<li>A dedicated IAM user exists with read-only permissions and no console access</li>
<li>One access key exists, and ServiceNow's test returns success</li>
<li>Keys are in ServiceNow only — not in a file, chat, or commit</li>
</ul>

Next: [Lab 4 — run the import]({{ '/labs/04-run-import/' | relative_url }})
