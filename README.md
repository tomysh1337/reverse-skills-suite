# Android Reverse Skills Suite

This repository packages an evidence-driven reverse-engineering workflow for APK/DEX, JNI, native ELF, VM/VMP/ZKM-style protection, and emulator validation.

The central skill is `reverse-deobf-orchestrator`. It enforces a strict `FULL_DEOBF_COMPLETE` gate: unresolved JNI registrations, native bodies, VM handlers, or missing dynamic validation remain partial.

Every run must inventory all listed reverse-engineering tools and match each protection signal to an appropriate tool. Missing open tools are installed into the project-local `.reverse-tools` directory by default; licensed tools or user-selected installations require a path decision before work continues.

When the inventory reports `pending_user_path`, place existing installations in `.reverse-tools/user-paths.json` using the keys in `reverse-deobf-orchestrator/references/tool-paths.example.json`, then rerun `scripts/tool_inventory.py`.

The repository intentionally contains workflow code and public references only. It does not contain an APK, extracted native libraries, credentials, signing keys, or private analysis output.

Public source references include `reverse-deobf-orchestrator/references/research-sources.md` and the AndroidReverse101-derived workflow at `reverse-deobf-orchestrator/references/androidreverse101.md`. The latter preserves the upstream repository URL, commit, MIT license notice, tool matrix, and evidence hard gates without copying course chapters or sample APKs.
