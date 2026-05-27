---
status: complete
created: 2026-05-28
completed: 2026-05-28T00:00:00+08:00
---

# Summary

Ran the requested 10-sample Pulsar precision controls.

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_10_precision_controls_20260528
```

Summary artifacts:

```text
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_10_precision_controls_20260528/pulsar_10_precision_control_summary.csv
/data2/liyanlei/stego_attack_data/attack_runs/pulsar_10_precision_controls_20260528/pulsar_10_precision_control_summary.md
```

Results:

| Control | Records | Result rows | Reveal failures | Positive-payload failure rate | PSNR | LPIPS |
|---------|---------|-------------|-----------------|-------------------------------|------|-------|
| storage uint16 | 10 | 10 | 0 | 0/10 | inf | 0.000000 |
| storage uint8 | 10 | 0 | 10 | 10/10 | inf | 0.000000 |
| resize 1.25 uint16-preserving | 10 | 0 | 10 | 10/10 | 46.719224 | 0.015046 |
| median blur 3 uint16-preserving | 10 | 0 | 10 | 10/10 | 43.080436 | 0.022913 |
| Gaussian blur 3 uint16-preserving | 10 | 0 | 10 | 10/10 | 42.363897 | 0.049013 |

Interpretation:

- Native 16-bit PNG storage is lossless for this Pulsar recovery path.
- 8-bit storage alone breaks all 10 positive-payload samples.
- Resize and blur still break all 10 positive-payload samples even when the
  attack is applied in a 16-bit-preserving path.
- Therefore the previous Pulsar fragility is not only a `uint8` conversion
  artifact, although `uint8` conversion is itself sufficient to break the
  current Pulsar setup.

Implementation note:

- `scripts/run_pulsar_identity.py` now has `--preserve-sample-dtype-attack`.
  The default attack path is unchanged; the new flag applies resize/blur
  directly to the saved PNG bit depth for Pulsar controls.
