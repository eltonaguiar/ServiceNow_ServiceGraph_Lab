# ServiceNow Service Graph Lab

An end-to-end, free lab: take a **free-tier AWS account** and get its real EC2 instances,
VPCs and account metadata into a **ServiceNow Personal Developer Instance** CMDB via the
**Service Graph Connector for AWS**, reconciled by IRE, joined to a CSDM service, then
extended with Azure to demonstrate a multisource CMDB.

**Live site:** https://eltonaguiar.github.io/ServiceNow_ServiceGraph_Lab/

## Why this lab exists

Most "ServiceNow CMDB" tutorials start with a CSV and end with a table full of records nobody
trusts. This one starts with a real cloud account, uses the product's own connector, and spends
its time on the part that actually decides whether a CMDB is usable:

- **IRE** — why a record was inserted, updated or rejected
- **ETL mappings** — how AWS JSON becomes CMDB fields
- **Reconciliation** — which source wins when AWS and Azure disagree
- **Drift** — what happens to the CMDB when the cloud changes

## Contents

| Path | What it is |
|---|---|
| `index.md` | Lab overview / landing page |
| `labs/00`…`11` | The lab sequence (prerequisites → cleanup) |
| `labs/fallback-ire-api.md` | Path for PDIs that cannot install the Store app |
| `aws/lab-stack.yaml` | CloudFormation: VPC, subnet, SG, one tagged EC2 instance |
| `aws/iam-readonly-lab-policy.json` | Narrow read-only policy for the connector |
| `scripts/verify_cmdb.py` | Counts CIs, IRE outcomes and staleness over REST |
| `scripts/fallback_ire_import.py` | boto3 → `/api/now/identifyreconcile` |
| `scripts/link_ci.py` | Creates the service-instance → EC2 relationship |
| `.github/workflows/pages.yml` | Builds and deploys the site to GitHub Pages |

## Run it

```bash
git clone https://github.com/eltonaguiar/ServiceNow_ServiceGraph_Lab
cd ServiceNow_ServiceGraph_Lab
pip install boto3 requests
# then follow the site, starting at Lab 0
```

Site is built by GitHub Actions on every push to `main` (Jekyll → GitHub Pages).

## Cost

`$0` if you follow Lab 11. One `t3.micro` instance in a new account, stopped or deleted at the
end, stays inside the free tier. Set a budget alarm before you create anything — Lab 0 shows
where.

## Safety

Never commit AWS keys or Azure client secrets. Everything in this repo is either read-only
IAM guidance or scripts that read credentials from environment variables.
