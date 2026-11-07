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
<p>You need two free accounts (ServiceNow and AWS) and a way to notice if the lab starts costing money. The budget alarm is not optional — it is the whole reason the lab stays free.</p>
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

1. Create the account at [aws.amazon.com/free](https://aws.amazon.com/free). A card is
   required for identity verification.
2. **Immediately** set a budget alarm: **Billing and Cost Management → Budgets → Create budget
   → Zero-spend budget** or a fixed **$1–5** monthly budget with an email alert at 50 %.
3. Choose one region and stick to it for the whole lab (for example `ca-central-1`).
   Multi-region imports multiply the data and the surprises.
4. Note your **12-digit account ID** (top-right account menu).

### What "free tier" actually means in 2026

Accounts created after mid-2025 are on a **credit-based Free plan**, not the old twelve-month
allowance. The practical consequences:

- You start with a credit balance. The plan **ends when the credits run out or after about six
  months**, whichever comes first. After that, resources are stopped/billed depending on your
  choice at signup.
- A public **IPv4 address is billed per hour** on most account types. Networking is where the
  surprise charges come from, not the instance.
- `t3.micro`/`t2.micro` is only "free" inside a monthly hour allowance and only in a new
  account. An instance left running past the allowance bills normally.

So the rule for this lab is not "it is free, leave it" but:

> **Create → verify → stop the instance → delete the stack the same day.** Treat "I will clean
> up later" as the failure mode. Lab 11 is designed to take four minutes, not to be a chore you
> postpone.

The budget alarm is your only early warning, which is why it is step 2 and not an afterthought.

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
| PDI **Filter Navigator** | Fast path to any table or module |
| AWS **CloudFormation** console | Lab 1 stack status |
| AWS **IAM** console | Lab 3 access key |
| PDI **All → System Applications → All Available Applications** | Lab 2 app search |
| AWS **Billing → Budgets** | Confirm your alarm exists |

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
<li>At least one <code>cmdb_ci_ec2_instance</code> whose <code>object_id</code> is a real AWS
<code>i-…</code> id and whose <code>discovery_source</code> is the AWS connector</li>
<li>One IRE output row you can explain: inserted, updated, or skipped, and why</li>
<li>One CI linked to a service you created, not one the lab created for you</li>
<li>Nothing running in AWS at the end</li>
</ul>

Next: [Lab 1 — build a real AWS inventory]({{ '/labs/01-aws-inventory/' | relative_url }})
