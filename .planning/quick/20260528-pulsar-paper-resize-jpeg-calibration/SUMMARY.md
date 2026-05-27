---
status: complete
created: 2026-05-28
completed: 2026-05-28T00:00:00+08:00
---

# Summary

Ran the requested 10-sample paper-style Pulsar resize/JPEG calibration.

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_paper_baseline_10_20260528
```

Summary artifacts:

```text
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_paper_baseline_10_20260528/paper_baseline_summary.csv
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_paper_baseline_10_20260528/paper_baseline_summary.md
```

Results:

| Attack | Records | Paper failures | Failure rate | BER mean | PSNR | LPIPS |
|--------|--------:|---------------:|-------------:|---------:|-----:|------:|
| identity | 10 | 0 | 0.000000 | 0.284637 | inf | 0.000000 |
| resize 256->224->256 | 10 | 6 | 0.600000 | 0.478658 | 32.652135 | 0.117909 |
| JPEG Q90 | 10 | 10 | 1.000000 | 0.486659 | 41.437630 | 0.004443 |
| JPEG Q70 | 10 | 10 | 1.000000 | 0.493576 | 35.601819 | 0.016213 |

Interpretation:

- The raw Pulsar identity BER is very close to the ADS paper's reported raw
  Pulsar identity BER, so the paper-style Pulsar path appears aligned.
- JPEG Q90 and Q70 reproduce the paper's high-failure regime.
- Resize 256->224->256 gives 6/10 failures, matching the paper's 59.37%
  resize failure rate in direction and magnitude, but this 10-sample estimate
  is noisy because BER values sit very close to the 0.48 threshold.
- This confirms the workspace's earlier region/ECC Pulsar runner and the ADS
  paper's raw BER-based Pulsar evaluation are different protocols. They should
  not be compared as if they were the same metric.

Implementation note:

- Added `scripts/run_pulsar_paper_baseline.py` for paper-style raw Pulsar
  calibration. It does not replace `scripts/run_pulsar_identity.py`.
