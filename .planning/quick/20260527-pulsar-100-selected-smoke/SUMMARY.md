---
status: complete
created: 2026-05-27
completed: 2026-05-27T14:24:00+08:00
---

# Summary

Ran the user-approved Pulsar-only 100-sample selected attack smoke.

Scope:

```text
root: /data2/liyanlei/stego_attack_data/attack_runs/pulsar_100_selected_20260527
method: pulsar only
count: 100 samples per selected attack
attacks: resize 1.25, JPEG 95, median blur 3, Gaussian blur 3, Regen-VAE q6
```

All five jobs exited successfully and no non-Pulsar jobs were launched.

Raw runner records:

| Attack | Result rows | Native reveal failures | Total |
|--------|-------------|------------------------|-------|
| resize 1.25 | 2 | 98 | 100 |
| JPEG 95 | 2 | 98 | 100 |
| median blur 3 | 2 | 98 | 100 |
| Gaussian blur 3 | 2 | 98 | 100 |
| Regen-VAE q6 | 2 | 98 | 100 |

Important interpretation:

- The two raw result rows per attack are zero-capacity samples
  (`payload_bytes=0`).
- For positive-capacity samples, every selected Pulsar attack had 98/98 native
  reveal failures.
- Therefore, the meaningful 100-sample conclusion is not "2% payload
  recovery"; it is that all positive-capacity attacked samples failed native
  reveal under these selected parameters.

Quality-budget summary with LPIPS:

| Attack | PSNR | LPIPS |
|--------|------|-------|
| resize 1.25 | 43.261514 | 0.027227 |
| JPEG 95 | 47.415071 | 0.002498 |
| median blur 3 | 40.862331 | 0.027948 |
| Gaussian blur 3 | 40.165268 | 0.060507 |
| Regen-VAE q6 | 40.543400 | 0.031850 |

Artifacts:

```text
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_100_selected_20260527/selected_attack_summary_all_methods.csv
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_100_selected_20260527/pulsar_100_effective_payload_summary.csv
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_100_selected_20260527/pulsar_100_effective_payload_summary.md
```
