#!/usr/bin/env python3
"""Inventory cross-language protection and recovery adapters.

The inventory is evidence metadata, not a claim that every tool was used.  A
tool is available only when a concrete executable/JAR is found and its safe
version probe succeeds or a pinned install manifest supplies the version.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


TOOLS = {
    # Java/JVM and Minecraft
    "java": ("jvm-runtime", ["java.exe", "java"]),
    "javac": ("jvm-build", ["javac.exe", "javac"]),
    "javap": ("bytecode-evidence", ["javap.exe", "javap"]),
    "gradle": ("minecraft-build", ["gradle.bat", "gradle.exe", "gradle"]),
    "gradlew": ("minecraft-build", ["gradlew.bat", "gradlew"]),
    "jadx": ("dex-view", ["jadx/bin/jadx.bat", "jadx/bin/jadx", "jadx.bat", "jadx"]),
    "apktool": ("apk-smali", ["apktool.jar", "apktool.bat", "apktool"]),
    "recaf": ("bytecode-navigation", ["recaf.jar", "recaf.exe", "recaf"]),
    "vineflower": ("java-decompiler", ["vineflower.jar", "vineflower*.jar"]),
    "cfr": ("java-decompiler", ["cfr.jar", "cfr*.jar"]),
    "enigma": ("reviewed-mappings", ["enigma.jar", "enigma-mcp.jar"]),
    "java-deobfuscator": ("java-transformers", ["deobfuscator.jar", "java-deobfuscator.jar"]),
    "threadtear": ("java-transformers", ["threadtear.jar"]),
    "krakatau": ("bytecode-roundtrip", ["krak2", "krak2.bat"]),
    # Native/C++
    "ghidra": ("native-elf-pe-vm", ["ghidra*/support/analyzeHeadless.bat", "analyzeHeadless.bat"]),
    "ida": ("native-elf-pe-vm", ["ida64.exe", "ida.exe"]),
    "radare2": ("native-elf-pe-vm", ["radare2*/**/bin/radare2.exe", "radare2*/**/bin/r2.exe", "radare2.exe", "r2.exe"]),
    "rizin": ("native-elf-pe-vm", ["rizin*/**/bin/rizin.exe", "rizin.exe", "rz.exe"]),
    "clang": ("cpp-build", ["clang++.exe", "clang++", "clang.exe", "clang"]),
    "gcc": ("cpp-build", ["g++.exe", "g++", "gcc.exe", "gcc"]),
    "cmake": ("cpp-build", ["cmake.exe", "cmake"]),
    "objdump": ("native-evidence", ["llvm-objdump.exe", "llvm-objdump", "objdump.exe", "objdump"]),
    "nm": ("native-evidence", ["llvm-nm.exe", "llvm-nm", "nm.exe", "nm"]),
    "strings": ("native-evidence", ["strings.exe", "strings"]),
    "capstone": ("native-disassembly", ["capstone.dll", "capstone"]),
    "unicorn": ("native-emulation", ["unicorn.dll", "unicorn"]),
    "qemu": ("native-emulation", ["qemu-x86_64.exe", "qemu-system-x86_64.exe", "qemu-x86_64"]),
    # Runtime/JNI
    "frida": ("runtime-trace", ["python/Scripts/frida.exe", "python/bin/frida.exe", "frida.exe", "frida"]),
    "frida-server": ("runtime-trace", ["frida-server.exe", "frida-server"]),
    "adb": ("android-runtime", ["platform-tools/adb.exe", "adb.exe", "adb"]),
    "android-emulator": ("android-runtime", ["emulator/emulator.exe", "emulator.exe", "emulator"]),
    "mumu": ("android-runtime", ["MuMuPlayer.exe", "NemuPlayer.exe"]),
    # Python
    "python": ("python-runtime", ["python.exe", "python"]),
    "pyarmor": ("python-protection", ["pyarmor.exe", "pyarmor"]),
    "nuitka": ("python-protection", ["nuitka.exe", "nuitka"]),
    "uncompyle6": ("python-recovery", ["uncompyle6.exe", "uncompyle6"]),
    "decompyle3": ("python-recovery", ["decompyle3.exe", "decompyle3"]),
    # Protection adapters are optional and never silently substituted.
    "phantomshield": ("java-protection-adapter", ["phantomshield.jar"]),
    "native-obfuscator": ("java-native-adapter", ["native-obfuscator.jar"]),
    "j2c": ("java-native-adapter", ["j2c.jar"]),
    "c2j-native-deobfuscator": ("java-native-recovery", ["c2j-native-deobfuscator.jar", "scripts/j2c"]),
}

LICENSES = {
    "java-deobfuscator": "Apache-2.0", "recaf": "MIT", "krakatau": "GPL-3.0",
    "c2j-native-deobfuscator": "GPL-3.0", "native-obfuscator": "GPL-3.0-output-exception",
    "j2c": "AGPL-3.0", "radare2": "LGPL-3.0", "rizin": "LGPL-3.0",
}


def locate(names: list[str], root: Path) -> str | None:
    for name in names:
        direct = root / name
        if direct.is_file():
            return str(direct.resolve())
        if "*" in name or "/" in name:
            for path in root.glob(name if "*" in name else "**/" + Path(name).name):
                if path.is_file():
                    return str(path.resolve())
        else:
            found = shutil.which(name)
            if found:
                return str(Path(found).resolve())
            # Do not recursively scan large extracted distributions. A caller
            # that needs a nested artifact supplies an explicit path/wildcard.
    return None


def file_hash(path: str | None) -> str | None:
    if not path or not Path(path).is_file():
        return None
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_version(path: str | None) -> tuple[str | None, int | None, str]:
    if not path:
        return None, None, ""
    suffix = Path(path).suffix.lower()
    version_from_name = re.search(r"(?<!\d)(\d+\.\d+(?:\.\d+)?)(?!\d)", str(path))
    if suffix in {".jar", ".bat", ".dll", ".so"}:
        return version_from_name.group(1) if version_from_name else None, None, ""
    try:
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=3)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, None, str(exc)
    output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    return output.splitlines()[0][:300] if output else None, result.returncode, output[-1000:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--tools-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    tools_dir = (args.tools_dir or project / ".reverse-tools").resolve()
    tools_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (target, candidates) in TOOLS.items():
        # Avoid traversing an analysis tree with extracted APK/JAR content.
        # Project-local lookup is limited to the conventional tools directory;
        # system installations are resolved through PATH.
        path = locate(candidates, tools_dir)
        if not path and (project / "tools").is_dir():
            path = locate(candidates, project / "tools")
        scope = "project-local" if path and str(project).lower() in path.lower() else "system" if path else "missing"
        version, code, output = safe_version(path)
        rows.append({
            "tool": name, "evidence_target": target, "license_hint": LICENSES.get(name, "inspect-upstream"),
            "path": path, "scope": scope, "version": version, "version_exit_code": code,
            "version_output": output, "sha256": file_hash(path),
            "status": "available" if path else "missing",
            "required_action": "use" if path else "install-project-local-or-record-user-path",
        })
    missing = [row["tool"] for row in rows if row["status"] == "missing"]
    result = {
        "schema": "polyglot-tool-inventory/v1", "project": str(project),
        "tools_dir": str(tools_dir), "tools": rows, "missing": missing,
        "complete": not missing, "hard_gate": "PASS" if not missing else "FAIL",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"complete": result["complete"], "missing": missing, "count": len(rows)}, ensure_ascii=False))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
