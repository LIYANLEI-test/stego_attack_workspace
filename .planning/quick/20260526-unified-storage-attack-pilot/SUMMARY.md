---
status: complete
completed: 2026-05-26
---

# Unified Storage Attack Pilot Summary

Implemented shared storage attack helpers and wired `--attack-kind storage`
into CRoSS, MAS/GRDH, GSD, Pulsar, and the MDDM pilot runners.

Run root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unified_storage_20260526
```

Headline results:

```text
CRoSS: 10/10 rows, 0 failures, mean recovery PSNR 20.520565 dB and SSIM 0.655835.
MAS/GRDH: 10/10 rows, 0 failures, mean bit accuracy 0.951678.
GSD CIFAR10: 10/10 rows, 0 failures, mean bit accuracy 0.891048.
Pulsar: 10/10 rows, 0 failures, mean bit accuracy 1.000000, exact 10/10 using native 16-bit PNG storage.
MDDM 128-byte pilot: 10/10 rows, 0 failures, mean bit accuracy 0.998535, exact 7/10.
```

RGS was skipped per user instruction because it is too slow for attack runs on
the current machine. Diffusion-Stego was not included because it is still
projection-only in this workspace.
