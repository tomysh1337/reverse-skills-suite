---
name: polyglot-protector-orchestrator
description: Evidence-driven Java/C++/Python obfuscation and full deobfuscation for desktop applications and Minecraft clients. Use for ZKM/Zelix, PhantomShield-style transforms, JNIC/native-obfuscator, VMP-like native VM protection, invokedynamic/string/control-flow obfuscation, JNI hybrids, Fabric/Forge/Mixin metadata, and reproducible light/medium/heavy protection plans.
---

# Polyglot Protector Orchestrator

This skill treats obfuscation and recovery as two sides of one reproducible build. The original artifact, source tree, mappings, native libraries, and runtime traces remain immutable inputs. Every generated artifact is written to a versioned output directory with a command log, tool hash, and verification result.

## Required start

1. Run `scripts/polyglot_tool_inventory.py` against the workspace and record every available adapter, version, path, license, and evidence target. The inventory covers Java/JAR, Minecraft, C/C++/native, Python, JVM agents, bytecode editors, decompilers, emulators, and runtime tracers.
2. Run `scripts/mc_protect.py plan` for Minecraft projects or `scripts/deobf_plan.py` for an existing artifact. A plan is not completion evidence.
3. Preserve input hashes and copy outputs to `original/`, `stages/`, `decompiled/`, `native/`, `runtime/`, `mappings/`, `reports/`, and `logs/`.
4. Pin source-derived methods to the commit and license recorded in `references/source-research.md`. Do not copy third-party source into the skill package.

## Protection profiles

For the Starry desktop implementation, use [the Starry workflow](../skills/starry-obfuscator/SKILL.md). It records the implemented native targets and evidence boundaries. The legacy `phantom-protector` MVP and generic adapter plans do not establish what the current desktop application executed. For strength-only reviews, read [measurement guidance](../skills/java-reverse-toolchain/references/obfuscation-strength.md) and inspect the exact artifact hash before assigning any component or coverage claim.

Use `scripts/mc_protect.py` to generate a profile and execute only tools that are present:

```powershell
python scripts/mc_protect.py plan --project . --level light --languages java,cpp,python --out build/protection-plan.json
python scripts/mc_protect.py apply --plan build/protection-plan.json
```

The profiles are deliberately additive:

- **light**: reproducible names/mapping, debug/source metadata removal, resource-aware shrinking, symbol visibility controls, deterministic Python bytecode packaging, and verification.
- **medium**: light profile plus string/constant transforms supported by the selected Java tool, conservative control-flow transforms, selected native transpilation, C/C++ hardening flags, and runtime smoke tests.
- **heavy**: medium profile plus explicitly selected native/JVM virtualization or JNIC/native-obfuscator adapters, layered loaders, and dynamic regression capture. Heavy transforms are opt-in per package or method and must never be applied to the whole Minecraft client without a benchmark and rollback stage.

The generator preserves Fabric/Forge entrypoints, `fabric.mod.json`, `mods.toml`, mixin configs/refmaps, access wideners, `META-INF/services`, Kotlin metadata, resource paths, and reflection strings. Any unlisted entrypoint is a plan failure.

## Full deobfuscation routes

### Java and Minecraft

Use `references/protector-matrix.md` to route evidence. Run archive and class-version probes, then compare Vineflower, CFR, Recaf bytecode, `javap -v`, and a Java bytecode parser. Detect and handle one family per stage: string tables, integer/long packing, DES or XOR `invokedynamic`, member-reference `invokedynamic`, opaque predicates, exception identity, parameter descriptors, control-flow islands, and changelog mappings. Use Java Deobfuscator/Threadtear/ZKM-specific transformers only when their detector matches the artifact.

Native-transpiled Java is a separate branch. Recover JNI declarations and registration tables first, then use dynamic JVMTI/JNI traces, static binary discovery, Ghidra p-code, or CPU emulation. A decompiler view or restoration stub is not a recovered body.

### C and C++

Fingerprint PE/ELF/Mach-O, symbols, relocations, unwind data, RTTI, exception tables, imports, exports, and compiler ABI. Use Ghidra, IDA, radare2/rizin, Capstone, and a debugger as independent views. For control-flow flattening or MBA, record dispatcher/state variables, recover only proven transitions, and validate lifted pseudocode against traces or a focused emulator. VMP-like handlers require an entry-to-handler map and per-handler semantics before source synthesis.

### Python

Identify Python version from `.pyc` magic and marshal format. For PyInstaller/zipapp/Nuitka branches, inventory the container before decompilation. Use `dis`, `marshal`, `uncompyle6`/`decompyle3`, AST normalization, and runtime tracing. Preserve imports, package resources, entrypoint metadata, and native extension boundaries. A recovered AST with unresolved native calls remains partial.

## Completion gate

`FULL_DEOBF_COMPLETE` is allowed only when:

1. Original hashes, tool versions, commands, and licenses are recorded.
2. Every owned Java class/method, native function, Python module/code object, resource entrypoint, and loader has a source or complete annotated pseudocode mapping.
3. Every JNI/native boundary is matched to a registration/export and a verified body; VM/VMP dispatchers have handler maps.
4. Strings, constants, `invokedynamic`/bootstrap families, opaque predicates, flow islands, exception tricks, and packer loaders have evidence-backed transformations or an explicit zero-residual audit.
5. Fabric/Forge/Mixin/Kotlin/service metadata and native ABI behavior pass consistency checks.
6. Critical flows replay in a local fixture, JVM, native harness, Python runtime, or Android emulator as applicable, with input/output/log evidence.
7. The final source tree or pseudocode passes parse, bytecode, ABI, and build checks, and all unresolved counts are zero.

Any missing tool, missing runtime trace, guessed name, restoration stub, opaque VM call, unresolved native body, or absent metadata reference keeps the status `PARTIAL`.

Read `references/source-research.md`, `references/protector-matrix.md`, `references/minecraft-metadata.md`, and `references/full-deobf-gates.md` before reporting completion.
