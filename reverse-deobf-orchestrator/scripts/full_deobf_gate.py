#!/usr/bin/env python3
"""Strict evidence gate. Exits 0 only for an explicit complete report with no unresolved items."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("jni-map.csv", "native-functions.csv", "vm-handlers.csv", "feature-scan.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", type=Path)
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    failures = []
    for name in REQUIRED:
        if not (args.reports / name).is_file():
            failures.append(f"missing:{name}")
    status = {}
    if args.status.is_file():
        try:
            status = json.loads(args.status.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"invalid_status:{exc}")
    else:
        failures.append("missing_status")
    if status.get("status") != "FULL_DEOBF_COMPLETE":
        failures.append("status_is_not_FULL_DEOBF_COMPLETE")
    if status.get("unresolved"):
        failures.append(f"unresolved:{len(status['unresolved'])}")
    if status.get("dynamic_validation") is not True:
        failures.append("dynamic_validation_missing")
    result = {"complete": not failures, "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
