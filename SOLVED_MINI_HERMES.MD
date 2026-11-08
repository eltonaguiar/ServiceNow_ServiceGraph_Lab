# Findings: SG-AWS MISSING_DEPENDENCY

> **Corrected 2026-11-08.** The earlier version of this file said the prerequisite scheduled imports
> are *not configured*. They are configured and active — they just never produced data. Details and
> proof: `SOLVED_FREEBUFF.MD`.

- **Issue**: `SG-AWS-EC2` partial imports reporting `MISSING_DEPENDENCY` for NICs and Volumes (`eni-04843cac6d5784192`, `vol-0d78f1f1bebee052f`), 6 partial entries per run.

- **Cause**: the two prerequisite imports exist and are enabled, but are **non-productive**:
  - `SG-AWS-Network-Interface` (`e2f9b7d3eb2c7010a24882ea7c5228e9`, active, order 140) ran once — `CEX0001013`, 2026-11-07 07:00:31 — and loaded **0 rows**.
  - `SG-AWS-Storage-Volume` (`e6fbff17eb2c7010a24882ea7c522835`, active, order 160) has **never executed** (0 executions, 0 import sets).
  - Both are `run_type=parent` children of `SG-AWS-Organization` (`4bf63f53…`), which is **inactive**, so nothing runs on schedule and a manual EC2 run never triggers them.

- **Not the cause**: the EC2 mapping. Its NIC/volume entities are reference-only stubs (`source_native_key`, plus `cmdb_ci` on NIC 1); blank **Object ID** / **Public IP** is correct there. Attributes live in the prerequisite feeds. Both identifiers are dependent (`independent = false`).

- **Verification**:
  - `cmdb_ci_nic` = 0 records; `cmdb_ci_storage_volume` = 7 records, all `discovery_source=ServiceNow` Mid Server disks with blank `object_id`.
  - `sys_object_source` has keys only for the CIs that were created (`VNICEndpoint`, `StorageMapping`, `BlockEndpoint`) — no plain eni/volume key.
  - EC2 staging table: 5 pages, all containing both the eni and the volume — AWS data does arrive.

- **Fix**: explain the `rows=0` first (likely IAM `ec2:DescribeNetworkInterfaces`/`DescribeVolumes` for alias `c3f0b8c4…`), then run NIC → Volume → EC2 in that order and confirm `ire_partial` drops 6 → 0. Do not create duplicate schedules, edit mappings, or reprocess partials.
