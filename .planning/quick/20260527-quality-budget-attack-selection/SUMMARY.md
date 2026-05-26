---
status: complete
created: 2026-05-27
completed: 2026-05-27T15:40:00+08:00
---

# Summary

Completed the 10-sample quality-budget calibration for the currently runnable
attack methods and generation/recovery baselines.

Budget:

```text
stego-vs-attacked PSNR >= 30 dB
stego-vs-attacked LPIPS <= 0.10
```

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527
```

Selected parameter table:

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary_selected.csv
```

Doc:

```text
docs/quality_budget_attack_selection_20260527.md
```

The selector now treats native recovery failures after a saved attacked image
as complete payload recovery failure while still computing image quality from
the saved stego/attacked image pair. Pulsar therefore appears correctly in the
selected table: all selected attacks keep high visual quality but cause native
reveal failure on the 10-sample calibration set.
