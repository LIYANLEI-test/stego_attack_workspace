---
status: complete
created: 2026-05-26
completed: 2026-05-26T14:07:00+08:00
---

# UnMarker Attack Candidate Smoke

Assess whether `andrekassis/ai-watermark` is suitable for this project's paper
comparison, and if suitable, run a 10-image smoke.

## Decision

The repository is not a hiding/steganography baseline. It is the official
UnMarker attack implementation for defensive image watermarking, so it should
only be considered as an attack-method candidate.

It is suitable enough to keep as a candidate because the core attack is a recent,
published, detector-feedback-free image-domain optimization. It must be labeled
as adapted when applied to our steganographic recovery protocol.

## Execution

- Added `references/ai-watermark` as a pinned reference checkout.
- Added `scripts/unmarker_attack.py`, a thin adapter around the official
  UnMarker coordinate optimization core.
- Added `--attack-kind unmarker` to `scripts/run_gsd_identity.py`.
- Ran a 10-sample GSD CIFAR10 smoke with high-frequency UnMarker core, smoke
  profile, and 25 iterations.

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unmarker_smoke_20260526/gsd_cifar10_unmarker_high_smoke_10
```

## Result

| Method | Attack | Rows | Failures | Main metric |
|--------|--------|------|----------|-------------|
| GSD CIFAR10 | UnMarker-core high-frequency smoke | 10 | 0 | mean bit accuracy 0.765430 |

Saved attacked-image quality:

```text
mean stego-vs-attacked PSNR: 45.083339 dB
mean stego-vs-attacked MAE: 1.336328
mean runtime: 34.61 s/sample
```

## Caveats

- Smoke-only; not a full paper result.
- GSD CIFAR10 is 32x32, chosen because full UnMarker settings are heavy and the
  official README asks for at least 32 GB GPU memory.
- The original UnMarker paper evaluates defensive watermark detector removal,
  while this smoke evaluates native steganographic message recovery after attack.
