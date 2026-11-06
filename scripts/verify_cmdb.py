#!/usr/bin/env python3
"""Check that AWS data actually landed in the CMDB.

Usage:
    export SN_INSTANCE=dev123456 SN_USER=admin SN_PASS=...
    python3 scripts/verify_cmdb.py                 # count the lab's CI tables
    python3 scripts/verify_cmdb.py --ire           # IRE outcomes, last 24h
    python3 scripts/verify_cmdb.py --stale-days 7  # CIs not rediscovered recently

Exits non-zero when the core tables are empty or (with --stale-days) stale, so it can be
dropped into cron as a crude freshness monitor.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

TABLES = [
    "cmdb_ci_cloud_service_account",
    "cmdb_ci_ec2_instance",
    "cmdb_ci_vpc",
]


def env(name: str, *fallbacks: str) -> str:
    for key in (name, *fallbacks):
        val = os.environ.get(key)
        if val:
            return val
    return ""


def client() -> tuple[str, str]:
    inst = env("SN_INSTANCE", "SERVICENOW_INSTANCE")
    user = env("SN_USER", "SERVICENOW_USER")
    pwd = env("SN_PASS", "SN_PASSWORD", "SERVICENOW_PASSWORD")
    if not (inst and user and pwd):
        sys.exit("set SN_INSTANCE, SN_USER and SN_PASS (see Lab 4)")
    if inst.startswith("http"):
        base = inst.rstrip("/")
    else:
        base = f"https://{inst}.service-now.com"
    token = base64.b64encode(f"{user}:{pwd}".encode()).decode()
    return base, token


def get(base: str, token: str, path: str, params: dict | None = None):
    url = f"{base}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} for {path}: {e.read()[:300].decode(errors='replace')}")


def count(base: str, token: str, table: str, query: str | None = None) -> int:
    params = {"sysparm_count": "true"}
    if query:
        params["sysparm_query"] = query
    data = get(base, token, f"/api/now/stats/{table}", params)
    return int(data.get("result", {}).get("stats", {}).get("count", 0))


def cmd_counts(base: str, token: str) -> int:
    print(f"{'table':<34}{'count':>8}")
    empty = []
    for table in TABLES:
        try:
            n = count(base, token, table)
        except SystemExit:
            print(f"{table:<34}{'missing':>8}")
            continue
        print(f"{table:<34}{n:>8}")
        if n == 0:
            empty.append(table)
    if empty:
        print("\nEMPTY:", ", ".join(empty))
        print("Rows may be arriving and being dropped by IRE — see Lab 5 and Lab 10.")
        return 1
    return 0


def cmd_ire(base: str, token: str) -> int:
    since = (dt.datetime.utcnow() - dt.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    data = get(base, token, "/api/now/table/cmdb_ire_output_item", {
        "sysparm_query": f"sys_created_on>={since}",
        "sysparm_fields": "outcome,status,className,data_source,sys_created_on",
        "sysparm_limit": "2000",
    })
    rows = data.get("result", [])
    if not rows:
        print("No IRE output in the last 24h. Did the import run?")
        return 1
    buckets: dict[str, int] = {}
    for row in rows:
        key = (row.get("outcome") or row.get("status") or "unknown").lower()
        buckets[key] = buckets.get(key, 0) + 1
    print(f"IRE output items, last 24h: {len(rows)}")
    for key, n in sorted(buckets.items(), key=lambda kv: -kv[1]):
        print(f"  {key:<16}{n:>6}")
    return 0


def cmd_stale(base: str, token: str, days: int) -> int:
    cutoff = (dt.datetime.utcnow() - dt.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    total = count(base, token, "cmdb_ci_ec2_instance")
    stale = count(base, token, "cmdb_ci_ec2_instance", f"last_discovered<{cutoff}")
    print(f"cmdb_ci_ec2_instance: {total} total, {stale} not rediscovered in {days}d")
    if total and stale == total:
        print("Every EC2 CI is stale — the connector is probably not running.")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ire", action="store_true", help="show IRE outcomes for the last 24h")
    ap.add_argument("--stale-days", type=int, metavar="N",
                    help="fail if all EC2 CIs are older than N days")
    args = ap.parse_args()
    base, token = client()
    if args.ire:
        return cmd_ire(base, token)
    if args.stale_days:
        return cmd_stale(base, token, args.stale_days)
    return cmd_counts(base, token)


if __name__ == "__main__":
    sys.exit(main())
