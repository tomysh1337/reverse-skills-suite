#!/usr/bin/env python3
"""Triage APK/extracted trees for JNI, VM/VMP, ZKM, loader, and anti-trace indicators."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PATTERNS = {
    "jni_dynamic": [r"JNI_OnLoad", r"RegisterNatives", r"JNINativeMethod", r"FindClass"],
    "vm_dispatch": [r"vmInterpret", r"getJNIWrapper", r"cacheInitial", r"Apk-VM"],
    "native_loader": [r"dlopen", r"dlsym", r"mprotect", r"mmap"],
    "anti_trace": [r"ptrace", r"/proc/self/maps", r"/proc/.{0,30}/status", r"TracerPid"],
    "zkm_java": [r"com\.zelix", r"ZKM", r"ControlFlowConfusion", r"not printable characters"],
    "string_protection": [r"char\[\]", r"short\[\]", r"XOR", r"decoder", r"f39903short"],
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def scan_file(path: Path) -> list[dict]:
    if path.stat().st_size > 32 * 1024 * 1024:
        return []
    try:
        data = path.read_bytes()
        text = data.decode("utf-8", "ignore")
    except OSError:
        return []
    hits = []
    for family, expressions in PATTERNS.items():
        for expression in expressions:
            match = re.search(expression, text, flags=re.IGNORECASE)
            if match:
                hits.append({"family": family, "pattern": expression, "offset": match.start()})
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", type=Path, default=Path("feature-scan.json"))
    parser.add_argument("--markdown", type=Path, default=Path("feature-scan.md"))
    args = parser.parse_args()
    root = args.input.resolve()
    files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
    records = []
    for path in files:
        hits = scan_file(path)
        if hits:
            records.append({"path": str(path), "size": path.stat().st_size, "sha256": digest(path), "hits": hits})
    families = {family: sum(1 for row in records if any(h["family"] == family for h in row["hits"])) for family in PATTERNS}
    result = {"input": str(root), "files_scanned": len(files), "files_with_hits": len(records), "families": families, "files": records}
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Feature scan", "", f"- input: `{root}`", f"- files scanned: {len(files)}", f"- files with hits: {len(records)}", "", "## Families", ""]
    lines.extend(f"- `{family}`: {count}" for family, count in families.items())
    lines += ["", "## Evidence", ""]
    for row in records:
        for hit in row["hits"]:
            lines.append(f"- `{row['path']}` `{hit['family']}` `{hit['pattern']}` offset={hit['offset']}")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"files_scanned": len(files), "files_with_hits": len(records), "families": families}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
