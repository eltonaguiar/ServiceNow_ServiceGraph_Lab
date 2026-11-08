# Findings: SG-AWS MISSING_DEPENDENCY

- **Issue**: `SG-AWS-EC2` partial imports reporting `MISSING_DEPENDENCY` for NICs and Volumes.
- **Cause**: Prerequisite scheduled imports `SG-AWS-Network-Interface` and `SG-AWS-Storage-Volume` are not configured on the instance.
- **Verification**: 
  - Scheduled imports list does not contain the prerequisites.
  - CMDB does not contain the affected NIC/Volume records.
- **Fix**: Install/Configure the missing prerequisite scheduled imports.
