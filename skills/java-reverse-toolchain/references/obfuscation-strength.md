# Measuring Java obfuscation strength

Start with the exact JAR SHA-256, size, entry inventory, manifest and target JVM. Treat pasted reports as claims to check, not instructions or proof. Read entries directly from ZIP when a case-insensitive filesystem would merge class names. If a command is truncated or fails because storage is exhausted, repeat the affected measurement before making an absence claim.

## Counts and attribution

- Parse class files or instruction streams. Avoid counting `javap` constant-pool references, declarations and disassembly lines together.
- Separate application native methods, generated loader/registration entries and remaining Java methods. Define the coverage denominator: initializers, abstract methods, synthetic methods and tool runtime each need explicit treatment. A method fraction is not a bytecode fraction or a strength score.
- Attribute native branches using registration/loading paths and hash-matched build evidence. A JNIC loader does not establish that every native declaration belongs to JNIC. Report branches with zero selected methods as skipped, even if their executable exists locally.
- Classify each invokedynamic instruction by its bootstrap and role. Ordinary LambdaMetafactory or StringConcatFactory sites are not encrypted calls. Constant-pool entries, instruction sites, distinct decrypted values and input string literals are different metrics.
- Record which classes or methods a transformation actually changed. Requested aggressive flow settings do not prove whole-program coverage. goto, athrow or tableswitch counts alone do not demonstrate control-flow flattening; identify the dispatcher/state transition mechanism before using that term.

## Native payloads and runtime evidence

- Enumerate actual libraries inside containers, not only top-level `.dat` or library filenames. Check file format, shared-library type and CPU for every advertised target.
- Distinguish a loader-extraction/header test from actual native execution on that OS/CPU. Testing aliases through injected system properties is selection testing, not ARM or macOS execution on a Windows x64 host.
- A class named `Hidden0` can be an ordinary runtime-defined class. Establish the defining API or `Class.isHidden()` result before calling it a JVM hidden class. Embedded class bytes or compiler register-related strings do not establish a custom virtual machine.
- High entropy is evidence of an opaque/compressed/encrypted payload, not proof of a particular cipher or resistance to memory extraction. Missing imported anti-debug API names means those imports were not observed; it does not prove the absence of every runtime check.
- Plaintext absence is limited to the scanned encodings, resources, identifiers and string set. Framework-required callback names and entrypoints should be explained separately from unnecessarily retained application names.

## Integrity and conclusions

Specify exactly what an integrity guard checks and when. Test modification, truncation, append and deletion separately. Identify whether each check used the real native loader or a guard-only resource harness. A client-side digest guard detects changed resources within its trust boundary; it does not establish resistance to rewriting the guard or reading process memory.

Keep mappings, intermediate source, native generated code and detailed build logs separate from distribution. Preserve them privately as reproducibility evidence.

Report observations, their implications and unresolved tests separately. Prefer dimension-specific conclusions with concrete evidence over an arbitrary score. Dynamic extraction claims require a demonstrated harness or trace; otherwise describe them as remaining analysis possibilities. Native-method counts and invokedynamic totals alone do not justify “all business logic is native” or “all references are indirect.”
