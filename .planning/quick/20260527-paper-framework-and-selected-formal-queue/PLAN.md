---
status: complete
created: 2026-05-27
completed: 2026-05-27T16:20:00+08:00
---

# Paper Framework And Selected Formal Queue

Create a publishable experiment framework from the 10-sample quality-budget
calibration and prepare formal selected-attack sweeps.

## Tasks

1. Define a single source of truth for selected attack parameters.
2. Add a formal queue runner that executes only selected quality-budget attacks.
3. Add an aggregation script with means, standard deviations, and 95% CIs.
4. Document paper-ready reporting rules, claim boundaries, and next work.
5. Verify with compile checks and dry-run commands before launching long jobs.

## Acceptance

- Formal queue command is deterministic and resumable.
- Parameters match `docs/quality_budget_attack_selection_20260527.md`.
- Paper framework distinguishes main baselines, pilots, adapted attacks, and
  excluded methods.
- No generated images, CSVs, logs, or model files are committed.
