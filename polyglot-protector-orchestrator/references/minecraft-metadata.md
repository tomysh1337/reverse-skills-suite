# Minecraft Client Metadata Closure

Minecraft clients have coupling outside class bytecode. Every protection or recovery plan must inventory and validate:

- Fabric `fabric.mod.json`, entrypoints, mixins, refmaps, access wideners, nested jars, and language adapters.
- Forge/NeoForge `mods.toml`, `META-INF/services`, coremod/access-transformer files, and launch targets.
- Kotlin metadata, service-provider files, `MANIFEST.MF`, multi-release paths, resource JSON, shader paths, and reflection strings.
- Gradle version catalogs, mappings, loader/API versions, Java toolchain, generated sources, and native libraries.

Protection plans keep entrypoint and serializer names, preserve mixin/refmap/resource paths, and write a mapping report. Recovery plans compare class/resource references before and after each stage and run a clean Gradle compile plus a minimal loader fixture before claiming IDEA-ready or full recovery.

Do not obfuscate the complete Minecraft dependency graph. Apply native transpilation, virtualization, or aggressive flow transforms only to a selected package/method allowlist and record benchmark/rollback artifacts.
