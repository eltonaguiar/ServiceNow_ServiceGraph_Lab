---
layout: default
title: Cleanup
lab: 11
time: 25 min
level: Wrap-up
order: 11
permalink: /labs/11-cleanup/
---

<div class="eli5">
<span class="label">ELI5</span>
<p><strong>Identity and Access Management (IAM)</strong> keys first — so nothing keeps calling <strong>Amazon Web Services (AWS)</strong> after you tear down cloud gear. <strong>AWS Config</strong> “recording” is not a video of your network or your app’s traffic; it is AWS writing <em>inventory notes</em> (configuration snapshots and change history) about selected resource types into a bucket. Stopping recording stops <em>new</em> notes — it does not erase old bucket objects or every charge by itself.</p>
</div>

<nav class="toc" aria-label="Lab 11 contents">
  <p class="toc-title">Required path</p>
  <ul class="toc-list">
    <li><a href="#lab11-credentials">1. Revoke credentials</a></li>
    <li><a href="#lab11-cloudformation">2. Delete lab stacks</a></li>
    <li><a href="#lab11-config-recording">3. AWS Config recording (ELI5 + stop)</a></li>
    <li><a href="#lab11-schedules">4. Stop ServiceNow schedules</a></li>
    <li><a href="#lab11-billing">5. Confirm billing</a></li>
    <li><a href="#lab11-checkpoint">Checkpoint</a></li>
  </ul>
  <p class="toc-title">Appendix (optional depth)</p>
  <ul class="toc-list">
    <li><a href="#lab11-config-appendix">What Config records (detail)</a></li>
    <li><a href="#lab11-connector-appendix">Connector vs Config (no fixed claim)</a></li>
    <li><a href="#lab11-keep">What to keep</a></li>
  </ul>
</nav>

## Objective

Leave with no live keys, cloud resources torn down **where you can verify**, and usage and credits
checked in the **correct** account. On a confirmed **AWS Free plan**, cleanup mainly prevents
unnecessary credit consumption; it does **not** extend the six-month plan limit. On **Paid** or
legacy accounts it also prevents continuing out-of-pocket charges.

Retained **AWS Config** / **Simple Storage Service (S3)** resources can continue **metered** usage. Do **not**
rely on eventual Free plan suspension as your cleanup procedure ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }})).

---

## 1. Revoke the credentials first
{: #lab11-credentials}

1. AWS → **IAM → Users → servicenow-sgc-lab → Security credentials** → **Deactivate**, then
   **Delete** the access key.
2. Delete the IAM user (or at least remove its policies).
3. In ServiceNow, delete or disable the connection / credential record the connector created.
4. Azure (optional Lab 8): delete client secret and Reader role assignment.

**Order matters:** kill keys before deleting resources so a leftover schedule cannot keep calling AWS.

### Observed progress snapshot (one lab account — yours may differ)

*Qualification: table reflects **verified UI at one point in time** during cleanup. It is **not** proof of zero AWS charges, not a guarantee every background delete finished, and **not** “Lab 11 complete” for all learners.*

| Check | Observed state (snapshot) | Notes |
|---|---|---|
| IAM access keys | **Access keys (0)** | Lab user cannot authenticate with deleted key |
| ServiceNow **AWS Default Connection** | **Active = false** | Schedules may still run — check **System Scheduler** |
| Stack **`sgclab`** | **DELETE_COMPLETE** | Lab VPC / EC2 template stack |
| **AWS Config → Settings** | Customer-managed recorder **Recording is off** (after **Confirm**) | **service-linked recorders (0)** |
| Stack **`sg-aws-config`** | **DELETE_COMPLETE** | Deleted with **CloudFormation Express mode** enabled — see caveat below |
| **Config S3 delivery bucket** | **Pending** | Template **`ConfigBucket`** uses **`DeletionPolicy: Retain`** — bucket **stays** after stack delete; user navigating **S3** to empty/delete |
| Stack **`sg-aws-snow-role`** | **Still active / pending cleanup** | Lab 3 STS role stack — delete when you are ready ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }}#lab3-config)) |
| IAM user **`servicenow-sgc-lab`** | **Pending** (if user not removed) | Delete user after keys |
| Billing | **Not verified here** | **Do not** assert $0 — use Cost Explorer |

