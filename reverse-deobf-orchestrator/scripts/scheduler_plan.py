#!/usr/bin/env python3
"""Create a reproducible logical 20-write/80-read reverse-engineering plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


WRITE_SCOPES = [
    "artifact-hash", "manifest-dex", "java-mapping", "resource-map", "jni-table",
    "jni-arm64", "jni-arm32", "jni-x86", "jni-x86_64", "native-arm64",
    "native-arm32", "native-x86", "native-x86_64", "vm-dispatch", "vmp-handlers",
    "zkm-strings", "dynamic-trace", "evidence-merge", "verification", "final-report",
]
READ_SCOPES = [
    "permissions", "components", "dex-stats", "assets", "resources", "reflection", "loaders",
    "crypto", "network", "webview", "storage", "exports", "imports", "strings", "xref",
    "cfg", "jni-signatures", "jni-names", "jni-offsets", "jni-abi", "arm64-functions",
    "arm32-functions", "x86-functions", "x86_64-functions", "vm-entry", "vm-handlers",
    "bytecode-readers", "indirect-branches", "dispatch-tables", "mprotect", "dlopen",
    "dlsym", "proc-maps", "ptrace", "tracerpid", "art-hooks", "sandhook", "pine",
    "zkm-markers", "control-flow", "string-pools", "xor-decoders", "short-pools", "dex-load",
    "class-load", "native-assets", "main-jar", "signing", "certificates", "cleartext",
    "exported-services", "mcp-tools", "mcp-routing", "http-body", "http-headers", "json-rpc",
    "error-paths", "lifecycle", "application", "launcher", "native-hashes", "abi-diff",
    "function-counts", "ghidra", "radare2", "recaf", "enigma", "vineflower", "cfr",
    "jadx-errors", "smali-gaps", "runtime-device", "runtime-emulator", "frida", "logcat",
    "loaded-modules", "loaded-dex", "register-natives", "vm-arguments", "input-output",
]


TOOL_REQUIREMENTS = {
    "artifact-hash": ["python"], "manifest-dex": ["apktool", "jadx"],
    "java-mapping": ["jadx", "recaf", "enigma"], "resource-map": ["apktool"],
    "jni-table": ["frida", "adb"], "jni-arm64": ["ghidra", "radare2", "rizin"],
    "jni-arm32": ["ghidra", "radare2", "rizin"], "jni-x86": ["ghidra", "radare2", "rizin"],
    "jni-x86_64": ["ghidra", "radare2", "rizin"], "native-arm64": ["ghidra", "ida", "radare2"],
    "native-arm32": ["ghidra", "ida", "radare2"], "native-x86": ["ghidra", "ida", "radare2"],
    "native-x86_64": ["ghidra", "ida", "radare2"], "vm-dispatch": ["ghidra", "ida", "rizin"],
    "vmp-handlers": ["ghidra", "ida", "radare2"], "zkm-strings": ["jadx", "cfr", "vineflower"],
    "dynamic-trace": ["frida", "adb", "android-emulator"], "evidence-merge": ["python"],
    "verification": ["python", "adb"], "final-report": ["python"],
}

def requirements(scope: str) -> list[str]:
    if scope in TOOL_REQUIREMENTS:
        return TOOL_REQUIREMENTS[scope]
    if scope in {"ghidra", "radare2", "cfg", "imports", "exports", "strings", "xref", "function-counts", "native-hashes"}:
        return ["ghidra", "radare2", "rizin"]
    if scope in {"recaf", "enigma", "vineflower", "cfr", "jadx-errors", "bytecode-readers", "smali-gaps"}:
        return ["jadx", "recaf", "vineflower", "cfr"]
    if scope in {"runtime-device", "runtime-emulator", "frida", "logcat", "loaded-modules", "loaded-dex", "register-natives", "input-output"}:
        return ["frida", "adb", "android-emulator"]
    return ["python"]

def task(task_id: str, mode: str, scope: str, concurrency: int, depends_on=None) -> dict:
    tools = requirements(scope)
    return {"id": task_id, "mode": mode, "scope": scope, "status": "queued", "depends_on": depends_on or [], "actual_concurrency_cap": concurrency, "tool_requirements": tools, "evidence_target": f"reports/{scope}.json"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--analysis-root", required=True, type=Path)
    parser.add_argument("--actual-concurrency", type=int, default=4)
    parser.add_argument("--json", type=Path, default=Path("scheduler-plan.json"))
    args = parser.parse_args()
    writes = [task(f"write-{i+1:02d}", "write", scope, args.actual_concurrency, ["inventory"] if i else []) for i, scope in enumerate(WRITE_SCOPES)]
    reads = [task(f"read-{i+1:02d}", "read", scope, args.actual_concurrency, ["inventory"]) for i, scope in enumerate(READ_SCOPES)]
    plan = {"artifact": args.artifact, "analysis_root": str(args.analysis_root.resolve()), "logical_workers": 100, "write_slots": 20, "read_slots": 80, "actual_concurrency_cap": args.actual_concurrency, "queued_workers": max(0, 100 - args.actual_concurrency), "tasks": writes + reads}
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"logical_workers": 100, "write_slots": 20, "read_slots": 80, "actual_concurrency_cap": args.actual_concurrency, "tasks": len(plan["tasks"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
