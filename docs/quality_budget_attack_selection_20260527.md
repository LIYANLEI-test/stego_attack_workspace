# Quality-Budget Attack Selection - 2026-05-27

## Scope

This calibration selects attack parameters under a shared stego-vs-attacked
image-quality budget, using 10 samples per method/factor.

Output root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527
```

Budget:

```text
stego-vs-attacked PSNR >= 30 dB
stego-vs-attacked LPIPS <= 0.10
```

The thresholds are intentionally conservative for the paper comparison. PSNR
30 dB is a common lower bound for mild visible distortion, while LPIPS 0.10 is
a perceptual ceiling that rejects attacks that change image content too much.
Both metrics are required for parameter selection and are computed between the
generated stego image and its attacked version, not against the original
cover/secret. LPIPS uses the Alex backbone;
tiny CIFAR-scale images are upsampled to 64x64 only for LPIPS ranking.

## Candidate Grid

```text
resize factor: 0.5, 0.75, 1.25, 1.5
JPEG quality: 95, 90, 80, 70, 50
median blur kernel: 3, 5, 7
Gaussian blur kernel: 3, 5, 7
Regen-VAE quality: 6, 5, 4, 3, 2, 1
UnMarker: high-frequency smoke profile, 25 iterations, GSD only
```

The selection rule is per method and attack family: among parameters inside the
quality budget, choose the strongest message-destruction setting. For bit
payload methods, lower bit accuracy is stronger. For image payload methods,
lower recovered-secret PSNR is stronger. If native recovery fails after the
attacked image is saved, the sample is counted as complete payload-recovery
failure while still using the saved stego/attacked images for PSNR and LPIPS.
Failures without a saved measurable attacked pair are not scoreable attack
outcomes and cannot qualify a setting for selection.

Storage/PNG round trip is treated as a control rather than a destructive
attack candidate, so it is not selected here.

## Selected Parameters

| Method | Attack | Selected parameter | Recovery metric | Stego-vs-attacked PSNR | LPIPS | Rows / failures |
|--------|--------|--------------------|-----------------|------------------------|-------|-----------------|
| CRoSS `native_official` | Gaussian blur | kernel 3 | recovery PSNR 19.715908 dB | 33.840 dB | 0.0861 | 10 / 0 |
| CRoSS `native_official` | JPEG | quality 50 | recovery PSNR 19.244603 dB | 33.355 dB | 0.0574 | 10 / 0 |
| CRoSS `native_official` | Median blur | kernel 3 | recovery PSNR 19.344630 dB | 33.194 dB | 0.0689 | 10 / 0 |
| CRoSS `native_official` | Regen-VAE | quality 5 | recovery PSNR 17.101117 dB | 34.569 dB | 0.0780 | 10 / 0 |
| CRoSS `native_official` | Resize | factor 1.5 | recovery PSNR 19.920919 dB | 36.343 dB | 0.0451 | 10 / 0 |
| GSD CIFAR10 `native_official` | JPEG | quality 80 | bit accuracy 0.586784 | 31.384 dB | 0.0424 | 10 / 0 |
| GSD CIFAR10 `native_official` | Regen-VAE | quality 6 | bit accuracy 0.580794 | 31.794 dB | 0.0362 | 10 / 0 |
| GSD CIFAR10 `native_official` | Resize | factor 1.25 | bit accuracy 0.781608 | 30.801 dB | 0.0803 | 10 / 0 |
| GSD CIFAR10 `native_official` | UnMarker | high smoke, 25 iter | bit accuracy 0.766016 | 45.132 dB | 0.0006 | 10 / 0 |
| MAS/GRDH `native_official` | JPEG | quality 50 | bit accuracy 0.843793 | 30.638 dB | 0.0579 | 10 / 0 |
| MAS/GRDH `native_official` | Regen-VAE | quality 6 | bit accuracy 0.881555 | 33.479 dB | 0.0694 | 10 / 0 |
| MAS/GRDH `native_official` | Resize | factor 1.5 | bit accuracy 0.941510 | 31.560 dB | 0.0878 | 10 / 0 |
| MDDM 128-byte `native_third_party` | JPEG | quality 70 | bit accuracy 0.987695 | 32.989 dB | 0.0580 | 10 / 0 |
| Pulsar `native_official` | Gaussian blur | kernel 3 | bit accuracy 0.000000 | 42.475 dB | 0.0489 | 0 / 10 |
| Pulsar `native_official` | JPEG | quality 95 | bit accuracy 0.000000 | 47.753 dB | 0.0025 | 0 / 10 |
| Pulsar `native_official` | Median blur | kernel 3 | bit accuracy 0.000000 | 43.114 dB | 0.0229 | 0 / 10 |
| Pulsar `native_official` | Regen-VAE | quality 6 | bit accuracy 0.000000 | 41.424 dB | 0.0318 | 0 / 10 |
| Pulsar `native_official` | Resize | factor 1.25 | bit accuracy 0.000000 | 45.542 dB | 0.0221 | 0 / 10 |

## Budget Coverage

| Method | Attack | In-budget settings |
|--------|--------|--------------------|
| CRoSS | Resize | 3 / 4 |
| CRoSS | JPEG | 5 / 5 |
| CRoSS | Median blur | 1 / 3 |
| CRoSS | Gaussian blur | 1 / 3 |
| CRoSS | Regen-VAE | 2 / 6 |
| GSD CIFAR10 | Resize | 2 / 4 |
| GSD CIFAR10 | JPEG | 3 / 5 |
| GSD CIFAR10 | Median blur | 0 / 3 |
| GSD CIFAR10 | Gaussian blur | 0 / 3 |
| GSD CIFAR10 | Regen-VAE | 1 / 6 |
| GSD CIFAR10 | UnMarker | 1 / 1 |
| MAS/GRDH | Resize | 2 / 4 |
| MAS/GRDH | JPEG | 5 / 5 |
| MAS/GRDH | Median blur | 0 / 3 |
| MAS/GRDH | Gaussian blur | 0 / 3 |
| MAS/GRDH | Regen-VAE | 1 / 6 |
| MDDM 128-byte pilot | Resize | 0 / 4 |
| MDDM 128-byte pilot | JPEG | 4 / 5 |
| MDDM 128-byte pilot | Median blur | 0 / 3 |
| MDDM 128-byte pilot | Gaussian blur | 0 / 3 |
| MDDM 128-byte pilot | Regen-VAE | 0 / 6 |
| Pulsar | Resize | 3 / 4 |
| Pulsar | JPEG | 5 / 5 |
| Pulsar | Median blur | 2 / 3 |
| Pulsar | Gaussian blur | 2 / 3 |
| Pulsar | Regen-VAE | 3 / 6 |

## Notes

- Pulsar selected attacks all produced native `reveal_with_regions` failures on
  these 10 samples. This is counted as complete payload destruction, not as a
  missing measurement, because the attacked images are saved and remain within
  the image-quality budget.
- For Pulsar, ties at bit accuracy 0 are broken by higher image quality. That
  is why JPEG quality 95 is selected instead of a harsher JPEG setting.
- MDDM remains a `native_third_party` 128-byte pilot. It is useful for local
  calibration but should not be described as an official baseline.
- RGS is excluded from this calibration per the runtime decision to skip RGS
  attacks for now. Diffusion-Stego has since been removed from the active
  project because the old path was projection-only, not full image
  generation/reveal.
- UnMarker is currently integrated only for GSD. It is an adapted attack-method
  candidate, not a hiding/steganography baseline and not a full paper
  reproduction.
- These are 10-sample calibration choices on sample indices `0-9`. Final paper
  tables rerun the selected parameters across the deterministic raw set but
  exclude `0-9` from formal estimates to prevent parameter-selection leakage.
  The fixed held-out counts are CRoSS `90`, GSD/MAS/GRDH/Pulsar `490`, and
  MDDM pilot `40`.

## Artifacts

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary_selected.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/logs/cross_quality_driver.log
```

## Verification

Commands run:

```text
python -m py_compile scripts/run_pulsar_identity.py scripts/select_quality_budget_attacks.py scripts/run_quality_budget_attacks.py scripts/identity_common.py scripts/run_gsd_identity.py scripts/run_mas_grdh_identity.py
git diff --check
```

Selector output:

```text
summaries: 106
selected rows: 18
budget: PSNR >= 30 dB, LPIPS <= 0.10
```
