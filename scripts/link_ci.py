#!/usr/bin/env python3
"""Relate a service instance to a discovered CI (Lab 7).

    export SN_INSTANCE=dev123456 SN_USER=admin SN_PASS=...
    python3 scripts/link_ci.py --list-types
    python3 scripts/link_ci.py --parent "payments-prod-01" --child i-0abc123 \
        --type "Hosted on::cmdb_ci_ec2_instance"
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def client() -> tuple[str, str]:
    inst = os.environ.get("SN_INSTANCE", "")
    user = os.environ.get("SN_USER", "admin")
    pwd = os.environ.get("SN_PASS", "")
    if not (inst and pwd):
        sys.exit("set SN_INSTANCE and SN_PASS")
    base = inst.rstrip("/") if inst.startswith("http") else f"https://{inst}.service-now.com"
    return base, base64.b64encode(f"{user}:{pwd}".encode()).decode()


def call(base: str, token: str, method: str, path: str, params: dict | None = None,
         body: dict | None = None):
    url = f"{base}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {method} {path}: {e.read()[:400].decode(errors='replace')}")


def find_ci(base: str, token: str, table: str, name: str) -> str | None:
    res = call(base, token, "GET", f"/api/now/table/{table}",
               {"sysparm_query": f"name={name}", "sysparm_fields": "sys_id,name",
                "sysparm_limit": "1"})
    rows = res.get("result", [])
    return rows[0]["sys_id"] if rows else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parent", help="parent CI name (e.g. the service instance name)")
    ap.add_argument("--parent-table", default="cmdb_ci_service_instance")
    ap.add_argument("--child", help="child CI name or identifier (e.g. i-0abc123)")
    ap.add_argument("--child-table", default="cmdb_ci_ec2_instance")
    ap.add_argument("--type", default="Hosted on::cmdb_ci_vm_instance",
                    help="relationship type as 'label::table'")
    ap.add_argument("--list-types", action="store_true", help="show a few relationship types")
    args = ap.parse_args()

    base, token = client()

    if args.list_types:
        res = call(base, token, "GET", "/api/now/table/cmdb_rel_type",
                   {"sysparm_fields": "name,parent_descriptor,child_descriptor",
                    "sysparm_limit": "40"})
        for row in res.get("result", []):
            print(f"{row.get('name',''):<40} parent={row.get('parent_descriptor','')} "
                  f"child={row.get('child_descriptor','')}")
        return 0

    if not (args.parent and args.child):
        ap.print_help()
        return 1

    parent_id = find_ci(base, token, args.parent_table, args.parent)
    child_id = find_ci(base, token, args.child_table, args.child)
    if not parent_id:
        sys.exit(f"parent not found: {args.parent} in {args.parent_table}")
    if not child_id:
        sys.exit(f"child not found: {args.child} in {args.child_table}")

    type_name, _, child_table = args.type.partition("::")
    res = call(base, token, "GET", "/api/now/table/cmdb_rel_type",
               {"sysparm_query": f"name={type_name}", "sysparm_fields": "sys_id,name",
                "sysparm_limit": "1"})
    rel_types = res.get("result", [])
    if not rel_types:
        sys.exit(f"relationship type not found: {type_name} (try --list-types)")

    created = call(base, token, "POST", "/api/now/table/cmdb_rel_ci", body={
        "parent": parent_id,
        "child": child_id,
        "type": rel_types[0]["sys_id"],
    })
    rel = created.get("result", {}) or {}
    rel_id = rel.get("sys_id", "?")
    print(f"created relationship {rel_id}: {args.parent} -[{type_name}]-> {args.child}"
          + (f" (child table {child_table})" if child_table else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
