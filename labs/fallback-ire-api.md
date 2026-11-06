---
layout: default
title: Fallback — push AWS into IRE yourself
lab: 12
time: 60 min
level: Fallback
order: 12
permalink: /labs/fallback-ire-api/
---

## Objective

If the Store app will not install on your PDI (no entitlement, missing release, no
IntegrationHub), do not abandon the lab. The interesting parts — identification, IRE outcomes,
field mapping, relationships, service graph — are all still available through the **IRE REST
API**, which ships on every instance.

You end up with the same CMDB records; you just feed them yourself instead of letting the
connector do it.

## 1. Confirm the API exists

Filter Navigator → **System Web Services → REST → REST API Explorer**, search for
**`identifyreconcile`**. The endpoint is:

```
POST /api/now/identifyreconcile
```

with a body of `{"items":[...],"relations":[...]}`. No extra plugin needed.

## 2. Read AWS inventory

```bash
pip install boto3
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=ca-central-1
python3 scripts/fallback_ire_import.py --dump aws_inventory.json
```

`--dump` writes the normalized payload without touching ServiceNow, so you can inspect it.

## 3. Push it

```bash
export SN_INSTANCE=dev123456
export SN_USER=admin
export SN_PASS=...
python3 scripts/fallback_ire_import.py --push aws_inventory.json --dry-run
python3 scripts/fallback_ire_import.py --push aws_inventory.json
```

The script builds one item per EC2 instance with:

| CMDB field | Source |
|---|---|
| `className` | `cmdb_ci_ec2_instance` |
| `object_id` / `correlation_id` | the AWS instance ID (`i-…`) |
| `name` | the `Name` tag |
| `short_description` | instance type + AZ |
| `install_status` | 1 (Installed) |
| `environment` | the `Environment` tag, mapped to the choice value |
| attributes | `Owner`, `Application`, `InstanceType` |

Run it **twice**. The second run must report updates/no-change, not inserts — that is IRE
working, and it is the same checkpoint as Lab 5.

## 4. Relationships

`relations` in the same payload create the edges:

```json
{"parent": "i-0abc…", "child": "vpc-0def…", "type": "Hosted on::cmdb_ci_vpc"}
```

Or use `scripts/link_ci.py` after the CIs exist. Then continue at
[Lab 6]({{ '/labs/06-etl-mappings/' | relative_url }}) (you replace ETL mappings with the
script's field map) and [Lab 7]({{ '/labs/07-csdm-graph/' | relative_url }}) unchanged.

## What you do *not* get on this path

- Guided Setup, SGC Central monitoring, connection health
- Store-maintained mappings, software inventory via SSM
- The product's own schedules and retry behaviour

Say so plainly if you present this lab: it is the same CMDB mechanics, not the same product
experience.

## Checkpoint

<ul class="check">
<li><code>--dump</code> produced a payload you can read</li>
<li>A push created CIs whose discovery source is your integration, and a second push produced no inserts</li>
<li>You created at least one relationship via the API</li>
</ul>

Back to the [overview]({{ '/' | relative_url }}) · [Troubleshooting]({{ '/labs/10-troubleshooting/' | relative_url }})
