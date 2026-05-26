---
status: complete
created: 2026-05-26
completed: 2026-05-26T14:07:00+08:00
---

# Summary

`andrekassis/ai-watermark` is suitable as an **attack-method candidate**, not as
a steganography baseline. The correct label is `unmarker_core_adapted` or similar.

Implemented a thin adapter around the official UnMarker core and ran 10 GSD
CIFAR10 samples end to end. The smoke completed 10/10 with 0 failures, mean bit
accuracy 0.765430, mean stego-vs-attacked PSNR 45.083339 dB, and mean runtime
34.61 s/sample.

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unmarker_smoke_20260526/gsd_cifar10_unmarker_high_smoke_10
```

Docs:

```text
docs/unmarker_attack_smoke_20260526.md
```
