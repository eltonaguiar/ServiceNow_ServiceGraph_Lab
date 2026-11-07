---
layout: default
title: Prerequisites
lab: 0
time: 15 min
level: Setup
order: 0
permalink: /labs/00-prerequisites/
---

<div class="eli5">
<span class="label">ELI5</span>
<p>You need a ServiceNow PDI, an AWS account, and a budget alarm so spend shows up in email — the alarm warns; it does not stop charges.</p>
</div>

<div style="border: 2px solid #d73a49; border-radius: 6px; padding: 12px 16px; margin: 16px 0; background: #fff5f5; color: #24292e;">
<p style="margin: 0; font-weight: bold; color: #cb2431;">⚠️ AWS plan check — conserve credits and avoid unintended upgrades</p>
<p style="margin: 8px 0 0 0; color: #24292e;">Confirm the <strong>current plan</strong> for the <strong>Amazon Web Services (AWS)</strong> account you are using. A genuine <strong>Free plan</strong> does <strong>not</strong> automatically become <strong>Paid</strong> merely because credits run out or six months pass; access ends instead. Small scope and prompt cleanup preserve credits, but <strong>cannot</strong> extend the six‑month cap. Creating or joining <strong>AWS Organizations</strong> or setting up an <strong>AWS Control Tower</strong> landing zone can trigger a paid upgrade — neither is needed for this lab. <strong>Paid</strong>, legacy, and optional <strong>Microsoft Azure</strong> (Lab 8) accounts have different billing rules. Set budget <strong>alerts</strong> (they warn; they do not cap spend) and follow [Lab 11]({{ '/labs/11-cleanup/' | relative_url }}) cleanup. Read §2 below for official sources and the full explanation.</p>
</div>

## Objective

Have a working PDI, a live AWS account with a budget alarm, and verification access to
both — before you touch any connector.

## 1. Personal Developer Instance (PDI)

