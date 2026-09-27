# Android Reverse Skills Suite

This repository packages an evidence-driven reverse-engineering workflow for APK/DEX, JNI, native ELF, VM/VMP/ZKM-style protection, and emulator validation.

The central skill is `reverse-deobf-orchestrator`. It enforces a strict `FULL_DEOBF_COMPLETE` gate: unresolved JNI registrations, native bodies, VM handlers, or missing dynamic validation remain partial.

The repository intentionally contains workflow code and public references only. It does not contain an APK, extracted native libraries, credentials, signing keys, or private analysis output.
