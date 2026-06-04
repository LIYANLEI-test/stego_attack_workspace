---
status: complete
created: 2026-06-05
completed: 2026-06-05T01:25:00+08:00
---

# Summary

Added a target-PSNR attack comparison path for the user's requested fair
comparison point.

Implemented:

- `scripts/select_target_psnr_attacks.py`: selects the parameter closest to a
  target PSNR per method/attack and writes both per-target and attack-family
  bit-payload summaries.
- `docs/target_psnr_attack_comparison_20260605.md`: records the current
  10-sample results and caveats.
- `tests/test_selected_reporting.py`: regression tests for target-PSNR
  selection and bit-summary calculations.

Generated artifacts:

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_selection.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_attack_summary_bit_methods.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_attack_summary_bit_methods_no_pulsar.csv
```

Key result excluding Pulsar from the bit-payload average:

```text
Regen-VAE: mean BER 0.2259, PSNR 29.814, LPIPS 0.1751
JPEG:      mean BER 0.2050, PSNR 30.673, LPIPS 0.0736
MBlur:     mean BER 0.1315, PSNR 30.428, LPIPS 0.1223
GBlur:     mean BER 0.1021, PSNR 29.475, LPIPS 0.1896
Resize:    mean BER 0.0966, PSNR 30.336, LPIPS 0.1865
```

Verification:

```text
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python -m py_compile scripts/select_target_psnr_attacks.py
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python -m unittest discover -s tests -v
```
