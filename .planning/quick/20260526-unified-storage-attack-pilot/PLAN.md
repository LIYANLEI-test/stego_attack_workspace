---
status: complete
created: 2026-05-26
completed: 2026-05-26
---

# Unified Storage Attack Pilot

Run a first comparable storage attack pilot using one shared storage
round-trip concept across available non-RGS identity baselines.

## Scope

- Use lossless PNG save/reload as the storage attack.
- Run 10 samples per method for currently runnable non-RGS reveal paths.
- Preserve native embedding/sampling/recovery semantics outside the attack
  insertion point.
- Use Pulsar's native 16-bit sample storage path instead of generic 8-bit PIL
  conversion.
- Keep outputs under `/data2/liyanlei/...` and do not commit generated CSVs or
  images.

## Verification

- Each completed result directory has exactly 10 rows split between results and
  failures, with no duplicate sample IDs.
- Python runners compile.
- Results are documented in
  `docs/unified_storage_attack_pilot_20260526.md`.
