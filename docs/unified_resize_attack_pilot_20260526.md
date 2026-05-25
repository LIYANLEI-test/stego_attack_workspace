# Unified Resize Attack Pilot - 2026-05-26

## Scope

This pilot uses one shared image-domain resize attack across runnable identity
baselines:

```text
resize by factor -> resize back to original size
RGB image domain
PIL Image.Resampling.BILINEAR
factors: 0.5, 0.75, 1.25, 1.5
samples: 0-9 per method/factor
```

Shared implementation:

```text
scripts/attack_common.py
```

The attack is inserted after each method generates/saves the stego image and
before its native reveal/recovery path. The embedding, sampling, decoding, and
payload generation paths remain method-native.

Output root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unified_resize_20260526
```

## Result Summary

CRoSS uses recovered-image PSNR as the main recovery metric. Bit-payload methods
use bit accuracy. MDDM is still a `native_third_party` 128-byte pilot, not an
official baseline.

| Method | Factor | Rows | Failures | Main metric | Exact |
|--------|--------|------|----------|-------------|-------|
| CRoSS `native_official` | 0.5 | 10 | 0 | recovery PSNR 18.619120 dB | 0/10 |
| CRoSS `native_official` | 0.75 | 10 | 0 | recovery PSNR 20.542374 dB | 0/10 |
| CRoSS `native_official` | 1.25 | 10 | 0 | recovery PSNR 21.086257 dB | 0/10 |
| CRoSS `native_official` | 1.5 | 10 | 0 | recovery PSNR 19.920919 dB | 0/10 |
| MAS/GRDH `native_official` | 0.5 | 10 | 0 | bit accuracy 0.878314 | 0/10 |
| MAS/GRDH `native_official` | 0.75 | 10 | 0 | bit accuracy 0.926898 | 0/10 |
| MAS/GRDH `native_official` | 1.25 | 10 | 0 | bit accuracy 0.943085 | 0/10 |
| MAS/GRDH `native_official` | 1.5 | 10 | 0 | bit accuracy 0.941510 | 0/10 |
| GSD CIFAR10 `native_official` | 0.5 | 10 | 0 | bit accuracy 0.592936 | 0/10 |
| GSD CIFAR10 `native_official` | 0.75 | 10 | 0 | bit accuracy 0.685417 | 0/10 |
| GSD CIFAR10 `native_official` | 1.25 | 10 | 0 | bit accuracy 0.781608 | 0/10 |
| GSD CIFAR10 `native_official` | 1.5 | 10 | 0 | bit accuracy 0.785319 | 0/10 |
| Pulsar `native_official` | 0.5 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 0.75 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 1.25 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 1.5 | 0 | 10 | reveal failed | 0/10 |
| MDDM 128-byte `native_third_party` | 0.5 | 10 | 0 | bit accuracy 0.983398 | 0/10 |
| MDDM 128-byte `native_third_party` | 0.75 | 10 | 0 | bit accuracy 0.994336 | 2/10 |
| MDDM 128-byte `native_third_party` | 1.25 | 10 | 0 | bit accuracy 0.998145 | 4/10 |
| MDDM 128-byte `native_third_party` | 1.5 | 10 | 0 | bit accuracy 0.998145 | 4/10 |

## Pulsar Failure Interpretation

Pulsar completed generation and resize file handling for all four factors, but
all 40 attempts failed during native `reveal_with_regions`.

Observed failure pattern:

```text
stage: reveal_with_regions
error_type: ValueError
sample_dtype: uint8
```

This is counted as an attack result: under this unified image-domain resize
attack, the native Pulsar ECC/region reveal path did not decode any of the 10
pilot samples at any tested factor.

## Method Notes

- CRoSS: `scripts/run_cross_identity.py` now supports `--attack-kind resize`
  and records stego-vs-attacked image metrics.
- MAS/GRDH: `scripts/run_mas_grdh_identity.py` keeps the old native attack
  layer mode, but `--attack-kind resize` bypasses method-specific resize code
  and uses the shared image-domain attack.
- GSD: `scripts/run_gsd_identity.py` applies the shared resize to generated
  `[0,1]` image tensors before quantization and reverse recovery.
- Pulsar: `scripts/run_pulsar_identity.py` saves a sample, applies the shared
  file-level resize, reloads it, then calls native reveal.
- MDDM: `scripts/run_mddm_identity.py` passes a resized image override into the
  third-party decode service. This remains a pilot, not an official method.

## Not Included In This Pilot

- RGS: the official script can reveal attacked images only while the per-sample
  generated state remains in memory. It needs a dedicated attack branch in
  `hide_and_reveal.py` and is expensive at about 18 minutes per image on the
  current machine, so it is not included in this quick 10-sample unified pilot.
- Diffusion-Stego: the current workspace result is projection-only
  (`nsdser_reference`), not a complete generated-image reveal path, so a resize
  image attack would be misleading here.

## Verification

CSV integrity check:

```text
problems []
```

No duplicate sample IDs or incomplete row/failure totals were found across the
pilot result directories.