**Express mode caveat:** With **[CloudFormation quick starts / accelerated operations](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stacks.html)** (Express mode) on delete, the console can show **DELETE_COMPLETE** while AWS **still finishes deleting some resources in the background**. Re-check the stack events, **S3**, **IAM** roles, and **Config** settings before you call teardown done.

**Why the bucket remains:** `EnableAWSConfig.yml` sets the delivery bucket **`DeletionPolicy: Retain`** so stack delete does **not** remove historical Config JSON in **S3** — you empty and delete the bucket yourself if you want objects gone ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }})).

---

## 2. Delete the cloud lab stack
{: #lab11-cloudformation}

```bash
aws cloudformation delete-stack --stack-name sgclab
aws cloudformation wait stack-delete-complete --stack-name sgclab
```

Confirm **CloudFormation → Stacks** shows **`sgclab`** **DELETE_COMPLETE** (or absent).

**Do not** delete **`sg-aws-config`** in the same breath without reading [§3](#lab11-config-recording) — Config has its own recorder, bucket, and billing footprint.

---

## 3. AWS Config recording — what it means and how to stop safely
{: #lab11-config-recording}

### ELI5 (required)

| Idea | Plain language |
|---|---|
| **What “recording” is** | AWS **Config** evaluates **supported resource types** you chose and writes **configuration items** — what the resource’s settings were and how they changed — per [How AWS Config works](https://docs.aws.amazon.com/config/latest/developerguide/how-does-config-work.html). |
| **What it is not** | **Not** packet capture, **not** application payloads, **not** ServiceNow writing to your CMDB by itself. |
| **Stop recording** | Stops **new** configuration tracking for that **customer-managed recorder** in that **Region** — AWS documents ongoing change capture tied to the recorder ([stop/start recording](https://docs.aws.amazon.com/config/latest/developerguide/stop-start-recorder.html)). |
| **What stop does not do** | Does **not** delete existing AWS resources, does **not** empty **S3** history already delivered, does **not** by itself remove other Regions’ recorders or every Config-related charge. |

Setup context and narrow resource types: [Lab 3 — AWS Config]({{ '/labs/03-iam-connection/' | relative_url }}#lab3-config).

### Small safe steps (you perform — not done in this repo)

1. **Console:** **AWS Config** → same **Region** as Lab 3 (e.g. **US East (Ohio)**) → **Settings**.
2. Under **Customer-managed recorder**, if **Recording is on**, choose **Stop recording** → **Confirm**.
3. **Verify:** **Recording is off**; **service-linked recorders (0)** on observed account after stop.
4. **CloudFormation:** Delete stack **`sg-aws-config`** when recording is off (same Region):

   ```bash
   aws cloudformation delete-stack --stack-name sg-aws-config
   aws cloudformation wait stack-delete-complete --stack-name sg-aws-config
   ```

5. **Express mode:** If you use accelerated delete, treat **DELETE_COMPLETE** as a milestone — confirm background cleanup per AWS guidance and stack **Events**.

6. **S3 bucket (required when `Retain`):** Open **S3** → delivery bucket → **Empty** (handle **versioning** if enabled) → **Delete bucket** when you accept **permanent data loss** for Config history objects. **Observed snapshot:** stack gone, **bucket cleanup still in progress**.

7. **Stack `sg-aws-snow-role`:** Delete when no longer needed (after connector identity teardown).

8. **Other Regions / accounts:** Repeat **Config Settings** per Region if recording was enabled elsewhere.

**Status:** Observed snapshot shows **recorder off** and **`sg-aws-config` DELETE_COMPLETE** — **retained S3**, **`sg-aws-snow-role`**, schedules, IAM user removal, and billing review may still be **pending**. **Do not** mark the whole lab complete or claim zero charges.

---

## 4. Stop the schedules
{: #lab11-schedules}

**System Scheduler → Scheduled Jobs** → deactivate AWS (and Azure, if used) import jobs.

**Active = false** on a connection record is **insufficient** proof schedules stopped.

---

## 5. Confirm the bill
{: #lab11-billing}

- AWS **Billing → Cost Explorer**, group by service, last 7 days
- **Budgets** — alarm warns; it is **not** a spend cap
- After Config teardown: confirm **Config** and **S3** lines trend down (lag is normal)
- Azure **Cost Management** if you ran Lab 8

**Stopped EC2 is not free** — **Elastic Block Store (EBS)** and related charges can continue.

---

## Checkpoint
{: #lab11-checkpoint}

<ul class="check">
<li><b>Observed on one account:</b> keys <b>0</b>; connection <b>Inactive</b>; <code>sgclab</code> and <code>sg-aws-config</code> <b>DELETE_COMPLETE</b>; Config recorder <b>off</b></li>
<li><b>Still open (same account):</b> retained <b>Config</b> S3 bucket; <code>sg-aws-snow-role</code>; full IAM user removal; schedules; Cost Explorer</li>
<li>You can explain Config <b>recording</b> vs traffic capture (ELI5 above)</li>
<li>You understand <b>DeletionPolicy: Retain</b> and <b>Express mode</b> delete caveats</li>
</ul>

<p><strong>Lab 11 is not marked complete</strong> in this doc — partial progress is documented honestly.</p>

---

## Further details (optional)
{: #lab11-config-appendix}

<details markdown="1">
<summary><strong>Configuration items, history files, and continuous recording</strong></summary>

Per AWS documentation ([How AWS Config works](https://docs.aws.amazon.com/config/latest/developerguide/how-does-config-work.html)):

- **Discovery** — when recording starts, Config creates **configuration items** for supported types in scope.
- **Change stream** — many changes produce notifications / stream delivery (minutes, best effort).
- **Periodic recording** — Config may also record on a **periodic** basis for some changes not seen via API alone.
- **S3 delivery** — **configuration history files** (per type, on an interval when changes occur) and **snapshots** on demand; JSON in **S3**, not “live video.”

Lab 3 narrowed types to EC2 Instance, VPC, Subnet, Security Group — fewer types → fewer recorded items, **not** zero cost by itself ([Config pricing](https://aws.amazon.com/config/pricing/)).

</details>

<details markdown="1">
<summary><strong>CloudFormation Express mode on delete (background cleanup)</strong></summary>

When **Express mode** (or similar accelerated stack operations) is enabled, **DELETE_COMPLETE** can appear before every physical resource is gone. Check **CloudFormation → Events**, **S3**, **IAM**, and **Config → Settings** again after a short wait. This does not replace [Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html) for whether usage stopped billing.

</details>

<details markdown="1">
<summary><strong>ServiceNow connector and AWS Config (avoid a single feed-path story)</strong></summary>
{: #lab11-connector-appendix}

[Lab 3 §0]({{ '/labs/03-iam-connection/' | relative_url }}) describes **connector documentation** requiring a **configuration recorder** and Config read APIs for the supported integration path. **This course does not prove** every import row on your instance came only from Config versus **Elastic Compute Cloud (EC2)** / other loader APIs — that requires your **import-set payload** and release notes.

Cleanup goal: stop **metered Config recording** and remove lab **recorder/delivery** infrastructure you deployed, independent of ServiceNow schedule state.

</details>

### What to keep
{: #lab11-keep}

<ul class="check">
<li>IRE / reconciliation notes from Labs 5–6</li>
<li>Verifier output from Labs 4 and 9</li>
<li>CSDM / dependency screenshots from Lab 7</li>
</ul>

Screenshots from cleanup runs are **not** embedded in this publish (transfer limitation) — verify in your own console.

---

## Sources
{: #lab11-sources}

| Topic | URL |
|---|---|
| How AWS Config works | https://docs.aws.amazon.com/config/latest/developerguide/how-does-config-work.html |
| Stop / start configuration recorder | https://docs.aws.amazon.com/config/latest/developerguide/stop-start-recorder.html |
| AWS Config pricing | https://aws.amazon.com/config/pricing/ |
| S3 object lifecycle | https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html |

## Where to take this next

| Next step | Why it matters |
|---|---|
| Discovery against the same VPC | Second source — multisource reconciliation |
| Service Mapping | Top-down map vs bottom-up CIs |
| CMDB Health | Measure correctness, not just existence |
| `verify_cmdb.py` on a schedule | Catch a silent connector failure |

Back to the [overview]({{ '/' | relative_url }}).
