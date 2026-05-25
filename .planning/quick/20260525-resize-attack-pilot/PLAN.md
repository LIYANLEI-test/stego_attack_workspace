---
status: complete
created: 2026-05-25
completed: 2026-05-25
---

# Resize Attack Pilot

Run a first native resize-attack pilot using an idle GPU and report results.

## Scope

- Use MAS/GRDH because its official `robust_eval.py` already supports `resize`.
- Use the existing protocol payloads and prompt set.
- Keep the run small enough to finish interactively: 10 samples, resize factor 0.5.
- Compare attacked recovery against same-sample identity metrics.

## Verification

- `scripts/run_mas_grdh_identity.py` compiles.
- Pilot writes 10 result rows and 0 failure rows.
- Results are documented in `docs/resize_attack_pilot_20260525.md`.
