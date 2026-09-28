# Protection Profiles

The plan generator emits commands only for tools present in the inventory. Profiles are conservative defaults and must be reviewed per project.

| Level | Java/Minecraft | C/C++ | Python | Validation |
|---|---|---|---|---|
| light | shrink/rename with keep rules, remove debug/source metadata, preserve mappings/resources | hidden visibility, section GC, LTO when supported, strip release symbols | deterministic pyc/zipapp, source metadata cleanup | archive/resource diff, compile/import smoke |
| medium | light plus selected string/constant and flow passes, Enigma mapping, optional native-obfuscator allowlist | hardened release flags, optional LLVM transforms if installed | PyArmor or equivalent if installed, otherwise blocked | bytecode verifier, native smoke, runtime fixture |
| heavy | medium plus explicitly selected Phantom/JNIC/native/VM adapter per package | selected native VM/LLVM adapter, no whole-client default | compiled distribution/Nuitka/PyArmor adapter if installed | staged replay, ABI map, rollback and performance report |

The script never claims that a missing commercial or runtime-dependent tool ran.
