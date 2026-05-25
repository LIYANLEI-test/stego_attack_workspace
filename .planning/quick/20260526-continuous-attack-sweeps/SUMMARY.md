---
status: complete
completed: 2026-05-26
---

# Continuous Attack Sweeps Summary

Completed non-RGS JPEG, median blur, and Gaussian blur 10-sample pilots across
CRoSS, MAS/GRDH, GSD CIFAR10, Pulsar, and the MDDM 128-byte pilot.

Run root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unified_image_attacks_20260526
```

Completed matrix:

```text
3 attack families x 3 factors x 5 methods = 45 result directories.
Each directory has exactly 10 total sample records and no duplicate sample IDs.
```

Key outcomes:

```text
CRoSS completed all JPEG/blur settings with recovery PSNR ranging from 17.780781 to 20.209000 dB.
MAS/GRDH completed all settings with bit accuracy ranging from 0.748199 to 0.927435.
GSD CIFAR10 completed all settings with bit accuracy ranging from 0.528385 to 0.701009.
Pulsar generated all attacked samples but native reveal failed for all lossy JPEG/blur settings.
MDDM 128-byte pilot completed all settings with bit accuracy ranging from 0.933496 to 0.996680.
```

RGS attacks remained excluded per user instruction, but the RGS identity run
finished separately at 100/100 rows, 0 failures, mean recovery PSNR 23.316454
dB.
