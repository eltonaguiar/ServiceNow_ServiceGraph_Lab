# Investigation Report: Service Graph Connector for AWS - MISSING_DEPENDENCY

## Issue
Partial imports for `cmdb_ci_nic` and `cmdb_ci_storage_volume` were reporting `MISSING_DEPENDENCY` when running the `SG-AWS-EC2` import.

## Investigation Steps
1. **Evidence Review**: 
   - Confirmed `MISSING_DEPENDENCY` in `cmdb_ire_partial_payloads` for NIC `eni-04843cac6d5784192` and Volume `vol-0d78f1f1bebee052f`.
   - Observed that `SG-AWS-EC2` updates VM instances and tags but fails on NIC and Volume dependencies.

2. **Prerequisite Verification**:
   - According to ServiceNow AWS mapping documentation, `SG-AWS-Network-Interface` and `SG-AWS-Storage-Volume` are required prerequisites for `SG-AWS-EC2`.
   - Queried the `scheduled_import_set` table for all imports containing 'SG-AWS'.
   - **Finding**: Neither `SG-AWS-Network-Interface` nor `SG-AWS-Storage-Volume` are configured as scheduled imports on the instance.

3. **CMDB Verification**:
   - Queried `cmdb_ci_nic` for `eni-04843cac6d5784192`. Result: **No record found**.
   - Queried `cmdb_ci_storage_volume` for `vol-0d78f1f1bebee052f`. Result: **No record found**.

## Root Cause
The prerequisite scheduled imports responsible for creating Network Interfaces and Storage Volumes are missing from the instance. Because these CIs are not created first, the `SG-AWS-EC2` import cannot resolve the dependencies during its IRE process, leading to partial payloads and `MISSING_DEPENDENCY` errors.

## Resolution
Configure and execute the `SG-AWS-Network-Interface` and `SG-AWS-Storage-Volume` scheduled imports before running the `SG-AWS-EC2` import.
