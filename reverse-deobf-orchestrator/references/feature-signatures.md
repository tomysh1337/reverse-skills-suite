# Protection feature signatures

These are triage indicators, not proof of a specific vendor. Record the file, offset, matched text, and confidence.

| Family | Indicators |
|---|---|
| JNI dynamic registration | `JNI_OnLoad`, `RegisterNatives`, `JNINativeMethod`, `FindClass`, `getMethodID`, method/signature string tables |
| VM/VMP dispatch | `vmInterpret`, `getJNIWrapper`, handler tables, indirect branch loops, bytecode readers, `cacheInitial` |
| Native loader | `dlopen`, `dlsym`, `mmap`, `mprotect`, executable anonymous mappings |
| Anti-trace/anti-debug | `ptrace`, `/proc/self/maps`, `/proc/<pid>/status`, `TracerPid`, debugger checks |
| ZKM/Java obfuscation | `com.zelix`, `ZKM`, encrypted string pools, control-flow switch loops, invalid/non-printable names |
| String protection | XOR/additive loops over `char[]`/`short[]`, decoder helpers, late static initialization |
| Android packer/VM | `Apk-VM`, `ApkControlFlowConfusion`, protected DEX assets, runtime class loading |

Matches must be corroborated with imports, xrefs, or runtime events before assigning a vendor or semantic name.
