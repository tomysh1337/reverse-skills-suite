# Full Deobfuscation Gates

`PARTIAL` is the default. A full result requires all gates below:

1. **Artifact:** original hash, container inventory, signatures, ABI/class/Python version, and immutable copy.
2. **Tool:** complete inventory, exact versions and commands, licenses, and a direct evidence target for every selected tool.
3. **Managed code:** all classes/code objects have a verified bytecode/AST source or complete annotated pseudocode.
4. **Native code:** every native registration/export, function body, loader, string decoder, and relevant ABI has an address and evidence.
5. **VM/flow:** every dispatcher/handler/state transition is mapped; opaque predicates and exception/control-flow residues are either proven or zero.
6. **Metadata:** Minecraft entrypoints, services, mixins/refmaps, resources, reflection, and generated references are consistent.
7. **Runtime:** critical flows replay in a JVM/native/Python fixture or emulator; traces include inputs, outputs, loaded modules, and timestamps.
8. **Build:** bytecode verification, native build/ABI checks, Python import/compile checks, and full source compilation pass.
9. **Residual:** unresolved classes, methods, code objects, native bodies, handlers, strings, bootstraps, mappings, and resources are all zero.

Pseudocode, debugger output, a restoration stub, a decompiler output, or a server-side protocol model may support a report but cannot close the corresponding gate by itself.
