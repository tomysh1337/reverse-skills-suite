#!/usr/bin/env python3
"""Inventory required reverse-engineering tools and map them to evidence targets.

The inventory deliberately distinguishes an installed tool from a tool that needs
an existing user-selected installation.  A missing entry is never treated as a
successful substitute.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path


TOOLS = {
    "jadx": {"target": "managed-dex", "names": ["jadx/bin/jadx.bat", "jadx/bin/jadx", "jadx", "jadx.bat"]},
    "apktool": {"target": "resources-smali", "names": ["apktool.jar", "apktool", "apktool.bat"]},
    "dex2jar": {"target": "second-bytecode-view", "names": ["dex2jar/d2j-dex2jar.bat", "dex2jar/d2j-dex2jar", "d2j-dex2jar", "dex-tools"]},
    "recaf": {"target": "managed-navigation", "names": ["recaf.jar", "recaf", "recaf.bat"]},
    "enigma": {"target": "reviewed-mappings", "names": ["enigma.jar", "enigma-mcp.jar", "enigma", "enigma-mcp"]},
    "vineflower": {"target": "second-decompiler", "names": ["vineflower.jar", "vineflower*.jar", "vineflower"]},
    "cfr": {"target": "second-decompiler", "names": ["cfr.jar", "cfr*.jar", "cfr"]},
    "ghidra": {"target": "native-elf-vm", "names": ["ghidra*/support/analyzeHeadless.bat", "ghidra*/support/analyzeHeadless", "analyzeHeadless.bat", "analyzeHeadless"]},
    "ida": {"target": "native-elf-vm", "names": ["ida64.exe", "ida.exe"]},
    "radare2": {"target": "native-elf-vm", "names": ["radare2*/bin/radare2.exe", "radare2*/bin/r2.exe", "radare2.exe", "r2.exe", "radare2", "r2"]},
    "rizin": {"target": "native-elf-vm", "names": ["rizin*/bin/rizin.exe", "rizin.exe", "rz.exe", "rizin", "rz"]},
    "frida": {"target": "runtime-jni", "names": ["python/Scripts/frida.exe", "python/bin/frida.exe", "frida.exe", "frida"]},
    "adb": {"target": "runtime-jni", "names": ["platform-tools/adb.exe", "platform-tools/adb", "adb.exe", "adb"]},
    "android-emulator": {"target": "runtime-jni", "names": ["android-sdk/emulator/emulator.exe", "emulator/emulator.exe", "emulator.exe", "emulator"]},
    "mumu": {"target": "runtime-jni", "names": ["MuMuPlayer.exe", "NemuPlayer.exe"]},
    "java": {"target": "runtime-build", "names": ["java", "java.exe"]},
    "python": {"target": "orchestration", "names": ["python", "python.exe"]},
}

USER_PATH_TOOLS = {"ida", "mumu", "android-emulator", "enigma"}


def find_tool(names: list[str], project_tools: Path) -> str | None:
    for name in names:
        candidate = shutil.which(name) if "/" not in name and "*" not in name else None
        if candidate:
            return str(Path(candidate).resolve())
        direct = project_tools / Path(name)
        if direct.is_file():
            return str(direct.resolve())
        if "*" in name and "/" not in name:
            for path in project_tools.glob(name):
                if path.is_file():
                    return str(path.resolve())
        elif "/" in name:
            # Search only inside the named tool directory.  This keeps a
            # missing dex2jar lookup from traversing a multi-gigabyte Ghidra
            # distribution.
            parts = list(Path(name).parts)
            first = parts[0]
            bases = list(project_tools.glob(first)) if "*" in first else [project_tools / first]
            suffix = Path(*parts[1:])
            for base in bases:
                if not base.exists():
                    continue
                direct_suffix = base / suffix
                if direct_suffix.is_file():
                    return str(direct_suffix.resolve())
                suffix_text = str(suffix).replace("/", "\\").lower()
                for path in base.glob("**/" + suffix.name):
                    if path.is_file() and str(path).lower().endswith(suffix_text):
                        return str(path.resolve())
    return None


def version(path: str | None) -> str | None:
    if not path:
        return None
    suffix = Path(path).suffix.lower()
    name = Path(path).name.lower()
    path_match = re.search(r"(?<!\d)(\d+\.\d+(?:\.\d+)?)(?!\d)", str(path))
    if path_match and any(token in str(path).lower() for token in ("radare2", "rizin", "jadx", "ghidra")):
        return path_match.group(1)
    if suffix == ".jar":
        try:
            with zipfile.ZipFile(path) as archive:
                manifest = archive.read("META-INF/MANIFEST.MF").decode("utf-8", "replace")
            for key in ("Implementation-Version", "Bundle-Version", "Specification-Version"):
                match = re.search(rf"^{re.escape(key)}:\s*(.+)$", manifest, re.MULTILINE | re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        except (OSError, KeyError, zipfile.BadZipFile):
            pass
        match = re.search(r"(?<!\d)(\d+\.\d+(?:\.\d+)?)(?!\d)", str(path))
        return match.group(1) if match else None
    if suffix == ".bat" and name != "jadx.bat":
        return None
    if name.startswith("analyzeheadless"):
        return None
        return None
    try:
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=3)
        text = (result.stdout or result.stderr).strip().splitlines()
        first = text[0][:300] if text else None
        if first and (first.lower().startswith("error") or first.lower().startswith("traceback")):
            return None
        return first
    except (OSError, subprocess.SubprocessError):
        return None


def sha256(path: str | None) -> str | None:
    if not path or not Path(path).is_file():
        return None
    h = hashlib.sha256()
    try:
        with Path(path).open("rb") as fh:
            for block in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(block)
    except OSError:
        return None
    return h.hexdigest()


def load_install_manifest(tools_dir: Path) -> dict:
    manifest = tools_dir / "install-manifest.json"
    if not manifest.is_file():
        return {}
    try:
        return json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tools-dir", type=Path)
    parser.add_argument("--paths-json", type=Path)
    args = parser.parse_args()
    project = args.project.resolve()
    tools_dir = (args.tools_dir or project / ".reverse-tools").resolve()
    tools_dir.mkdir(parents=True, exist_ok=True)
    install_manifest = load_install_manifest(tools_dir)
    paths_file = (args.paths_json or tools_dir / "user-paths.json").resolve()
    path_overrides = {}
    if paths_file.is_file():
        try:
            path_overrides = json.loads(paths_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            path_overrides = {}
    rows = []
    for name, spec in TOOLS.items():
        override = path_overrides.get(name) if isinstance(path_overrides, dict) else None
        path = str(Path(override).resolve()) if override and Path(override).is_file() else find_tool(spec["names"], tools_dir)
        scope = "project-local" if path and str(tools_dir).lower() in path.lower() else "system" if path else "missing"
        status = "available" if path else "pending_user_path" if name in USER_PATH_TOOLS else "missing"
        entry = install_manifest.get(name, {}) if isinstance(install_manifest, dict) else {}
        rows.append({
            "tool": name,
            "evidence_target": spec["target"],
            "path": path,
            "scope": scope,
            "status": status,
            "version": version(path) or entry.get("version"),
            "sha256": sha256(path) or entry.get("sha256"),
            "source_url": entry.get("source_url"),
            "required_action": "use" if path else "ask-user-path" if name in USER_PATH_TOOLS else "install-project-local",
            "path_source": "user-paths.json" if override and path else "auto-detected",
        })
    missing = [r["tool"] for r in rows if r["status"] == "missing"]
    pending = [r["tool"] for r in rows if r["status"] == "pending_user_path"]
    result = {
        "schema": "reverse-tool-inventory/v2",
        "project": str(project),
        "default_install_dir": str(tools_dir),
        "tools": rows,
        "missing": missing,
        "pending_user_path": pending,
        "complete": not missing and not pending,
        "hard_gate": "PASS" if not missing and not pending else "FAIL",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"complete": result["complete"], "missing": result["missing"], "default_install_dir": str(tools_dir)}, ensure_ascii=False))
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
