---
name: phantom-protector
description: Run the executable Phantom-style Java/Minecraft protector with evidence-backed profiles, metadata keep rules, deterministic mappings, and a configurable verification backend.
---

# Phantom Protector

Use this skill only after running the parent polyglot tool inventory. Treat the input JAR as immutable and write a separate output plus mapping file.

## Commands

```powershell
pwsh -File phantom-protector/scripts/run-jdk.ps1 protect --input client.jar --output build/client-light.jar --level light --seed 7
pwsh -File phantom-protector/scripts/run-jdk.ps1 protect --input client.jar --output build/client-medium.jar --level medium --package-prefix com.example.client --seed 7
pwsh -File phantom-protector/scripts/run-jdk.ps1 protect --input client.jar --output build/client-heavy.jar --level heavy --package-prefix com.example.client --backend http://127.0.0.1:8787 --seed 7
```

`light` encrypts eligible string constants. `medium` also renames classes in the explicit private package prefix. `heavy` requires a backend decision and uses a fresh seed when one is not supplied. All levels preserve Fabric/Forge/Mixin namespaces, annotations, module/package descriptors, service resources, and non-class entries.

## Backend contract

The backend adapter expects `GET /v1/status` to return `{"available":true}` and `POST /v1/builds` to return `{"accepted":true,"buildId":"..."}`. The repository includes a local fixture server used by tests. The adapter does not contain production credentials or upstream signing material.

## Completion evidence

Record input/output SHA-256, profile, seed policy, mapping file, class verification result, preserved resource checks, and backend response. A successful Java archive rewrite does not establish native/JNIC/VMP coverage. Those branches remain partial until their configured adapter supplies native bodies, registration maps, and runtime evidence.
