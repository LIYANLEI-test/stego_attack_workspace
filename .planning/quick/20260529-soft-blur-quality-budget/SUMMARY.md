---
status: complete
created: 2026-05-29
completed: 2026-05-29T11:13:36+08:00
---

# Summary

Completed the soft-blur quality-budget extension requested after the original
kernel-3 blur grid failed the quality budget on GSD CIFAR10, MAS/GRDH, and
MDDM-128 pilot.

Implemented:

- `scripts/attack_common.py`: soft median blur factors below 1 use alpha
  blending with kernel-3 median blur; Gaussian blur factors below 3 use
  radius-based Gaussian blur.
- `scripts/run_quality_budget_attacks.py`: expanded blur calibration factors.
- `scripts/selected_attack_matrix.py`: added in-budget blur selections for
  GSD CIFAR10, MAS/GRDH, and MDDM-128 pilot.
- `docs/quality_budget_attack_selection_20260527.md`: updated selected rows,
  coverage, notes, and artifacts.

Results:

```text
quality summaries: 133
selected rows: 24
selected CSV: /data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary_selected.csv
driver log: /data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/logs/soft_blur_driver_20260529.log
```

New selected soft-blur settings:

```text
GSD CIFAR10: mblur 0.5, gblur 0.5
MAS/GRDH: mblur 0.5, gblur 0.5
MDDM-128 pilot: mblur 0.5, gblur 0.25
```
