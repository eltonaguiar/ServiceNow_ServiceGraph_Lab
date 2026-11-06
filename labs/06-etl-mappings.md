---
layout: default
title: Change an ETL mapping
lab: 6
time: 30 min
level: Data
order: 6
permalink: /labs/06-etl-mappings/
---

## Objective

Take control of what AWS data becomes. Inspect the connector's IntegrationHub ETL mapping,
add one field end to end, and see it land on the CI.

## 1. Open the mapping

**Process Automation → Flow Designer → IntegrationHub → ETL** (older releases:
**IntegrationHub → ETL Definitions**), or from the connector's Guided Setup there is usually a
**Configure ETL mappings** link.

Select the AWS hardware/EC2 definition. You will see a three-stage pipeline:

| Stage | What it does |
|---|---|
| **Extract / Data source** | The REST step that calls AWS and returns JSON |
| **Transform** | Field-level mappings: AWS JSON path → ServiceNow CI field, with transforms |
| **Load** | The IRE call that submits the transformed records |

## 2. Read one field end to end

Pick `name` on `cmdb_ci_ec2_instance` and follow it backwards:

1. Find the target field in the Transform stage.
2. Note the **source path** (something under `Reservations[].Instances[]`, e.g. `InstanceId`
   or a `Tags` entry).
3. Note any transform applied (concatenation, lookup, script).

Then do the same for a tag-derived field. Tags are the usual source of `Environment` and
`Owner`, and they are why Lab 1 insisted on them.

## 3. Add a field

Goal: surface the AWS **instance type** (`t3.micro`) on the CI, using a field your class
already has (or a string attribute you add in CI Class Manager).

1. In the Transform stage, add a mapping: source `InstanceType` → target field (for example
   `model_id` or a custom `u_instance_type` string).
2. Save, then **Execute Now** the hardware schedule again.
3. Confirm on the CI record that the value appears.

If nothing lands, the transform referenced a path that the payload does not contain. Check the
**import set row → payload** to see the JSON the REST step actually returned; paths in
documentation are often one array level off from reality.

## 4. Break it on purpose

1. Point the `name` mapping at a field that does not exist (e.g. `DoesNotExist`).
2. Re-run. Rows still import, but the CI's name falls back to the identifier.
3. Revert the mapping and re-run to restore.

This is the fastest way to learn the difference between "the connector failed" (no rows) and
"the mapping is wrong" (rows with empty fields).

## Checkpoint

<ul class="check">
<li>You can point at the exact JSON path that fills the CI name</li>
<li>You added and verified one new mapped field</li>
<li>You know where to look up the raw payload for a failed mapping</li>
</ul>

Next: [Lab 7 — CSDM and the service graph]({{ '/labs/07-csdm-graph/' | relative_url }})
