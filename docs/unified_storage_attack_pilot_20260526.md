# Unified Storage Attack Pilot - 2026-05-26

## Scope

This pilot uses one shared storage attack concept across runnable identity
baselines:

```text
save stego image to lossless PNG -> reload before native reveal/recovery
samples: 0-9 per method
```

Shared implementation:

```text
scripts/attack_common.py
```

The attack is inserted after each method generates the stego image and before
its native reveal/recovery path. Embedding, sampling, decoding, and payload
generation remain method-native.

Output root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unified_storage_20260526
```

## Result Summary

CRoSS uses recovered-image PSNR as the main recovery metric. Bit-payload methods
use bit accuracy. MDDM is still a `native_third_party` 128-byte pilot, not an
official baseline.

| Method | Rows | Failures | Main metric | Exact |
|--------|------|----------|-------------|-------|
| CRoSS `native_official` | 10 | 0 | recovery PSNR 20.520565 dB, recovery SSIM 0.655835 | 0/10 |
| MAS/GRDH `native_official` | 10 | 0 | bit accuracy 0.951678 | 0/10 |
| GSD CIFAR10 `native_official` | 10 | 0 | bit accuracy 0.891048 | 0/10 |
| Pulsar `native_official` | 10 | 0 | bit accuracy 1.000000 | 10/10 |
| MDDM 128-byte `native_third_party` | 10 | 0 | bit accuracy 0.998535 | 7/10 |

## Metric Details

| Method | Mean | Std | Min | Max |
|--------|------|-----|-----|-----|
| CRoSS recovery PSNR | 20.520565 | 2.986621 | 17.028774 | 25.442797 |
| CRoSS recovery SSIM | 0.655835 | 0.099669 | 0.492262 | 0.817511 |
| MAS/GRDH bit accuracy | 0.951678 | 0.043982 | 0.830872 | 0.993408 |
| GSD CIFAR10 bit accuracy | 0.891048 | 0.044063 | 0.801107 | 0.934570 |
| Pulsar bit accuracy | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| MDDM 128-byte bit accuracy | 0.998535 | 0.003217 | 0.989258 | 1.000000 |

## Method Notes

- CRoSS: `scripts/run_cross_identity.py` now supports `--attack-kind storage`
  and records stego-vs-attacked image metrics. The storage round trip is
  lossless for the stego image (`attack_mse` 0, `attack_ssim` 1), while the
  reported main metric remains recovered-secret quality.
- MAS/GRDH: `scripts/run_mas_grdh_identity.py` applies the shared storage
  round trip to the generated `[-1,1]` image tensor before native recovery.
- GSD: `scripts/run_gsd_identity.py` applies the shared storage round trip to
  generated `[0,1]` image tensors before quantization and reverse recovery.
- Pulsar: `scripts/run_pulsar_identity.py` uses Pulsar's native 16-bit PNG
  `save_sample`/`load_sample` storage semantics. A generic 8-bit PIL RGB
  storage path is invalid for Pulsar and caused decode failures during an
  earlier discarded run.
- MDDM: `scripts/run_mddm_identity.py` passes a storage-round-tripped image
  override into the third-party decode service. This remains a pilot, not an
  official method.

## Not Included In This Pilot

- RGS: skipped for storage attack per user instruction because RGS is too slow
  on the current machine.
- Diffusion-Stego: the current workspace result is projection-only
  (`nsdser_reference`), not a complete generated-image reveal path, so a
  storage image attack would be misleading here.

## Verification

CSV integrity check:

```text
problems []
```

No duplicate sample IDs or incomplete row/failure totals were found across the
pilot result directories.
