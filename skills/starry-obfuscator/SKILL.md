---
name: starry-obfuscator
description: Build, configure, or validate the Starry Java obfuscator and its protected JAR outputs, including PhantomShield transforms, native backend attribution, Windows/Linux/macOS targets, and private release evidence. Use for the Starry desktop project rather than the separate Starry Minecraft client or OpenStarry AI application.
---

# Starry Java Obfuscator

The current desktop application source is in the private [starry-obfuscator repository](https://github.com/tomysh1337/starry-obfuscator). The repository's build layout, dependency hashes and commands are authoritative. Check access and the checkout before invoking a build; this skill contains no proprietary tool binaries, activation material, server secrets or source mappings.

Use the project's README, `winui/README.md`, `docs/THIRD-PARTY.md`, and `docs/OBFUSCATION-CONFIGURATION.md` for the selected version. Preserve the user's input JAR and settings. Build output and private build evidence have separate locations; publish only the intended final artifact and checksums. Keep mappings, generated native source and account runtime state private.

## Implemented behavior in 0.6.0

- The GUI uses .NET 8 / WinUI 3 and runs on Windows x64, with Chinese and English settings. Light, medium and heavy are protection profiles, not user-facing engine brands.
- Enhanced strings invoke the OpenPhantomShield stage before the bytecode stage. Native compilation routes compatible methods to j2c, JNIC and native-obfuscator. Read actual per-stage counts; a configured branch may select zero methods.
- `NativeTargets=desktop64` packages Windows/Linux/macOS × x64/ARM64 in one JAR. Each target can also be selected individually. Select according to the running JVM architecture, including x64 JVMs on ARM machines.
- Android, iOS, 32-bit JVMs and Linux musl are outside this native target set. Plain Java profiles still depend on application/JVM compatibility.
- Generated native resources receive length/SHA-256 integrity checks before extraction when enabled. This is resource integrity, not a claim that runtime code or memory cannot be modified.

## Verification

For the exact output hash, inspect `report.json` and the separate release, platform, integrity and runtime evidence. Verify methods by original-to-final identities privately, and verify actual PE/ELF/Mach-O architecture rather than filenames.

The project provides `tests/check_snake_release.py`, `tests/check_platform_release.py` and `tests/check_native_integrity.py`, each taking a build `report.json`. Use Snake only as a fixture; passing it does not establish compatibility with an arbitrary application. The combined EngineChecks fixture exercises all three native routes even when Snake has zero j2c matches.

As of the 0.6.0 acceptance run, Windows x64 and Linux x64 were actually executed. Windows ARM64, Linux ARM64 and both macOS targets had successful payload extraction/header validation and await target-machine runtime tests. Preserve this distinction in later reports unless new evidence changes it.

For strength analysis, separate application native methods from runtime entries, classify invokedynamic by bootstrap, and use a declared coverage denominator. Do not equate jump counts with flattening, entropy with cryptographic strength, or a `Hidden0` name with JVM hidden-class semantics. Attribute transformations from hash-matched build evidence and observable loader paths; never reuse a previous fixture's counts as current measurements.
