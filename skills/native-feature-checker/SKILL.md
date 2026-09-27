---
name: native-feature-checker
description: Evidence-based static feature scan for Android JNI, dynamic loading, VM/VMP, ZKM/Zelix, control-flow, string-pool, anti-debug, and executable-memory indicators.
---

# Native Feature Checker

Use `NP-analysis/scripts/native_feature_checker.py` as the first pass before
Ghidra/IDA/radare2 or runtime capture. The input may be an APK, an individual
ELF/DEX file, or an unpacked APK directory. The checker emits a JSON report and
a Markdown report containing category summaries plus path/offset/context
evidence.

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" `
  NP-analysis/scripts/native_feature_checker.py `
  NP-analysis/original/NP.apk `
  --out NP-analysis/reports/native-feature-check
```

The JSON schema is `native-feature-check/v1`. Consumers should use
`classification`, `categories`, and `evidence[*]`; `score` is a triage aid and
does not identify a commercial protector. A match is a static indicator, not a
recovered implementation and not a `full deobf` result. Packed/encrypted
payloads, dynamic `RegisterNatives` tables, and VM instruction streams require
runtime capture in an Android emulator/device followed by native lifting.

The rule families are:

- `jni`: `JNI_OnLoad`, `RegisterNatives`, exported `Java_*`, native declarations,
  and JNI API calls.
- `dynamic_loading`: `dlopen`/`dlsym`, class loaders, and embedded payloads.
- `vmp`: VM interpreter/dispatcher vocabulary and known sample markers.
- `zkm`: exact-case ZKM/Zelix markers and generated symbol names.
- `control_flow`: flattening, opaque-predicate, and OLLVM markers.
- `string_obfuscation`: string-pool and decoder indicators.
- `anti_debug`: `/proc`, `TracerPid`, ptrace, and instrumentation probes.
- `memory_protection`: `mprotect`, executable mappings, and cache flush APIs.

The scanner uses only the Python standard library and leaves the input artifact
unchanged.
