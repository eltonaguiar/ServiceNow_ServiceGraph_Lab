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

### Observed on one lab account (cleanup in progress — not a template for yours)

| Check | Observed state | Implication |
|---|---|---|
| IAM access keys | **Access keys (0)** after delete | User cannot call AWS APIs with old key |
| ServiceNow connection | **AWS Default Connection** **Active = false** | **Not** proof ServiceNow schedules are off — verify **System Scheduler** separately |
| Stack **`sgclab`** | **DELETE_COMPLETE** | Lab VPC/EC2 stack removed when this status is shown |
| Stack **`sg-aws-config`** | **Still present** | Recorder, delivery channel, role, **SNS**, **S3** may still exist |

**AWS Config console (observed, not stopped yet):** **Settings** → customer-managed recorder → **Recording is on** → **Stop recording** available; **service-linked recorders (0)**. **Do not** document this as “already stopped” until you perform and verify the steps below.

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
2. Under **Customer-managed recorder**, confirm **Recording is on** (matches observed UI: **Stop recording** visible).
3. Choose **Stop recording** for that recorder → confirm per console prompts.
4. **Verify:** Settings shows recording **off** for that customer-managed recorder; note **service-linked recorders** separately if any appear later.
5. **CloudFormation:** When recording is stopped and you are ready, delete stack **`sg-aws-config`** (same Region):

   ```bash
   aws cloudformation delete-stack --stack-name sg-aws-config
   aws cloudformation wait stack-delete-complete --stack-name sg-aws-config
   ```

6. **S3 bucket (retention warning):** Lab 3 notes the template may **retain** the delivery bucket. After stack delete, open **S3** — if the bucket remains, **empty** it (versioned buckets may need **delete markers** / versions removed) before **Delete bucket**. **Permanent data loss** in that bucket if you delete without backup. See [S3 lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html) in AWS docs for long-term archive choices.

7. **Other Regions / accounts:** If you ever enabled Config elsewhere, repeat **Settings** per Region.

**Status:** This guide does **not** claim cleanup is finished until **you** complete and verify steps 3–6 on your account.

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
<li>IAM lab user keys deleted; connector connection disabled</li>
<li><code>sgclab</code> stack <b>DELETE_COMPLETE</b> (or equivalent verification)</li>
<li>You can explain Config <b>recording</b> in plain language (inventory snapshots — not traffic capture)</li>
<li>Customer-managed Config recorder <b>stopped</b> and verified in <b>Settings</b> — or honestly still pending</li>
<li><code>sg-aws-config</code> removed after stop; retained <b>S3</b> handled with data-loss awareness</li>
<li>ServiceNow import schedules deactivated</li>
<li>Billing/Cost Explorer reviewed on the <b>correct</b> account</li>
</ul>

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

No screenshot is embedded for **Stop recording** in this publish (transfer limitation) — use your **Settings** page when verifying.

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
