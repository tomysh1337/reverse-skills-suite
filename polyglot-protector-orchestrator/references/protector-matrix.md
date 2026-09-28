# Protector Matrix

| Signal | Static indicators | Primary route | Required evidence |
|---|---|---|---|
| ZKM/XOR tables | repeated XOR helpers, packed integer/string arrays, once-written sentinels | ASM/Java Deobfuscator/ZKM-27 style bounded pass | before/after class hash, decoded constants, verifier pass |
| ZKM DES/indy | bootstrap methods, `invokedynamic`, DES-shaped helpers | bootstrap inventory, isolated constant evaluation, CFR/Vineflower/javap comparison | callsite-to-value map and no unresolved bootstrap |
| ZKM flow/exception | opaque guards, shared tails, dummy handlers | CFG normalization and exception table audit | preserved descriptors/frames and control-flow proof |
| PhantomShield-like | annotation names, transformer config, native loader, VM family labels, verification lock | inspect annotations/config, then Java/native branch | transform detection, loader/module map, runtime checks |
| JNIC/native-obfuscator/j2c | native declarations, `JNI_OnLoad`, `RegisterNatives`, packaged `.dll/.so`, string pool | JNI manifest, JVMTI/JNI trace, Ghidra/r2, c2j-style lifter | class/method/signature/function pointer/RVA/body |
| VMP/native VM | dispatcher loops, handler tables, opaque state, executable memory changes | Ghidra/IDA/r2 plus debugger/emulator | entry-to-handler map and replayed semantics |
| Python bytecode/packers | `.pyc` magic, marshal, PyInstaller archive, Nuitka/native extension | versioned bytecode parser, container extraction, `dis`, runtime trace | module/code-object map, imports/resources, native boundary |

Names are never inferred solely from short identifiers. Use neutral stable names until call sites, descriptors, resources, stack traces, or runtime events support a semantic mapping.
