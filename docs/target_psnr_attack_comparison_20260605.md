# Target-PSNR Attack Comparison - 2026-06-05

## Scope

This report reuses the existing 10-sample calibration grid:

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary.csv
```

New comparison rule:

```text
target stego-vs-attacked PSNR = 30 dB
tolerance flag = +/- 1 dB
LPIPS is reported, not filtered
```

For each target steganography method and attack family, the selected parameter
is the candidate whose mean stego-vs-attacked PSNR is closest to 30 dB. If two
candidates are equally close, the one with stronger message degradation is
preferred.

For bit-payload methods, the destruction rate is:

```text
bit_destruction_rate = BER = 1 - bit_accuracy
```

For Pulsar region/ECC, a saved attacked image followed by native reveal failure
is scored as complete payload destruction and is also reported with
`reveal_failure_rate`. For CRoSS, the payload is an image, so the main recovery
metric remains recovered-secret PSNR rather than BER.

## Bit-Payload Attack Summary

This table excludes Pulsar from the average because Pulsar currently returns
native reveal failures for all selected attacks, which would dominate the mean
and hide the ordinary bit-decoding behavior of GSD, MAS/GRDH, and MDDM pilot.

| Attack | Targets | Mean PSNR | Mean PSNR gap | Mean LPIPS | Mean BER / destruction |
|---|---:|---:|---:|---:|---:|
| Regen-VAE | 3 | 29.814 | 0.556 | 0.1751 | 0.2259 |
| JPEG | 3 | 30.673 | 0.698 | 0.0736 | 0.2050 |
| Median blur | 3 | 30.428 | 0.655 | 0.1223 | 0.1315 |
| Gaussian blur | 3 | 29.475 | 0.583 | 0.1896 | 0.1021 |
| Resize | 3 | 30.336 | 1.155 | 0.1865 | 0.0966 |
| UnMarker | 1 | 45.132 | 15.132 | 0.0006 | 0.2340 |

Current interpretation:

- Regen-VAE is the strongest non-Pulsar averaged attack at PSNR about 30, but
  LPIPS is high.
- JPEG is nearly as destructive on average and has the best LPIPS among the
  comparable multi-target attacks.
- Resize is not competitive at this equal-PSNR point, despite being a strong
  simple baseline in some individual targets.
- UnMarker is not yet comparable because the current smoke profile stays at
  PSNR about 45 dB; it needs tuning to the 30 dB quality point or should remain
  a candidate-only result.

## Including Pulsar

| Attack | Targets | Mean PSNR | Mean PSNR gap | Mean LPIPS | Mean BER / destruction | Mean reveal failure |
|---|---:|---:|---:|---:|---:|---:|
| Regen-VAE | 4 | 30.556 | 1.113 | 0.1772 | 0.4194 | 0.2500 |
| JPEG | 4 | 32.712 | 2.730 | 0.0624 | 0.4037 | 0.2500 |
| Median blur | 4 | 31.422 | 1.593 | 0.1271 | 0.3486 | 0.2500 |
| Gaussian blur | 4 | 31.122 | 1.954 | 0.1843 | 0.3266 | 0.2500 |
| Resize | 4 | 32.002 | 2.616 | 0.1707 | 0.3224 | 0.2500 |
| UnMarker | 1 | 45.132 | 15.132 | 0.0006 | 0.2340 | 0.0000 |

Pulsar-specific caveat: the closest available Pulsar candidates are still above
the 30 dB target for most attack families:

| Attack | Param | PSNR | LPIPS | Reveal failure |
|---|---:|---:|---:|---:|
| Regen-VAE | q=1 | 32.783 | 0.1835 | 10/10 |
| Median blur | k=7 | 34.406 | 0.1417 | 10/10 |
| Gaussian blur | k=7 | 36.065 | 0.1684 | 10/10 |
| Resize | 0.5 | 36.999 | 0.1233 | 10/10 |
| JPEG | q=50 | 38.829 | 0.0289 | 10/10 |

This means Pulsar is already fully broken by the current candidates, but a
stricter equal-PSNR-30 table would need a harsher or finer Pulsar grid if the
paper requires every row to sit near 30 dB.

## CRoSS Image-Payload Target

CRoSS carries an image payload, so lower recovered-secret PSNR means stronger
payload degradation. Exact-match failure is not a useful main metric because
CRoSS native identity recovery is not pixel-exact.

| Attack | Param | Stego PSNR | LPIPS | Recovered-secret PSNR |
|---|---:|---:|---:|---:|
| Regen-VAE | q=2 | 30.084 | 0.1935 | 16.453 |
| Gaussian blur | k=7 | 29.369 | 0.2271 | 17.781 |
| Resize | 0.5 | 30.043 | 0.1792 | 18.619 |
| JPEG | q=50 | 33.355 | 0.0574 | 19.245 |
| Median blur | k=5 | 29.280 | 0.1670 | 19.752 |

At the target-PSNR point, Regen-VAE is strongest for CRoSS but has high LPIPS.
JPEG has much lower LPIPS but its PSNR is about 33.4 dB rather than close to
30 dB in the existing grid.

## Artifacts

```text
scripts/select_target_psnr_attacks.py
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_selection.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_attack_summary_bit_methods.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_attack_summary_bit_methods_no_pulsar.csv
```

## Verification

```text
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python -m py_compile scripts/select_target_psnr_attacks.py
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python -m unittest discover -s tests -v
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python scripts/select_target_psnr_attacks.py /data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary.csv --target-psnr 30 --tolerance 1 --output /data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_selection.csv --attack-summary-output /data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/target_psnr_30_attack_summary_bit_methods.csv
```
