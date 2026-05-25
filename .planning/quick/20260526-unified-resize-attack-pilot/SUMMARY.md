---
status: complete
completed: 2026-05-26
---

# Unified Resize Attack Pilot Summary

Implemented `scripts/attack_common.py` as the shared resize attack and wired it
into CRoSS, MAS/GRDH, GSD, Pulsar, and the MDDM pilot runners.

Run root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unified_resize_20260526
```

Completed factors:

```text
0.5, 0.75, 1.25, 1.5
```

Headline results:

```text
CRoSS: 10/10 rows for each factor, 0 failures, mean recovery PSNR 18.619120 / 20.542374 / 21.086257 / 19.920919 dB.
MAS/GRDH: 10/10 rows for each factor, 0 failures, mean bit accuracy 0.878314 / 0.926898 / 0.943085 / 0.941510.
GSD CIFAR10: 10/10 rows for each factor, 0 failures, mean bit accuracy 0.592936 / 0.685417 / 0.781608 / 0.785319.
Pulsar: 0 rows and 10 reveal failures for each factor; resize breaks native decode in this pilot.
MDDM 128-byte pilot: 10/10 rows for each factor, 0 failures, mean bit accuracy 0.983398 / 0.994336 / 0.998145 / 0.998145.
```

RGS and Diffusion-Stego were not included in this quick pilot. RGS needs a
dedicated in-memory attack branch and is long-running. Diffusion-Stego is still
projection-only in this workspace.
