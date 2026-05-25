# Unified JPEG And Blur Attack Pilots - 2026-05-26

## Scope

This pilot completes the non-RGS image-domain attack queue after the resize and
storage pilots.

Attack families and factors follow the MAS/GRDH README robustness scenarios:

```text
JPEG compression: quality 90, 70, 50
Median blur: kernel 3, 5, 7
Gaussian blur: kernel 3, 5, 7
samples: 0-9 per method/factor
```

The attack is inserted after each method generates the stego image and before
its native reveal/recovery path. Embedding, sampling, decoding, and payload
generation remain method-native.

Output root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unified_image_attacks_20260526
```

## JPEG Results

| Method | Factor | Rows | Failures | Main metric | Exact |
|--------|--------|------|----------|-------------|-------|
| CRoSS `native_official` | 90 | 10 | 0 | recovery PSNR 20.209000 dB | 0/10 |
| CRoSS `native_official` | 70 | 10 | 0 | recovery PSNR 20.044553 dB | 0/10 |
| CRoSS `native_official` | 50 | 10 | 0 | recovery PSNR 19.244603 dB | 0/10 |
| MAS/GRDH `native_official` | 90 | 10 | 0 | bit accuracy 0.926306 | 0/10 |
| MAS/GRDH `native_official` | 70 | 10 | 0 | bit accuracy 0.882642 | 0/10 |
| MAS/GRDH `native_official` | 50 | 10 | 0 | bit accuracy 0.843793 | 0/10 |
| GSD CIFAR10 `native_official` | 90 | 10 | 0 | bit accuracy 0.608561 | 0/10 |
| GSD CIFAR10 `native_official` | 70 | 10 | 0 | bit accuracy 0.567969 | 0/10 |
| GSD CIFAR10 `native_official` | 50 | 10 | 0 | bit accuracy 0.566764 | 0/10 |
| Pulsar `native_official` | 90 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 70 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 50 | 0 | 10 | reveal failed | 0/10 |
| MDDM 128-byte `native_third_party` | 90 | 10 | 0 | bit accuracy 0.996680 | 2/10 |
| MDDM 128-byte `native_third_party` | 70 | 10 | 0 | bit accuracy 0.987695 | 2/10 |
| MDDM 128-byte `native_third_party` | 50 | 10 | 0 | bit accuracy 0.973340 | 0/10 |

## Median Blur Results

| Method | Factor | Rows | Failures | Main metric | Exact |
|--------|--------|------|----------|-------------|-------|
| CRoSS `native_official` | 3 | 10 | 0 | recovery PSNR 19.344630 dB | 0/10 |
| CRoSS `native_official` | 5 | 10 | 0 | recovery PSNR 19.751744 dB | 0/10 |
| CRoSS `native_official` | 7 | 10 | 0 | recovery PSNR 18.835050 dB | 0/10 |
| MAS/GRDH `native_official` | 3 | 10 | 0 | bit accuracy 0.894745 | 0/10 |
| MAS/GRDH `native_official` | 5 | 10 | 0 | bit accuracy 0.811877 | 0/10 |
| MAS/GRDH `native_official` | 7 | 10 | 0 | bit accuracy 0.748199 | 0/10 |
| GSD CIFAR10 `native_official` | 3 | 10 | 0 | bit accuracy 0.626367 | 0/10 |
| GSD CIFAR10 `native_official` | 5 | 10 | 0 | bit accuracy 0.548665 | 0/10 |
| GSD CIFAR10 `native_official` | 7 | 10 | 0 | bit accuracy 0.528385 | 0/10 |
| Pulsar `native_official` | 3 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 5 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 7 | 0 | 10 | reveal failed | 0/10 |
| MDDM 128-byte `native_third_party` | 3 | 10 | 0 | bit accuracy 0.986719 | 1/10 |
| MDDM 128-byte `native_third_party` | 5 | 10 | 0 | bit accuracy 0.961523 | 0/10 |
| MDDM 128-byte `native_third_party` | 7 | 10 | 0 | bit accuracy 0.933496 | 0/10 |

## Gaussian Blur Results

| Method | Factor | Rows | Failures | Main metric | Exact |
|--------|--------|------|----------|-------------|-------|
| CRoSS `native_official` | 3 | 10 | 0 | recovery PSNR 19.715908 dB | 0/10 |
| CRoSS `native_official` | 5 | 10 | 0 | recovery PSNR 18.680440 dB | 0/10 |
| CRoSS `native_official` | 7 | 10 | 0 | recovery PSNR 17.780781 dB | 0/10 |
| MAS/GRDH `native_official` | 3 | 10 | 0 | bit accuracy 0.927435 | 0/10 |
| MAS/GRDH `native_official` | 5 | 10 | 0 | bit accuracy 0.902606 | 0/10 |
| MAS/GRDH `native_official` | 7 | 10 | 0 | bit accuracy 0.862689 | 0/10 |
| GSD CIFAR10 `native_official` | 3 | 10 | 0 | bit accuracy 0.701009 | 0/10 |
| GSD CIFAR10 `native_official` | 5 | 10 | 0 | bit accuracy 0.637858 | 0/10 |
| GSD CIFAR10 `native_official` | 7 | 10 | 0 | bit accuracy 0.590918 | 0/10 |
| Pulsar `native_official` | 3 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 5 | 0 | 10 | reveal failed | 0/10 |
| Pulsar `native_official` | 7 | 0 | 10 | reveal failed | 0/10 |
| MDDM 128-byte `native_third_party` | 3 | 10 | 0 | bit accuracy 0.994238 | 2/10 |
| MDDM 128-byte `native_third_party` | 5 | 10 | 0 | bit accuracy 0.987891 | 1/10 |
| MDDM 128-byte `native_third_party` | 7 | 10 | 0 | bit accuracy 0.979004 | 0/10 |

## Method Notes

- CRoSS reports recovered-secret PSNR. It completed all 9 JPEG/blur settings
  with 10 result rows and 0 failures per setting.
- MAS/GRDH, GSD, and MDDM report bit accuracy. They completed all 9 settings
  with 10 result rows and 0 failures per setting.
- Pulsar completed generation and attacked-image handling for every lossy
  setting, but native `reveal_with_regions` failed for all 90 attacked samples.
  This mirrors the resize pilot pattern and is counted as an attack outcome.
- MDDM remains a `native_third_party` 128-byte pilot, not an official baseline.
- RGS was not attacked in this sweep. Its identity run completed separately at
  100/100 rows, 0 failures, mean recovery PSNR 23.316454 dB.

## Verification

CSV integrity check:

```text
dirs 45
problems []
```

All 45 method/factor directories have exactly 10 total records across result
and failure CSVs, with no duplicate sample IDs.
