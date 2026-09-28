# Phantom Protector

An auditable Java JAR protector for Minecraft clients. The initial implementation is intentionally small and executable: it encrypts eligible string constants, can rename project classes, preserves Minecraft loader metadata and resources, validates transformed classes with ASM, and can check a build against a configurable verification-server contract.

## Build

Requires JDK 21 and network access on the first build. ASM is declared as a Maven dependency; no third-party source is copied into this repository.

```powershell
.
\mvnw.cmd -q -DskipTests package
```

If Maven Wrapper is unavailable, install Maven 3.9+ and run `mvn -q package`.

## Use

```powershell
java -jar target/phantom-protector-1.0.0.jar protect `
  --input client.jar --output protected-client.jar --level medium `
  --package-prefix com/example/client/ --backend http://127.0.0.1:8787
```

Profiles:

- `light`: deterministic archive rewrite and string encryption.
- `medium`: light plus deterministic project-class renaming; package allowlist is required.
- `heavy`: medium plus randomized per-build string keys and strict backend verification. This profile does not claim JVM/native virtualization.

Classes under Minecraft/Fabric/Forge/Mixin namespaces, annotated classes, module descriptors, package-info classes, and service-provider interfaces are retained. Resources are copied byte-for-byte; JSON metadata is not rewritten. Therefore medium/heavy renaming must be limited to a private package whose classes are not named in external metadata or reflection strings. The tool rejects a missing package prefix for those levels.

## Verification backend

The backend is an adapter contract (`GET /v1/status`, `POST /v1/builds`) implemented by the local fixture server. Configure a compatible endpoint with `--backend URL`. The fixture returns a build decision and does not implement production accounts, HWID collection, licensing, or upstream credentials. The backend can be disabled for offline protection builds by omitting `--backend`.

## Scope

The Java bytecode path is functional. JNIC, C/C++, Python, VM virtualization, and VMP are represented as extension points in the orchestrator and are not reported as implemented by this Java MVP. Never treat a successful archive rewrite as proof against a particular commercial protector or deobfuscator.

## Fixture test

```powershell
./mvnw.cmd -q test
```

Tests create a fixture JAR, run the protection pipeline, load and invoke the transformed class, check resource preservation and mappings, and exercise the mock backend contract.
