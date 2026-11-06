#!/usr/bin/env python3
"""Fallback for PDIs that cannot install the Service Graph Connector.

Reads EC2/VPC inventory from AWS with boto3 and submits it to ServiceNow's
Identification and Reconciliation API (/api/now/identifyreconcile).

    python3 scripts/fallback_ire_import.py --dump aws_inventory.json
    python3 scripts/fallback_ire_import.py --push aws_inventory.json --dry-run
    python3 scripts/fallback_ire_import.py --push aws_inventory.json

Requires: pip install boto3   (only for --dump)
Env for --dump: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
Env for --push: SN_INSTANCE, SN_USER, SN_PASS
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

ENVIRONMENTS = {"lab": "2", "dev": "2", "test": "3", "qa": "3", "prod": "1", "production": "1"}


def tag(tags: list[dict], key: str, default: str = "") -> str:
    for t in tags or []:
        if t.get("Key") == key:
            return t.get("Value") or default
    return default


def dump_inventory(out_path: str) -> int:
    try:
        import boto3  # noqa: PLC0415
    except ImportError:
        sys.exit("pip install boto3 to use --dump (or hand-write the JSON)")

    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if not region:
        sys.exit("set AWS_REGION, e.g. ca-central-1")

    ec2 = boto3.client("ec2", region_name=region)
    account = boto3.client("sts", region_name=region).get_caller_identity()["Account"]

    items: list[dict] = [{
        "className": "cmdb_ci_cloud_service_account",
        "object_id": f"aws-{account}",
        "name": f"AWS {account}",
        "correlation_id": f"aws-{account}",
        "install_status": "1",
        "attributes": {"account_id": account, "region": region, "provider": "AWS"},
    }]
    relations: list[dict] = []
    vpcs: dict[str, str] = {}

    for vpc in ec2.describe_vpcs()["Vpcs"]:
        vpcs[vpc["VpcId"]] = tag(vpc.get("Tags", []), "Name", vpc["VpcId"])
        items.append({
            "className": "cmdb_ci_vpc",
            "object_id": vpc["VpcId"],
            "name": vpcs[vpc["VpcId"]],
            "correlation_id": vpc["VpcId"],
            "install_status": "1",
            "attributes": {"cidr_block": vpc.get("CidrBlock", ""),
                           "region": region, "account_id": account},
        })

    reservations = ec2.describe_instances()["Reservations"]
    for res in reservations:
        for inst in res.get("Instances", []):
            if inst.get("State", {}).get("Name") == "terminated":
                continue
            tags = inst.get("Tags", [])
            iid = inst["InstanceId"]
            items.append({
                "className": "cmdb_ci_ec2_instance",
                "object_id": iid,
                "name": tag(tags, "Name", iid),
                "correlation_id": iid,
                "install_status": "1",
                "environment": ENVIRONMENTS.get(tag(tags, "Environment").lower(), ""),
                "attributes": {
                    "instance_type": inst.get("InstanceType", ""),
                    "availability_zone": inst.get("Placement", {}).get("AvailabilityZone", ""),
                    "state": inst.get("State", {}).get("Name", ""),
                    "owner": tag(tags, "Owner"),
                    "application": tag(tags, "Application"),
                    "account_id": account,
                    "region": region,
                },
            })
            vpc_id = inst.get("VpcId")
            if vpc_id:
                relations.append({
                    "parent": vpc_id,
                    "child": iid,
                    "type": "Hosted on::cmdb_ci_vpc",
                })

    payload = {"items": items, "relations": relations}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    print(f"wrote {out_path}: {len(items)} items, {len(relations)} relations "
          f"(account {account}, region {region})")
    return 0


def push(payload_path: str, dry_run: bool, batch: int) -> int:
    with open(payload_path, encoding="utf-8") as fh:
        payload = json.load(fh)

    items = payload.get("items", [])
    relations = payload.get("relations", [])
    print(f"payload: {len(items)} items, {len(relations)} relations")
    if dry_run:
        print(json.dumps(payload, indent=1)[:2000])
        return 0

    inst = os.environ.get("SN_INSTANCE", "")
    user = os.environ.get("SN_USER", "admin")
    pwd = os.environ.get("SN_PASS", "")
    if not (inst and pwd):
        sys.exit("set SN_INSTANCE and SN_PASS")
    base = inst.rstrip("/") if inst.startswith("http") else f"https://{inst}.service-now.com"
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()

    for start in range(0, len(items), batch):
        chunk = {"items": items[start:start + batch],
                 "relations": relations if start == 0 else []}
        req = urllib.request.Request(
            f"{base}/api/now/identifyreconcile",
            data=json.dumps(chunk).encode(),
            headers={"Authorization": f"Basic {token}",
                     "Content-Type": "application/json",
                     "Accept": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            detail = e.read()[:600].decode(errors="replace")
            sys.exit(f"HTTP {e.code} on batch {start}: {detail}")

        result = body.get("result", {})
        print(f"batch {start//batch + 1}: "
              f"inserted {result.get('inserted', '?')} updated {result.get('updated', '?')} "
              f"skipped {result.get('skipped', '?')} errors {len(result.get('errors') or [])}")
        for err in (result.get("errors") or [])[:5]:
            print("  ", json.dumps(err)[:300])
    print("\nRun it again: a healthy second pass reports updates/skips, not inserts.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dump", metavar="FILE", help="read AWS and write the IRE payload")
    ap.add_argument("--push", metavar="FILE", help="submit a payload to /api/now/identifyreconcile")
    ap.add_argument("--dry-run", action="store_true", help="print the payload instead of posting")
    ap.add_argument("--batch", type=int, default=50, help="items per request (default 50)")
    args = ap.parse_args()
    if args.dump:
        return dump_inventory(args.dump)
    if args.push:
        return push(args.push, args.dry_run, args.batch)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
