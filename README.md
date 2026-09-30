# Android Reverse Skills Suite

This repository packages an evidence-driven reverse-engineering workflow for APK/DEX, JNI, native ELF, VM/VMP/ZKM-style protection, and emulator validation.

The central skill is `reverse-deobf-orchestrator`. It enforces a strict `FULL_DEOBF_COMPLETE` gate: unresolved JNI registrations, native bodies, VM handlers, or missing dynamic validation remain partial.

Every run must inventory all listed reverse-engineering tools and match each protection signal to an appropriate tool. Missing open tools are installed into the project-local `.reverse-tools` directory by default; licensed tools or user-selected installations require a path decision before work continues.

When the inventory reports `pending_user_path`, place existing installations in `.reverse-tools/user-paths.json` using the keys in `reverse-deobf-orchestrator/references/tool-paths.example.json`, then rerun `scripts/tool_inventory.py`.

The repository intentionally contains workflow code and public references only. It does not contain an APK, extracted native libraries, credentials, signing keys, or private analysis output.

Public source references include `reverse-deobf-orchestrator/references/research-sources.md` and the AndroidReverse101-derived workflow at `reverse-deobf-orchestrator/references/androidreverse101.md`. The latter preserves the upstream repository URL, commit, MIT license notice, tool matrix, and evidence hard gates without copying course chapters or sample APKs.

The `polyglot-protector-orchestrator` extends the suite to desktop Java/Minecraft, C/C++ native, and Python artifacts. It contains source-grounded ZKM/PhantomShield/JNIC/native-obfuscator/VMP-style routing, `light`/`medium`/`heavy` Minecraft protection plan generation, a cross-language tool inventory, and a fail-closed full-deobfuscation gate. See `polyglot-protector-orchestrator/references/source-research.md` for repository URLs, commits, license status, and synthesized methods.

Example commands:

```powershell
python polyglot-protector-orchestrator/scripts/polyglot_tool_inventory.py --project . --tools-dir .reverse-tools --output polyglot-tool-inventory.json
python polyglot-protector-orchestrator/scripts/mc_protect.py plan --project . --level medium --languages java,cpp,python --out build/protection-plan.json
python polyglot-protector-orchestrator/scripts/mc_protect.py apply --plan build/protection-plan.json
python polyglot-protector-orchestrator/scripts/deobf_plan.py INPUT.jar --out reports/deobf-plan.json
```

The original executable Java MVP lives in `phantom-protector/`. It provides light/medium/heavy profiles, string-constant encryption, deterministic class renaming with Minecraft metadata preservation, archive verification, and a configurable Phantom-style verification backend contract. See `phantom-protector/README.md` for build and fixture commands. Its native transformation remains an adapter boundary; this legacy MVP is distinct from the current Starry desktop implementation.

The current Starry 0.6.0 application is maintained separately in the private [starry-obfuscator repository](https://github.com/tomysh1337/starry-obfuscator). The public [Starry workflow skill](skills/starry-obfuscator/SKILL.md) describes its real component routing, six desktop native targets, distribution boundaries, and verification evidence without bundling private implementation, runtime data, mappings, or third-party tool binaries. The GUI runs on Windows x64; protected JAR targets cover Windows/Linux/macOS × x64/ARM64. Windows x64 and Linux x64 have runtime evidence; the remaining targets have extraction and binary-header evidence only.

For JAR strength reviews, use the [measurement guidance](skills/java-reverse-toolchain/references/obfuscation-strength.md): separate application methods from generated runtime entries, classify invokedynamic by bootstrap, and distinguish actual execution from resource/header checks.

Create an importable skill bundle with `pwsh -File phantom-protector/scripts/package-skill.ps1 -Force`. This writes `dist/phantom-protector-v1.skill`; see `phantom-protector/IMPORT.md` for its contents, import layout, JDK-only fallback, and evidence requirements.
