# Importing the Phantom Protector Skill

`phantom-protector-v1.skill` is a portable skill bundle containing the executable Java MVP, its Maven metadata, and the JDK fallback scripts. It deliberately excludes `target/`, fixture JARs, mappings, local tool downloads, and user input artifacts.

## Build the bundle

From the repository root:

```powershell
pwsh -File phantom-protector/scripts/package-skill.ps1 -Force
```

The output is `dist/phantom-protector-v1.skill`. A `.skill` file is a ZIP archive; inspect it with `tar -tf` or `Expand-Archive` before importing it into a skill directory.

## Use after import

Run commands from the imported `phantom-protector` directory. The Maven path is preferred when Maven is available:

```powershell
./mvnw.cmd -q test
java -jar target/phantom-protector-1.0.0.jar protect --input client.jar --output protected.jar --level light
```

For a JDK-only environment, the bundled scripts use ASM jars from the repository's local tool cache. Supply an explicit `-AsmRoot` to `scripts/build-jdk.ps1` when the imported bundle is placed next to a different tool cache, then invoke `scripts/run-jdk.ps1`.

The `--backend` option targets a compatible local verification endpoint. The contract is `GET /v1/status` followed by `POST /v1/builds`; use a test fixture or a separately deployed service. The bundle contains no production keys, account material, HWID logic, or upstream server credentials.

## Evidence required

Keep the input JAR unchanged and retain the output SHA-256, profile, seed, mapping file, archive verification result, resource-preservation checks, and backend response. `heavy` remains a JVM bytecode profile with an explicit adapter boundary; it does not claim JNIC, native, VMP, or commercial-protector virtualization coverage.
