---
name: reverse-deobf-orchestrator
description: Evidence-driven Android/APK reverse-engineering orchestration for Java/Dex, JNI, native ELF, VMP/ZKM-style protection, and emulator validation. Use when a reverse task requires strict full-deobfuscation status, coordinated static and dynamic analysis, feature detection, reproducible evidence, or a 20-write/80-read logical worker plan.
---

# Reverse Deobfuscation Orchestrator

Use this skill to coordinate APK, DEX, JNI, native ELF, VM/VMP, and dynamic-runtime work. Keep the original artifact immutable and write every derived artifact to a separate analysis directory.

## Mandatory tool coverage gate

Before analysis, run `scripts/tool_inventory.py` and record every required tool, detected path, version, installation scope, and intended evidence target. The inventory is mandatory for every run and must cover JADX, apktool, dex2jar, Recaf, Enigma/Enigma-MCP, Vineflower, CFR, Ghidra, IDA, radare2/rizin, Frida, ADB, an Android emulator, MuMu when selected, and the Java/Python runtimes.

For each protection signal, select a tool that directly addresses it and record the reason: JADX/Recaf/Vineflower/CFR for managed bytecode, Enigma for reviewed names, Ghidra/IDA/radare2/rizin for ELF and VM handlers, Frida/ADB/emulator for JNI registration and loaded code, and apktool/smali for resource or packaging verification. A generic tool list without an evidence target is a gate failure.

If a required tool is missing, install it into the project-local `.reverse-tools` directory by default and record the download URL, version, SHA-256, and command log. If the tool requires a commercial license or a user-selected existing installation, pause and ask where to install or which existing path to use. Never silently substitute a missing tool or claim that its analysis ran.

For an existing IDA, Android Emulator, or MuMu installation, put explicit paths in `.reverse-tools/user-paths.json` using `references/tool-paths.example.json`, then rerun `scripts/tool_inventory.py --project . --tools-dir .reverse-tools --output tool-inventory.json`.

## Hard completion gate

Never label a result `FULL_DEOBF_COMPLETE` because JADX produced source or because a native library was disassembled. Use `PARTIAL` until every protected boundary is evidenced.

Set `FULL_DEOBF_COMPLETE` only when all of these are true:

1. The original APK and every analyzed native library have recorded SHA-256 hashes and remain unchanged.
2. All DEX/classes are exported with package/class/member mappings, resource references, and no unexplained class-loading gaps.
3. Every Java native declaration is matched to a JNI registration entry or a verified static export, including class, method, signature, ABI, library, RVA/offset, and confidence.
4. Every dynamically registered JNI entry has a recovered native body represented as source or complete annotated pseudocode. A stub, guessed body, or unresolved VM call is not recovery.
5. VM/VMP/ZKM dispatch is mapped from entry to handler. `vmInterpret`, opaque dispatcher calls, encrypted string loaders, and control-flow flattening residues must have a documented handler map.
6. Critical flows are replayed in an Android emulator/device or a documented local sandbox. Capture the action, process, loaded modules, DEX path, JNI call, native offset, input, output, and logs.
7. Recovered source/pseudocode passes consistency checks: descriptors, call targets, resource references, and ABI calling conventions agree with the artifact and runtime evidence.
8. The final report lists zero unresolved protected methods. Any unresolved item forces `PARTIAL` and must include a blocker and next evidence required.
9. The tool inventory is complete, every applicable tool has either produced evidence or has a recorded, evidence-based reason it is not applicable, and missing tools are not silently skipped.

Pseudocode and debugger output may be used as evidence, but the report must say `pseudocode-recovered` and show complete coverage. They do not convert an unresolved method into a full result.

## Workflow

1. Fingerprint: hash the APK, enumerate DEX, manifest, components, permissions, ABIs, assets, native libraries, loaders, and framework markers.
2. Managed layer: run JADX and a second view when available. Preserve original package names and emit a reviewed mapping CSV.
3. Native boundary: locate `System.loadLibrary`, `dlopen`, `JNI_OnLoad`, `RegisterNatives`, `JNINativeMethod` arrays, `getJNIWrapper`, VM interpreters, anti-trace probes, and memory-permission changes.
4. Feature scan: run `scripts/feature_check.py` against the APK or extracted directory. Store JSON and Markdown output.
5. Static native analysis: use Ghidra headless or radare2 per ABI. Export function inventory, imports/exports, string references, JNI candidates, call graphs, and decompiler output for critical functions.
6. Dynamic bridge recovery: use `scripts/frida_register_natives.js` and `scripts/mumu_capture.ps1` on a test emulator/device. Capture registrations and loaded DEX/native modules; never infer missing registrations from names alone.
7. Synthesis: merge static and runtime evidence into `jni-map.csv`, `native-functions.csv`, `vm-handlers.csv`, and a status report.
8. Gate: run `scripts/full_deobf_gate.py`. The script returns success only when all required evidence files exist and contain no unresolved entries.

## Logical worker policy

The default plan is 100 logical roles: 20 write-capable analysis roles and 80 read-only evidence roles. The runtime adapter must report the actual host concurrency cap and queue the remainder; never claim that queued roles executed. Write roles may modify only assigned derived files. Read-only roles cannot modify source artifacts. Every role returns file paths, hashes, commands, and confidence.

Recommended role split:

- 20 write roles: manifest/DEX, mapping, JNI table, four ABI native passes, VM handler synthesis, dynamic trace merge, report, and verification owners.
- 80 read roles: independent string/import/xref/function/permission/resource reviews, duplicate-result checks, and evidence audits.

Use `references/agent-policy.md` for the queue schema and merge rules.

## Runtime environments

Prefer an isolated Android emulator. MuMu is acceptable when ADB is enabled. Install only a copied APK, collect `adb logcat`, and keep snapshots clean. If no emulator is available, generate the capture scripts and mark dynamic status `BLOCKED_RUNTIME`; do not call the result full.

## Outputs

Required outputs are `reports/analysis-summary.md`, `reports/full-deobf-status.json`, `reports/jni-map.csv`, `reports/native-functions.csv`, `reports/vm-handlers.csv`, `reports/feature-scan.json`, and `mappings/names.csv`. Link every claim to a file, command, address, or runtime event.

Read `references/research-sources.md` for public GitHub/CSDN JNI, VMP, ZKM, and native analysis references and platform applicability notes.

Read `references/androidreverse101.md` for the AndroidReverse101-derived stage map, tool/evidence hard gates, and MIT source notice.

Use `native-feature-checker` before native lifting; its score is triage only and never proves full deobfuscation.

For desktop Java/Minecraft, C/C++ native, Python bytecode, ZKM/PhantomShield/JNIC/native-obfuscator, or VMP-like mixed artifacts, hand off to `../polyglot-protector-orchestrator/SKILL.md`. It shares the same immutable-artifact, tool-evidence, 20+80 scheduling, and fail-closed completion contract.
