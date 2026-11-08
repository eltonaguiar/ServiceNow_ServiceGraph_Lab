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

### Why targeted lab cleanup (not “close the whole AWS account”)

On a **shared** AWS account, other teams or personal workloads may still run. **Lab cleanup** removes **Service Graph lab** stacks, keys, Config recording, and connector schedules — it is **not** the same as account closure. A **disabled ServiceNow connection** and **deleted CloudFormation stacks** also **do not** guarantee every **billable** artifact is gone (retained **S3**, snapshots, Elastic IPs, other regions, or non-lab resources).

---

## 1. Revoke the credentials first
{: #lab11-credentials}

1. AWS → **IAM → Users → servicenow-sgc-lab → Security credentials** → **Deactivate**, then
   **Delete** the access key. **Access keys (0)** means **credentials are revoked** — AWS APIs
   no longer accept that key. That is the **required** stop for scheduled connector calls.
2. **Optional:** delete the IAM user (and inline policies) when you are done with the lab identity.
   Keeping the empty user record does **not** restore API access without a new key.
3. In ServiceNow, delete or disable the connection / credential record the connector created.
4. Azure (optional Lab 8): delete client secret and Reader role assignment.

**Order matters:** kill keys before deleting resources so a leftover schedule cannot keep calling AWS.

### Observed progress snapshot (one lab account — yours may differ)

*Qualification: table reflects **verified UI at one point in time** during cleanup. It is **not** proof of zero AWS charges, not a guarantee every background delete finished, and **not** “Lab 11 complete” for all learners.*

| Check | Observed state (snapshot) | Notes |
|---|---|---|
| IAM access keys | **Access keys (0)** — **revoked** | Connector cannot authenticate; distinct from optional user delete ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }}#lab3-iam-programmatic)) |
| IAM user **`servicenow-sgc-lab`** | **Still present (optional cleanup)** | User delete is **not** required once keys are gone |
| ServiceNow **AWS Default Connection** | **Active = false** | Parent scheduling chain addressed in [§4](#lab11-schedules) |
| Stacks **`sgclab`**, **`sg-aws-config`**, **`sg-aws-snow-role`** | **All DELETE_COMPLETE** | Three lab stacks gone on observed account |
| Role **`SnowOrganizationAccountAccessRole`** | **DELETE_COMPLETE** (with snow-role stack) | Verify in **IAM → Roles** if stack used Express mode |
| **AWS Config → Settings** | Customer-managed recorder **Recording is off** | **service-linked recorders (0)** |
| **Config S3 bucket (`ConfigBucket`, Retain)** | **Emptied and deleted** | **16** objects, **19.8 KB**, **0** failures, then bucket delete |
| **Ohio (`us-east-2`) footprint** | **Volumes 0**; **owned snapshots 0**; **Elastic IPs 0**; lab **EC2 Terminated** | Spot-check other regions if you used them |
| **Cost Explorer** (unfiltered Nov MTD, group by service) | **$0.00 total**, **0 services** | **Snapshot only** — lag and filters matter; not “never charged again” |
| **Credits / invoice** (observed) | **~140** remaining of **400** total; est. used **~100** base + **20** budget + **20** EC2 launch rewards | [Billing estimates](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-what-is.html) can lag **~24h**; invoice **finalizes** totals |
| **Parent schedule `SG-AWS-Organization`** | **Inactive** — **verified** | Stops the **scheduled chain** that fans out child imports ([§4](#lab11-schedules)) |
| **Child `SG-AWS-*` schedules (24)** | **Active = true** (snapshot) | **After Parent Runs** — parent inactive; do **not** claim all children inactive |
| **CMDB CIs from imports** | Rows may remain (e.g. Storage-Volume) | **Learning records** — not AWS metered resources; **no requirement** to delete CIs for billing cleanup |

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

6. **S3 bucket (required when `Retain`):** Open **S3** → delivery bucket → **Empty** (handle **versioning** if enabled) → **Delete bucket** when you accept **permanent data loss** for Config history objects. **Observed snapshot:** **16** objects emptied, bucket deleted.

7. **Stack `sg-aws-snow-role`:** Delete when no longer needed (after connector identity teardown). **Observed snapshot:** **DELETE_COMPLETE**.

8. **Other Regions / accounts:** Repeat **Config Settings** per Region if recording was enabled elsewhere.

**Status:** Observed snapshot shows **three stacks deleted**, **Config off**, **retained bucket removed**, **Ohio lab compute/storage checks clean**, **keys revoked**, and **parent AWS schedule inactive (verified)** — **child schedules may still show Active**; **optional** IAM user delete; **billing** estimate lag. **Do not** mark Lab 11 complete for all learners or claim universal $0 / no future charges.

---

## 4. Stop the schedules
{: #lab11-schedules}

**System Scheduler → Scheduled Jobs** → confirm the **parent** AWS import job is **inactive** so the connector’s **scheduled chain** does not keep firing against AWS after keys and stacks are gone.

**Active = false** on a connection record is **insufficient** proof schedules stopped.

### Parent job vs child jobs (observed pattern)

Service Graph AWS jobs are often wired **After Parent Runs** to a parent such as **`SG-AWS-Organization`**. On the observed instance:

- **Parent `SG-AWS-Organization`:** **Inactive** — this is the **verified** scheduling check for stopping **automatic** AWS import runs.
- **24 remaining `SG-AWS-*` child jobs:** still **Active = true**, **Run** = **After Parent Runs**, **Parent** = **`SG-AWS-Organization`**.

With the **parent inactive**, the **scheduled chain is stopped** even though children still display **Active**. A child can still be **executed manually** from the list (separate from the cron/parent chain). **Do not** document “all SG-AWS schedules inactive” unless you have verified each row.

![Scheduled Jobs filtered to SG-AWS — top of list showing parent and children]({{ '/assets/img/lab11/schedules-sg-aws-parents-top.png' | relative_url }})
*Filter **Name** starts with **`SG-AWS`** and **Active = true** (no “Updated This Week” filter). Top rows: parent **Organization** and children such as **EC2 instances**, **Subnets**, **VPCs** — **Run** = **After Parent Runs**.*

![Scheduled Jobs — bottom of same filtered list]({{ '/assets/img/lab11/schedules-sg-aws-parents-bottom.png' | relative_url }})
*Bottom of the same filtered view: additional **SG-AWS-*** children still **Active**, all tied to parent **`SG-AWS-Organization`**.*

### Instance security (do not bypass)

When editing some schedule fields inline, ServiceNow may show **`Security prevents writing to this field`**. **Do not** use this lab to advise ACL changes, elevated roles, or “force” edits to flip child **Active** flags. The observed cleanup path is: **revoke AWS keys**, **disable connection**, **inactivate parent schedule**, tear down **AWS** resources — not blanket-deactivate every child or bypass platform security.

### Scope: AWS only; CMDB rows are optional

| Do | Don't |
|---|---|
| Verify **`SG-AWS-Organization`** (or your parent) is **Inactive** | Blanket-deactivate every **SCCM**, **Azure**, or **Dynatrace** schedule |
| Leave non-AWS lab schedules alone unless you intend to | Delete CMDB CIs just because imports ran — rows are **learning evidence** and are **not** AWS charges |

A full **SG-name** export may still show CIs (e.g. **Storage-Volume**) with **After Parent Runs** semantics in data — that is normal after imports. **No CMDB delete is required** for AWS billing cleanup once keys, stacks, Config, and the **parent** schedule are handled.

---

## 5. Confirm the bill
{: #lab11-billing}

- AWS **Billing → Cost Explorer**, group by service — use an **unfiltered** month-to-date view when checking whether lab services still show lines (filters can mislead)
- **Budgets** — alarm warns; it is **not** a spend cap
- After Config teardown: confirm **Config** and **S3** lines trend down (lag is normal)
- **Credits & invoices:** remaining promotional credits and **estimated** usage can update on a **~24 hour** delay; the **invoice** finalizes totals. A **$0.00** Cost Explorer snapshot is **not** a universal guarantee of free usage forever or on every account type
- Azure **Cost Management** if you ran Lab 8

**Stopped EC2 is not free** — **Elastic Block Store (EBS)** and related charges can continue.

**Observed snapshot (one Free-plan account):** unfiltered **November** month-to-date Cost Explorer grouped by service showed **$0.00** total and **0** services, with **~140** credits remaining against **400** total (estimated consumption split across base, budget, and EC2 launch rewards). Your numbers will differ.

---

## Checkpoint
{: #lab11-checkpoint}

<ul class="check">
<li><b>Observed:</b> keys <b>0</b>; three stacks <b>DELETE_COMPLETE</b>; Config <b>off</b>; retained Config bucket <b>emptied/deleted</b>; Ohio volumes/snapshots/EIPs <b>0</b>; lab instance <b>Terminated</b></li>
<li><b>Verified:</b> parent <code>SG-AWS-Organization</code> <b>Inactive</b> (scheduled chain stopped); <b>child</b> jobs may still show <b>Active</b></li>
<li><b>Optional / ongoing:</b> delete IAM user; manual schedule runs still possible; CMDB rows kept for learning; billing estimate lag</li>
<li>You can explain <b>targeted cleanup</b> vs closing a shared account (Objective)</li>
<li>You can explain Config <b>recording</b> vs traffic capture (ELI5 above)</li>
<li>Lab user is <b>programmatic connector</b> identity — not human console login ([Lab 3]({{ '/labs/03-iam-connection/' | relative_url }}#lab3-iam-programmatic))</li>
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
