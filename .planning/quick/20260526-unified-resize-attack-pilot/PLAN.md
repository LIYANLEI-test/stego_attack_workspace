---
status: complete
created: 2026-05-26
completed: 2026-05-26
---

# Unified Resize Attack Pilot

Run a first comparable resize attack pilot using one shared resize
implementation across available identity baselines.

## Scope

- Use resize factors `0.5`, `0.75`, `1.25`, and `1.5`.
- Use one shared image-domain attack helper instead of each method's native
  attack variant.
- Run 10 samples per method/factor for currently runnable reveal paths.
- Preserve native embedding/sampling/recovery semantics outside the attack
  insertion point.
- Keep outputs under `/data2/liyanlei/...` and do not commit generated CSVs or
  images.

## Verification

- Each completed result directory has exactly 10 rows split between results and
  failures, with no duplicate sample IDs.
- Python runners compile.
- Results are documented in
  `docs/unified_resize_attack_pilot_20260526.md`.
