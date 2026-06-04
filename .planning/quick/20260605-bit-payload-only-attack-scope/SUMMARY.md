---
status: complete
created: 2026-06-05
completed: 2026-06-05T02:05:00+08:00
---

# Summary

Updated the active attack-comparison scope to bit-payload steganography methods
only.

Implemented:

- `scripts/select_target_psnr_attacks.py`: added method filtering and
  `--bit-payload-only`.
- `scripts/render_paper_tables.py` and
  `scripts/audit_selected_attack_results.py`: current main table now excludes
  image-payload methods.
- `scripts/selected_attack_matrix.py`: active formal matrix now uses bit-only
  target-PSNR parameters.
- `docs/target_psnr_attack_comparison_20260605.md`: removed the CRoSS section
  and made the active target-PSNR report bit-only.
- `docs/paper_experiment_framework_20260527.md`: current main-table candidates
  are GSD CIFAR10, MAS/GRDH, and Pulsar; MDDM remains pilot/appendix.
- `tests/test_selected_reporting.py`: added regression coverage for bit-only
  target selection and CRoSS exclusion from current main paper tables.

Generated artifacts:

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_selection_bit_payload.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_attack_summary_bit_payload.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_attack_summary_bit_payload_no_pulsar.csv
```

No full-scale queue was launched.
