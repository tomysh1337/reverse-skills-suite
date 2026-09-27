#!/usr/bin/env python3
"""Static feature checker for Android native/JNI/VMP/ZKM protection signals.

The checker is deliberately evidence based: it reports strings/symbols found in
the supplied APK or unpacked tree and never treats a match as proof of a
particular commercial protector.  It emits JSON for automation and Markdown
for review.  It uses only the Python standard library.

Examples:
    python native_feature_checker.py NP.apk --out reports/native-feature-check
    python native_feature_checker.py unpacked-apk --out reports/native-feature-check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterable, Iterator


MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_EVIDENCE_PER_RULE = 24
MAX_CONTEXT = 96


@dataclass(frozen=True)
class Rule:
    category: str
    name: str
    pattern: str
    description: str
    confidence: str = "medium"
    flags: int = re.IGNORECASE


RULES: tuple[Rule, ...] = (
    Rule("jni", "jni_onload", r"JNI_OnLoad", "JNI library initialization entrypoint", "high"),
    Rule("jni", "register_natives", r"RegisterNatives|JNINativeMethod", "dynamic JNI registration symbols", "high"),
    Rule("jni", "exported_java_binding", r"Java_[A-Za-z0-9_]+", "statically exported Java_* JNI binding", "high"),
    Rule("jni", "java_native_decl", r"\bnative\s+(?:public|private|protected|static|final|synchronized|abstract|\w+\s+)*\w+\s*\(", "Java native method declaration", "medium"),
    Rule("jni", "load_library", r"System\.(?:loadLibrary|load)\s*\(|\bloadLibrary\b", "Java native library loading", "high"),
    Rule("jni", "jni_env_api", r"GetMethodID|GetStaticMethodID|FindClass|GetFieldID|NewStringUTF", "JNI environment API usage", "medium"),
    Rule("dynamic_loading", "dlopen", r"\bdlopen\b|android_dlopen_ext", "runtime native module loading", "high"),
    Rule("dynamic_loading", "dlsym", r"\bdlsym\b|dladdr|dlclose", "runtime symbol lookup", "high"),
    Rule("dynamic_loading", "dex_loading", r"DexClassLoader|PathClassLoader|InMemoryDexClassLoader|BaseDexClassLoader", "runtime DEX/class loader", "high"),
    Rule("dynamic_loading", "embedded_payload", r"classes\d*\.dex|main\.jar|assets/.+\.(?:dex|jar|bin|dat)|assets\\.+\\(?:dex|jar|bin|dat)", "embedded DEX or payload artifact", "medium"),
    Rule("vmp", "vmp_library", r"libnpvmp\.so|libvmp\.so|vmprotect|vm_interpret|vmInterpret|virtualiz(?:e|ation)", "virtualized native/VM protector indicator", "high"),
    Rule("vmp", "vm_dispatch", r"vm[_ -]?(?:interpret(?:er|ation)?|dispatch(?:er)?|entry)|bytecode|opcode|handler[_ -]?table", "VM interpreter/dispatcher vocabulary", "medium"),
    Rule("vmp", "apk_vm_marker", r"Apk[-_ ]?VM|ApkControlFlowConfusion|VMP|VMProtect", "protector marker", "high"),
    Rule("vmp", "protected_init", r"classes(?:Init)?[0-9]+|classesInit[0-9]+", "protected DEX initialization family", "high"),
    Rule("zkm", "zkm_marker", r"(?:^|[^A-Za-z])ZKM(?:[^A-Za-z]|$)|Zelix|zelix\.klassmaster|KlassMaster", "ZKM/Zelix protector marker", "high", flags=0),
    Rule("zkm", "zkm_string", r"ZKMString|ZKMClass|ZKMMethod|ZKMNative", "ZKM generated symbol/string", "high", flags=0),
    Rule("string_obfuscation", "xor_string", r"\b(?:xor|XOR)\b|char\s*\[\]|StringBuilder|decryptString|decodeString", "possible XOR/string-pool decoding", "low"),
    Rule("string_obfuscation", "string_pool", r"string[_ ]?pool|f\d{4,}(?:short|String)?|decrypt(?:ed)?[_ ]?string", "string pool/decryption naming", "medium"),
    Rule("control_flow", "flattening_marker", r"control.?flow.?confusion|control.?flow.?flatten|flatten(?:ing|ed)?|opaque.?predicate|bogus.?control", "control-flow flattening/opaque predicate marker", "high"),
    Rule("control_flow", "ollvm_marker", r"OLLVM|obfuscator-llvm|splitbasicblock|substitution|bogus[_ -]?control", "compiler obfuscation marker", "medium"),
    Rule("anti_debug", "proc_status", r"/proc/(?:%d/)?status|/proc/self/status|TracerPid", "debugger status probe", "high"),
    Rule("anti_debug", "proc_maps", r"/proc/self/maps|/proc/\d+/maps|\bmaps\b", "loaded-module/maps probe", "medium"),
    Rule("anti_debug", "proc_system", r"/proc/meminfo|/proc/version|/proc/cpuinfo", "environment/virtualization probe", "medium"),
    Rule("anti_debug", "ptrace", r"\bptrace\b|PTRACE_TRACEME|Debug\.isDebuggerConnected|isDebuggerConnected", "debugger/trace detection", "high"),
    Rule("anti_debug", "instrumentation", r"\b(?:frida|gdb|lldb|xposed|substrate|magisk|zygisk)\b", "instrumentation/root framework probe", "medium"),
    Rule("memory_protection", "mprotect", r"\bmprotect\b|PROT_EXEC|PROT_WRITE", "runtime executable-memory permission change", "high"),
    Rule("memory_protection", "executable_mapping", r"\bmmap\b|memfd_create|cacheflush|__clear_cache", "runtime code mapping/cache maintenance", "medium"),
)


COMPILED = tuple((rule, re.compile(rule.pattern.encode("ascii", "ignore"), rule.flags)) for rule in RULES)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iter_ascii_strings(data: bytes) -> Iterator[tuple[int, bytes]]:
    """Yield printable ASCII runs and their byte offsets."""
    for match in re.finditer(rb"[\x20-\x7e]{4,}", data):
        yield match.start(), match.group()


def file_kind(name: str) -> str:
    lower = name.lower()
    if lower.endswith(".so") or "/lib/" in lower or "\\lib\\" in lower:
        return "elf/native"
    if lower.endswith((".dex", ".vdex", ".odex")):
        return "dex"
    if lower.endswith((".java", ".kt", ".smali", ".xml", ".json", ".txt")):
        return "source/resource"
    if lower.endswith((".jar", ".zip", ".apk")):
        return "archive"
    return "binary/resource"


def iter_sources(root: Path) -> Iterator[tuple[str, bytes]]:
    """Yield logical path and bytes from an APK or unpacked directory."""
    if root.is_file() and zipfile.is_zipfile(root):
        with zipfile.ZipFile(root) as archive:
            for info in archive.infolist():
                if info.is_dir() or info.file_size > MAX_FILE_BYTES:
                    continue
                try:
                    yield info.filename, archive.read(info)
                except (OSError, RuntimeError, zipfile.BadZipFile):
                    continue
        return
    if root.is_file():
        try:
            yield root.name, root.read_bytes()[:MAX_FILE_BYTES]
        except OSError:
            return
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            yield path.relative_to(root).as_posix(), path.read_bytes()
        except OSError:
            continue


def decode_context(blob: bytes, start: int, end: int) -> str:
    left = max(0, start - MAX_CONTEXT // 2)
    right = min(len(blob), end + MAX_CONTEXT // 2)
    text = blob[left:right].decode("utf-8", "replace")
    return re.sub(r"\s+", " ", text).strip()[:MAX_CONTEXT]


def scan_source(name: str, data: bytes) -> tuple[list[dict], dict[str, int]]:
    evidence: list[dict] = []
    counts: dict[str, int] = {}
    # Matching every rule over a multi-megabyte ELF is needlessly expensive.
    # ELF/DEX symbols and source literals are both represented by printable
    # runs, so match those runs while retaining the run's original file offset.
    # This also avoids treating arbitrary binary bytes as textual evidence.
    strings = list(iter_ascii_strings(data))
    for rule, regex in COMPILED:
        rule_matches: list[tuple[int, re.Match[bytes]]] = []
        for run_offset, run in strings:
            for match in regex.finditer(run):
                rule_matches.append((run_offset, match))
                if len(rule_matches) >= MAX_EVIDENCE_PER_RULE:
                    break
            if len(rule_matches) >= MAX_EVIDENCE_PER_RULE:
                break
        if not rule_matches:
            continue
        counts[rule.name] = len(rule_matches)
        for run_offset, match in rule_matches:
            start = run_offset + match.start()
            end = run_offset + match.end()
            evidence.append(
                {
                    "category": rule.category,
                    "rule": rule.name,
                    "confidence": rule.confidence,
                    "path": name,
                    "offset": start,
                    "match": match.group().decode("utf-8", "replace"),
                    "context": decode_context(data, start, end),
                    "description": rule.description,
                }
            )
    return evidence, counts


def classify_score(categories: dict[str, dict]) -> tuple[str, int]:
    weights = {
        "jni": 2,
        "dynamic_loading": 2,
        "vmp": 4,
        "zkm": 4,
        "string_obfuscation": 1,
        "control_flow": 3,
        "anti_debug": 2,
        "memory_protection": 2,
    }
    score = sum(weights.get(name, 0) for name, value in categories.items() if value.get("hits", 0))
    if score >= 12:
        return "strong_protection_signals", score
    if score >= 6:
        return "multiple_protection_signals", score
    if score:
        return "isolated_signals", score
    return "no_known_signals", 0


def scan(root: Path) -> dict:
    files = 0
    total_bytes = 0
    all_evidence: list[dict] = []
    by_category: dict[str, dict] = {
        category: {"hits": 0, "files": set(), "rules": {}}
        for category in sorted({rule.category for rule in RULES})
    }
    artifact_hash = hashlib.sha256()
    artifact_hash.update(str(root.resolve()).encode("utf-8", "replace"))
    for name, data in iter_sources(root):
        files += 1
        total_bytes += len(data)
        artifact_hash.update(name.encode("utf-8", "replace"))
        artifact_hash.update(sha256_bytes(data).encode("ascii"))
        evidence, counts = scan_source(name, data)
        all_evidence.extend(evidence)
        for item in evidence:
            category = by_category[item["category"]]
            category["hits"] += 1
            category["files"].add(name)
            category["rules"][item["rule"]] = category["rules"].get(item["rule"], 0) + 1
    for category in by_category.values():
        category["files"] = sorted(category["files"])
        category["file_count"] = len(category["files"])
    classification, score = classify_score(by_category)
    return {
        "schema": "native-feature-check/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(root),
        "input_type": "apk" if root.is_file() and zipfile.is_zipfile(root) else ("file" if root.is_file() else "directory"),
        "inventory": {"files_scanned": files, "bytes_scanned": total_bytes, "scan_id": artifact_hash.hexdigest()},
        "classification": classification,
        "score": score,
        "categories": by_category,
        "evidence": all_evidence,
        "limitations": [
            "Matches are static indicators, not proof of a commercial protector.",
            "Packed/encrypted payloads and runtime RegisterNatives tables require runtime capture.",
            "Absence of a string does not prove absence of a feature.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# Native/JNI/VMP/ZKM Feature Check",
        "",
        f"- Input: `{report['input']}`",
        f"- Type: `{report['input_type']}`",
        f"- Files scanned: `{report['inventory']['files_scanned']}`",
        f"- Bytes scanned: `{report['inventory']['bytes_scanned']}`",
        f"- Classification: **{report['classification']}** (score `{report['score']}`)",
        "",
        "## Category Summary",
        "",
        "| Category | Hits | Files | Rules |",
        "|---|---:|---:|---|",
    ]
    for category, value in report["categories"].items():
        rules = ", ".join(f"`{k}` ({v})" for k, v in sorted(value["rules"].items())) or "-"
        lines.append(f"| `{category}` | {value['hits']} | {value['file_count']} | {rules} |")
    lines += ["", "## Evidence", "", "| Category | Rule | Confidence | File | Offset | Match |", "|---|---|---|---|---:|---|"]
    for item in report["evidence"]:
        match = item["match"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{item['category']}` | `{item['rule']}` | {item['confidence']} | `{item['path']}` | {item['offset']} | `{match}` |")
    lines += ["", "## Interpretation", "", "Static evidence indicates mechanisms worth inspecting in a disassembler or runtime trace. It does not by itself recover protected function semantics.", ""]
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="APK, native file, or unpacked APK directory")
    parser.add_argument("--out", type=Path, default=None, help="output basename or directory")
    args = parser.parse_args(argv)
    if not args.input.exists():
        parser.error(f"input does not exist: {args.input}")
    report = scan(args.input)
    out = args.out or args.input.with_suffix("")
    # Treat an extension as a basename; otherwise create a directory.
    if out.suffix.lower() in {".json", ".md"}:
        out_dir = out.parent
        base = out.stem
    else:
        out_dir = out
        base = "native-feature-check"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{base}.json"
    md_path = out_dir / f"{base}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"Classification: {report['classification']} (score={report['score']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
