#!/usr/bin/env python3
"""Fail-closed cross-language completion gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("tool-inventory.json", "artifact.json", "metadata-audit.json", "runtime-replay.json", "build-verification.json", "residuals.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", type=Path)
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    failures = [f"missing:{name}" for name in REQUIRED if not (args.reports / name).is_file()]
    status = {}
    if args.status.is_file():
        try:
            status = json.loads(args.status.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            failures.append("invalid_status")
    else:
        failures.append("missing_status")
    if status.get("status") != "FULL_DEOBF_COMPLETE":
        failures.append("status_is_not_FULL_DEOBF_COMPLETE")
    if status.get("unresolved"):
        failures.append(f"unresolved:{len(status['unresolved'])}")
    for name, key in (("metadata-audit.json", "passed"), ("runtime-replay.json", "passed"), ("build-verification.json", "passed")):
        path = args.reports / name
        if path.is_file():
            try:
                if json.loads(path.read_text(encoding="utf-8")).get(key) is not True:
                    failures.append(f"{name}:{key}_missing")
            except json.JSONDecodeError:
                failures.append(f"invalid:{name}")
    residual_path = args.reports / "residuals.json"
    if residual_path.is_file():
        try:
            residuals = json.loads(residual_path.read_text(encoding="utf-8"))
            if residuals.get("total", 1) != 0:
                failures.append(f"residuals:{residuals.get('total')}")
        except json.JSONDecodeError:
            failures.append("invalid:residuals.json")
    result = {"complete": not failures, "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
