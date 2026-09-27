# Logical 20+80 worker policy

The scheduler represents 100 logical workers even when the host cannot run 100 processes. `write_slots=20` own derived artifacts; `read_slots=80` inspect evidence and return independent findings. A host adapter sets `actual_concurrency` and queues excess work.

Each task record contains:

```json
{
  "id": "jni-arm64-pass-01",
  "mode": "write",
  "scope": "lib/arm64-v8a/libnpprotect.so",
  "inputs": ["sha256:..."],
  "outputs": ["reports/jni-map-arm64.csv"],
  "depends_on": ["inventory"],
  "status": "queued"
}
```

Merge rules:

- A write result is accepted only if its output hash and command log are present.
- Read-only findings are evidence candidates until a write owner reconciles them.
- Conflicting addresses or signatures remain `CONFLICT` until a third independent check resolves them.
- A queued or failed task never counts as completed coverage.
- The final gate consumes task status, not progress messages.
- Every task declares `tool_requirements` and an `evidence_target`; a task with an unrecorded missing tool is blocked rather than marked successful.
