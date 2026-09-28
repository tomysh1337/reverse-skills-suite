#!/usr/bin/env python3
"""Route a Java, native, Python, or mixed artifact to evidence-backed stages."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    else:
        for child in sorted(path.rglob("*")):
            if child.is_file():
                digest.update(str(child.relative_to(path)).encode())
                digest.update(child.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    artifact = args.artifact.resolve()
    suffix = artifact.suffix.lower()
    name_lower = artifact.name.lower()
    kinds = []
    if suffix in {".jar", ".class", ".war", ".apk", ".aab"} or ".apk" in name_lower or ".aab" in name_lower or artifact.is_dir() and list(artifact.rglob("*.class")):
        kinds.append("java")
    if suffix in {".so", ".dll", ".dylib", ".exe"} or artifact.is_dir() and any(artifact.rglob("*.so")):
        kinds.append("cpp")
    if suffix in {".py", ".pyc", ".pyo", ".whl", ".pyz"} or artifact.is_dir() and list(artifact.rglob("*.pyc")):
        kinds.append("python")
    if not kinds:
        kinds = ["unknown"]
    steps = []
    if "java" in kinds:
        steps += [
            {"id": "java-probe", "tools": ["jar", "javap", "python"], "evidence_target": "reports/java-probe.json"},
            {"id": "java-views", "tools": ["vineflower", "cfr", "recaf"], "evidence_target": "reports/decompiler-views.json"},
            {"id": "java-transform-detect", "tools": ["java-deobfuscator", "threadtear"], "evidence_target": "reports/transform-detection.json"},
            {"id": "java-native-boundary", "tools": ["frida", "ghidra", "radare2"], "evidence_target": "reports/jni-native-map.csv"},
        ]
    if "cpp" in kinds:
        steps += [
            {"id": "native-fingerprint", "tools": ["objdump", "nm", "strings"], "evidence_target": "reports/native-fingerprint.json"},
            {"id": "native-static", "tools": ["ghidra", "ida", "radare2", "rizin"], "evidence_target": "reports/native-functions.csv"},
            {"id": "native-flow", "tools": ["capstone", "unicorn", "qemu"], "evidence_target": "reports/vm-handlers.csv"},
        ]
    if "python" in kinds:
        steps += [
            {"id": "python-version", "tools": ["python", "marshal", "dis"], "evidence_target": "reports/python-version.json"},
            {"id": "python-views", "tools": ["uncompyle6", "decompyle3", "python"], "evidence_target": "reports/python-code-objects.csv"},
            {"id": "python-runtime", "tools": ["python"], "evidence_target": "reports/python-runtime.json"},
        ]
    data = {"schema": "polyglot-deobf-plan/v1", "artifact": str(artifact), "sha256": sha256(artifact), "kinds": kinds, "steps": steps, "status": "planned", "full_deobf_claim_allowed": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"kinds": kinds, "steps": len(steps), "sha256": data["sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