1. Sign in at [developer.servicenow.com](https://developer.servicenow.com) → **Request Instance**.
2. Wait for the **Ready** state, then note the instance URL (`https://devNNNNNN.service-now.com`)
   and the **admin** password. Copy both into a scratch note.
3. Log in and confirm you hold `admin`.

> PDIs hibernate after a period of inactivity and the URL can change when they wake.
> If you get an XML "instance not found" page, wake the instance first — it is not a
> connector problem.

### If the PDI hibernates in the middle of the lab

This will happen, usually right after Lab 3. It is not a connector fault, and you do not need
to start over:

1. Go to [developer.servicenow.com](https://developer.servicenow.com) → **Manage instance** →
   **Wake**. Wait for **Ready**.
2. **Compare the URL with the one in your notes.** It often changes. If it did, every
   `SN_INSTANCE` value in your shells and scripts is now wrong.
3. Re-login with the same `admin` password.
4. Re-run the connection **Test** from Lab 3 before trusting any import. Credentials records
   and connection aliases can be invalidated by the wake.
5. Re-run one schedule manually (Lab 4) and compare counts with the verifier — a second import
   should *update* existing CIs, not duplicate them.

> Anything you installed stays installed. What breaks is usually the outbound connection, not
the app.

## 2. Free AWS account (Amazon Web Services)

### Create the account

1. Go to [aws.amazon.com/free](https://aws.amazon.com/free) and create an account.
2. Follow the sign-up experience AWS presents. Many customers on the simplified experience do
   **not** need a payment method at signup, although AWS may request one for identity verification;
   other sign-up routes can differ. A payment method on file does **not** by itself mean a confirmed
   Free plan silently becomes Paid when credits expire — check the actual plan and any upgrade
   confirmation before continuing.
3. After signup you will see a welcome / getting-started screen. You can skip the agent-toolkit prompts for this lab — they are not required.
4. Confirm your plan in the account menu (top right). A typical new Free plan looks like this:
   - **Current plan:** Free
   - **Credits remaining:** $100.00 (you can sometimes earn up to $100 more by completing onboarding activities)
   - **Days remaining:** ~180 days (about six months)
5. **Immediately** set a budget alarm. The **Settings → Billing** page (where you see credits and days remaining) does **not** have budgets. Open the **Billing and Cost Management** console instead:
   - Direct link: [https://us-east-1.console.aws.amazon.com/cost-management](https://us-east-1.console.aws.amazon.com/cost-management) (or search for **Budgets** in the top search bar).
   - In the navigation pane choose **Budgets** → **Create budget**.
   - Choose **Use a template (simplified)**.
   - Pick **Zero spend budget** (alerts on any spend) or **Monthly cost budget** set to **$1–5** with alerts at 50%.
   - Enter your email and create the budget, then **verify the email** (check for the AWS confirmation message and click the link) or alerts will not send.
6. Choose one region and stick to it for the whole lab (for example `ca-central-1` or `us-east-1`). Multi-region imports multiply the data and the surprises.
7. Note your **12-digit account ID** (top-right account menu).

### What the Free plan actually means in 2026

Verify **Current plan**, **credits remaining**, and **plan expiry** for this specific account.
New-customer credits are not a blanket protection for Paid or **legacy 12‑month Free Tier**
accounts. AWS also introduced a simplified, project-based sign-up experience in October 2026; its
screens and feature availability differ from the advanced AWS experience.

> **Our caution is primarily about conserving credits, not an automatic paid rollover.** Keep the
> lab small so credits last for more learning sessions. The Free plan still ends after **six months
> or credit exhaustion, whichever comes first**. Saving credits does **not** extend that time limit.

When a Free plan expires, account or project access is suspended or closed. AWS retains the data for
**90 days**; recovering access requires upgrading to **Paid** during that period (not free
read-only access). Afterward, AWS can permanently delete account content and resources. Export lab
evidence before expiry rather than relying on paid recovery.

Paid upgrades are separate actions. Do **not** choose **Upgrade** for this lab, create or join
**AWS Organizations**, or set up an **AWS Control Tower** landing zone. AWS also lists Partner
Network enrollment, Professional Services contracts, Enterprise Agreements, Skill Builder Team
subscriptions, and **HIPAA** or **SEC** compliance designation as automatic-upgrade triggers. An
**IAM Identity Center** *organization-instance* workflow can create an organization and trigger
upgrade; a **standalone account instance** is a different documented option — not every Identity
Center setup does this. None of those workflows are required here.

Practical consequences:

- Limit **AWS Config** recording to the existing four lab resource types and keep one region. This
  primarily conserves credits; it is not a spend cap.
- Stopping **Elastic Compute Cloud (EC2)** stops compute usage; **Elastic Block Store (EBS)** and
  other retained resources may continue to incur metered costs. Check which resources remain rather
  than assuming every public **Internet Protocol (IP)** charge behaves the same when an instance is
  stopped (see cost tables below — not re-verified in this pass).
- Credits cover eligible charges only. Paid accounts can be billed for uncovered usage even with
  credits remaining. Check credit applicability and each expiry in the console; current AWS pages
  **disagree** on post-upgrade credit validity — do not assume one universal rule.
- Keep budget alerts and inspect the actual balance and days remaining. Alerts are not a spending
  cap; do not confuse them with the simplified experience’s separate project spend-limit feature.
- These AWS rules do **not** describe Azure. Keep optional Azure trial and cleanup guidance
  separate (§3).

Official sources: [Choosing a plan](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html),
[Free Tier terms](https://aws.amazon.com/free/terms/),
[current FAQs](https://aws.amazon.com/free/free-tier-faqs/),
[new-experience upgrades](https://docs.aws.amazon.com/accounts/latest/reference/upgrade-account.html),
[Identity Center setup](https://docs.aws.amazon.com/singlesignon/latest/userguide/get-set-up-for-idc.html),
[Promotional credit exclusions](https://aws.amazon.com/awscredits/). Checked November 2026.

<details>
<summary><strong>How much does it actually cost? (AWS vs Azure)</strong></summary>

<p>Approximate on-demand rates in a cheap US region (late 2026) for one small lab VM.</p>

<table>
<thead>
<tr><th>Item</th><th>AWS (t3.micro)</th><th>Azure (B1s)</th></tr>
</thead>
<tbody>
<tr><td>VM compute</td><td>~$0.0104/hour</td><td>~$0.0104/hour</td></tr>
<tr><td>Public IPv4</td><td>$0.005/hour (even if stopped)</td><td>~$0.004–0.005/hour</td></tr>
<tr><td>Small disk</td><td>a few cents</td><td>a few cents</td></tr>
<tr><td>New-account free tier</td><td>$100–$200 credits (6 months)</td><td>$200 credit (30 days) + 750 free B1s hours/month for 12 months</td></tr>
</tbody>
</table>

<p><strong>Example costs for one lab VM</strong></p>

<table>
<thead>
<tr><th>Duration</th><th>Running</th><th>Stopped / deallocated (IP + disk kept)</th></tr>
</thead>
<tbody>
<tr><td>8 hours</td><td>~$0.12</td><td>~$0.04</td></tr>
<tr><td>2 days</td><td>~$0.75–$1.00</td><td>~$0.25–$0.40</td></tr>
<tr><td>1 month</td><td>~$11–12</td><td>~$4</td></tr>
</tbody>
</table>

<ul>
<li>On AWS, a public IPv4 keeps charging after you stop the instance.</li>
<li>On Azure, you must <strong>deallocate</strong> the VM (not just shut down inside the OS) to stop compute charges. Static IPs and managed disks still cost money.</li>
<li>These amounts are usually covered by free-tier credits on a new account. The risk is forgetting resources for weeks.</li>
</ul>

</details>

So the rule for this lab is not "it is free, leave it" but:

> **Create → verify → stop the instance → delete the stack the same day.** Treat "I will clean
> up later" as the failure mode. Lab 11 is designed to take four minutes, not to be a chore you
> postpone.

Budget alerts are one warning mechanism, not a spend cap. Also inspect the plan’s credit balance,
expiry date and AWS notices. These cautions preserve credits on a Free plan and help avoid
out-of-pocket charges on Paid or legacy accounts; they do **not** imply automatic paid rollover when
a Free plan ends.

## 3. Free Azure account (optional — Lab 8 only)

1. Create the account at [azure.microsoft.com/free](https://azure.microsoft.com/free).
2. Set a **Cost alert** in Cost Management → Budgets ($1–5).
3. Do not upgrade to pay-as-you-go for this lab.

You can complete Labs 0–7 and 9–11 without Azure.

## 4. Get the lab files

Some labs use files from the repo (the CloudFormation template in Lab 1, the verifier and the
fallback import script in Labs 4 and 12). The site is documentation only — **it does not ship
the scripts**. Pick one:

```bash
git clone https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab.git
cd ServiceNow_ServiceGraph_Lab
python3 -m pip install boto3 requests   # only needed for Labs 4 and 12
```

<details>
<summary><strong>Debugging: <code>error: externally-managed-environment</code> (PEP 668)</strong></summary>

<div class="eli5">
<span class="label">ELI5</span>
<p>Your computer’s main Python is locked on purpose so casual installs can’t break system tools. We make a private little Python just for this lab, turn it on when we need it, and install the packages there instead of fighting the lock.</p>
</div>

<p><strong>What happened?</strong></p>
<p>On Ubuntu 23.04+, Debian 12+, and many other modern Linux systems (including Ubuntu 24.04 on the ASUS GX10), the system Python is <strong>externally managed</strong>. When you run <code>python3 -m pip install ...</code> you get:</p>

<pre><code>error: externally-managed-environment
× This environment is externally managed</code></pre>

<p>This is intentional (PEP 668). Ubuntu uses its own package manager (<code>apt</code>) to install and update Python packages that system tools depend on. If you install things with <code>pip</code> into the same Python, you can accidentally upgrade or replace a library that those tools need, and then something important breaks. The error is the OS protecting itself.</p>

<p><strong>Why not just force it with <code>--break-system-packages</code>?</strong></p>
<p>You can override the lock, but that is exactly what the protection is trying to stop. It works until it doesn’t — a later system update or another tool can then fail in confusing ways. For a lab that only needs a couple of packages, it is not worth the risk.</p>

<p><strong>What we do instead: a virtual environment</strong></p>
<p>A virtual environment is a private copy of Python + its own package folder that lives inside the lab directory (the <code>.venv</code> folder). It is completely separate from the system Python. Installing packages there cannot touch Ubuntu’s own Python libraries.</p>

<p>Think of it like this:</p>
<ul>
<li>System Python = the house tools that came with the building. Don’t mess with them.</li>
<li>Virtual environment = a toolbox you keep in one room of the lab. Only you use it, and only when you are working on this project.</li>
</ul>

<p><strong>What “activating” the environment actually does</strong></p>
<p>When you run <code>source .venv/bin/activate</code>, your terminal temporarily changes which <code>python3</code> and <code>pip</code> commands it finds first. Instead of the system ones, it uses the ones inside <code>.venv</code>. Your prompt also changes to show <code>(.venv)</code> so you know the switch is on.</p>
<p>Nothing is permanently changed. Close the terminal or run <code>deactivate</code> and you are back to the normal system Python. The packages stay installed in the <code>.venv</code> folder, waiting for the next time you activate it.</p>

<p><strong>Recommended fix — create and use a virtual environment:</strong></p>

<pre><code># One-time: install venv support
sudo apt update
sudo apt install -y python3-venv python3-full

# Create and activate a virtual environment in the lab folder
python3 -m venv .venv
source .venv/bin/activate

# Now the install works (packages go into .venv, not the system)
pip install boto3 requests</code></pre>

<p>Your prompt should show <code>(.venv)</code>. While it is active, <code>python3</code> and <code>pip</code> use the isolated environment.</p>

<p><strong>To use the scripts later</strong> (any new terminal):</p>

<pre><code>cd ~/mylabclone/ServiceNow_ServiceGraph_Lab   # or wherever you cloned it
source .venv/bin/activate
python3 scripts/verify_cmdb.py</code></pre>

<p>Leave the environment with <code>deactivate</code> when you are finished.</p>

<p><strong>Other options (less ideal for this lab):</strong></p>
<ul>
<li><code>pipx</code> — good for single standalone tools, but less convenient when a lab needs several packages together.</li>
<li>Force system install (not recommended): <code>python3 -m pip install --break-system-packages boto3 requests</code></li>
</ul>

<p>Prefer the <code>.venv</code> approach. It is the officially recommended way on Ubuntu/Debian, keeps the lab isolated, and avoids any chance of breaking system tools.</p>

</details>

Or download individual files from
[github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab](https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab)
(`aws/lab-stack.yaml`, `scripts/verify_cmdb.py`, `scripts/fallback_ire_import.py`).

You do not need any of these for Labs 2–3 or 5–11 — those are pure UI work.

## 5. Browser tabs to keep open

| Tab | Why |
|---|---|
| PDI **Filter Navigator** | Fast path to any table or module — in your own PDI, type in the filter box at the top of the **All** menu |
| AWS [**CloudFormation** console (Ohio, `us-east-2`)](https://us-east-2.console.aws.amazon.com/cloudformation/home?region=us-east-2) | Lab 1 stack status (or replace `us-east-2` with whatever region you chose in Lab 0) |
| AWS [**IAM** console → Users](https://console.aws.amazon.com/iam/home#/users) | Lab 3 access key (open the user → **Security credentials**) |
| PDI **All → System Applications → All Available Applications** | Lab 2 app search — open from your own PDI's **All** menu |
| AWS [**Billing → Budgets**](https://us-east-1.console.aws.amazon.com/billing/home#/budgets) | Confirm your alarm exists |

The AWS links are generic: they open in whichever AWS account you are signed in to, with no
account-specific values. The CloudFormation link uses Ohio (`us-east-2`) (or replace `us-east-2`
with whatever region you chose in Lab 0). IAM and Budgets are global. PDI links are not
given because every PDI has its own hostname — use the menu path in your own instance.

## Checkpoint

<ul class="check">
<li>PDI loads and <code>admin</code> can open the Filter Navigator</li>
<li>AWS account ID noted, region chosen, budget alarm active</li>
<li>You have not created any billable resource yet</li>
<li>You know your PDI can hibernate, and where to wake it</li>
<li>If you plan to run the scripts: the repo is cloned and <code>boto3</code> imports</li>
</ul>

## Minimum viable success for the whole lab

Keep this bar in mind, because it is easy to spend six hours polishing:

<ul class="check">
<li>At least one <code>cmdb_ci_vm_instance</code> whose <code>object_id</code> is a real AWS
<code>i-…</code> id (Service Graph EC2 schedule — not <code>cmdb_ci_ec2_instance</code>)</li>
<li>One IRE output row you can explain: inserted, updated, or skipped, and why</li>
<li>One CI linked to a service you created, not one the lab created for you</li>
<li>Nothing running in AWS at the end</li>
</ul>

Next: [Lab 1 — build a real AWS inventory]({{ '/labs/01-aws-inventory/' | relative_url }})
