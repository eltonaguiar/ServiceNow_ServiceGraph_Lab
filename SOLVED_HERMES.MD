# Investigation Report: Service Graph Connector for AWS - MISSING_DEPENDENCY

> **Correction (2026-11-08, verified against `dev296154`):** an earlier version of this file stated
> that `SG-AWS-Network-Interface` and `SG-AWS-Storage-Volume` are *not configured* on the instance.
> That is wrong. Both exist as **active** `scheduled_import_set` records; what they have not done is
> **produce any CIs**. See "Prerequisite Verification" below and `SOLVED_FREEBUFF.MD` for the full
> evidence trail. Do **not** create new scheduled imports on the old premise — that would duplicate
> orchestration over the same source keys.

## Issue
Partial imports for `cmdb_ci_nic` and `cmdb_ci_storage_volume` were reporting `MISSING_DEPENDENCY` when running the `SG-AWS-EC2` import.

## Investigation Steps

1. **Evidence Review**:
   - Confirmed `MISSING_DEPENDENCY` in `cmdb_ire_partial_payloads` for NIC `eni-04843cac6d5784192` and Volume `vol-0d78f1f1bebee052f`.
   - Observed that `SG-AWS-EC2` updates VM instances and tags but fails on NIC and Volume dependencies.
   - The stored partial payload carries only `discovery_source: SG-AWS` (plus `source_native_key`), so IRE had nothing to identify the CI with — expected for a reference-only item.

2. **Prerequisite Verification** (corrected — verified by `sys_id`, not by a name scan):
   - Per ServiceNow AWS mapping documentation, `SG-AWS-Network-Interface` and `SG-AWS-Storage-Volume` are required prerequisites for `SG-AWS-EC2`, and the connector orders them accordingly: NIC **140** → Volume **160** → EC2 **180**.
   - Query `scheduled_import_set` by name returns **both records present and active**:

     | Import | `sys_id` | active | run_type | parent | order |
     |---|---|---|---|---|---|
     | `SG-AWS-Organization` | `4bf63f53eb2c7010a24882ea7c5228f6` | **false** | daily | — | — |
     | `SG-AWS-Network-Interface` | `e2f9b7d3eb2c7010a24882ea7c5228e9` | true | parent | Organization | 140 |
     | `SG-AWS-Storage-Volume` | `e6fbff17eb2c7010a24882ea7c522835` | true | parent | Organization | 160 |
     | `SG-AWS-EC2` | `cd2b7317eb2c7010a24882ea7c5228ad` | true | parent | Organization | 180 |

   - What is actually missing is **execution**, visible in `sn_cmdb_int_util_cmdb_integration_execution` (`CEX…`) and the staging tables:

     | Import | Executions | Rows loaded into its `sn_aws_integ_sg_aws_*` staging table |
     |---|---|---|
     | `SG-AWS-Network-Interface` | 1 — `CEX0001013`, 2026-11-07 07:00:31, `complete`, errors 0 | **0** |
     | `SG-AWS-Storage-Volume` | **none, ever** (0 import sets) | **0** |
     | `SG-AWS-EC2` | 5, all `complete`, `ire_partial=6` each | 5 pages, every one containing `eni-04843cac6d5784192` and `vol-0d78f1f1bebee052f` |

   - Because the three are `run_type=parent` children of an **inactive** `SG-AWS-Organization`, they never run on a schedule, and a manual *Execute Now* on `SG-AWS-EC2` executes **only EC2** — never the 140/160 prerequisites.

3. **CMDB Verification**:
   - `cmdb_ci_nic`: **0 records** — the NIC was never created.
   - `cmdb_ci_storage_volume`: 7 records, all `discovery_source = ServiceNow` (Mid Server disks such as `C:`, `/dev/nvme0n1p1`), all with blank `object_id` — none is the AWS volume.
   - `sys_object_source` contains keys only for the CIs that *were* created (`…|VNICEndpoint|…`, `…|StorageMapping|…`, `…|BlockEndpoint|…`) and no plain `…|639051062568|us-east-2|eni-04843…` / volume key.
   - The EC2 mapping is **not** defective: its `Cloud Mgmt Network Interface 1/2` and `Storage Volume 1` entities are reference-only stubs (`source_native_key`, plus `cmdb_ci` on NIC 1). The authoritative attributes live in the prerequisite feeds' mappings, and both CI identifiers are `independent = false` (dependent), so a stub cannot create the record.

## Root Cause
The prerequisite imports are configured and enabled but **non-productive**: `SG-AWS-Network-Interface` loaded 0 rows on its single run, and `SG-AWS-Storage-Volume` has never executed. No NIC or volume CI therefore exists carrying the matching `source_native_key`, so `SG-AWS-EC2` cannot resolve its reference-only NIC/volume items and IRE parks them as partials with `MISSING_DEPENDENCY` (2 CI items + 3 relationships per run, `ire_partial=6`).

## Resolution
1. **First explain the `rows=0`** on `SG-AWS-Network-Interface` — re-run it and watch `CEX` `rows`. Leading hypothesis (unproven): the role behind connection alias `c3f0b8c453b32010c23bddeeff7b12ee` lacks `ec2:DescribeNetworkInterfaces` / `ec2:DescribeVolumes`, or the account/region scope excludes them. EC2 sees both resources, so scope is reachable.
2. **Execute in chain order**: `SG-AWS-Network-Interface` (expect `cmdb_ci_nic` to gain the eni with a real `object_id`) → `SG-AWS-Storage-Volume` (expect the volume) → `SG-AWS-EC2`.
3. **Acceptance test**: latest `SG-AWS-EC2` `CEX` shows `ire_partial = 0` for this row, the 3 `cmdb_rel_ci` warnings clear, and no new partial payload references this eni/vol.
4. **Keep it running**: either activate the `SG-AWS-Organization` chain (it also re-enables org discovery — decide explicitly) or schedule the three children in 140 → 160 → 180 order.

Do **not** create duplicate scheduled imports, change mappings/identification rules, reprocess partials or manually create CIs — none of those address the cause.
