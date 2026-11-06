---
layout: default
title: Prerequisites
lab: 0
time: 15 min
level: Setup
order: 0
permalink: /labs/00-prerequisites/
---

## Objective

Have a working PDI, a live AWS account with a budget alarm, and verification access to
both — before you touch any connector.

## 1. Personal Developer Instance

1. Sign in at [developer.servicenow.com](https://developer.servicenow.com) → **Request Instance**.
2. Wait for the **Ready** state, then note the instance URL (`https://devNNNNNN.service-now.com`)
   and the **admin** password. Copy both into a scratch note.
3. Log in and confirm you hold `admin`.

> PDIs hibernate after a period of inactivity and the URL can change when they wake.
> If you get an XML "instance not found" page, wake the instance first — it is not a
> connector problem.

## 2. Free AWS account

1. Create the account at [aws.amazon.com/free](https://aws.amazon.com/free). A card is
   required for identity verification; you are on the **Free plan** with starter credits.
2. **Immediately** set a budget alarm: **Billing and Cost Management → Budgets → Create budget
   → Zero-spend budget** or a fixed **$1–5** monthly budget with an email alert at 50 %.
3. Choose one region and stick to it for the whole lab (for example `ca-central-1`).
   Multi-region imports multiply the data and the surprises.
4. Note your **12-digit account ID** (top-right account menu).

Free-tier reality in 2026: new accounts get starter credits that expire, plus a set of
always-free services. A `t3.micro`/`t2.micro` instance is free-tier eligible for a limited
monthly hour allowance in a new account; a public IPv4 address is **not** always free.
This lab creates one small instance and deletes it in Lab 11.

## 3. Free Azure account (optional — Lab 8 only)

1. Create the account at [azure.microsoft.com/free](https://azure.microsoft.com/free).
2. Set a **Cost alert** in Cost Management → Budgets ($1–5).
3. Do not upgrade to pay-as-you-go for this lab.

You can complete Labs 0–7 and 9–11 without Azure.

## 4. Browser tabs to keep open

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
</ul>

Next: [Lab 1 — build a real AWS inventory]({{ '/labs/01-aws-inventory/' | relative_url }})
