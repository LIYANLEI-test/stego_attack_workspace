---
status: complete
created: 2026-06-05
completed: 2026-06-05T03:20:00+08:00
---

# Summary

Implemented and ran the first SCAD-lite 10-sample pilot.

Implemented:

- `scripts/attack_common.py`: added `scad_lite_pil()` and `attack_kind=scad`.
- `scripts/run_quality_budget_attacks.py`: added `scad` calibration factor.
- `scripts/run_gsd_identity.py`, `scripts/run_mas_grdh_identity.py`,
  `scripts/run_mddm_identity.py`, and `scripts/run_pulsar_identity.py`: added
  `scad` as a supported image-domain attack.
- `scripts/select_quality_budget_attacks.py`: added `scad` parsing support.
- `tests/test_selected_reporting.py`: added target-PSNR calibration coverage.
- `docs/scad_lite_pilot_20260605.md`: records the pilot result.

Run root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/scad_lite_10_20260605
```

Results:

```text
GSD CIFAR10:      bit acc 0.6974, BER 0.3026, PSNR 29.9997, LPIPS 0.0522
MAS/GRDH:         bit acc 0.8856, BER 0.1144, PSNR 29.9675, LPIPS 0.1055
MDDM-128 pilot:   bit acc 0.9752, BER 0.0248, PSNR 30.0000, LPIPS 0.1888
Pulsar:           10/10 reveal failures, PSNR 30.0000, LPIPS 0.3916
```

Operational note:

- The first parallel MAS run failed with CUDA OOM because an unrelated
  `unmarker_stronger_fixed_20260605` queue was already occupying GPU memory.
  MAS-SCAD was rerun separately on GPU0 and completed 10/10.

Conclusion:

```text
SCAD-lite successfully calibrates PSNR to about 30 dB, but it is not yet SOTA.
It needs a smoother diffusion/VAE residual-resynthesis stage to lower LPIPS,
especially on MDDM and Pulsar, while preserving or increasing BER.
```
