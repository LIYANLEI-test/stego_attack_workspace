# SCAD-Lite 10-Sample Pilot - 2026-06-05

## Scope

This pilot tests the first lightweight implementation of the proposed
Stego-Carrier Adversarial Diffusion Sanitization idea.

Prototype name in code:

```text
attack_kind=scad
attack_factor=30
```

Implementation status:

- This is `SCAD-lite`, not the full diffusion-resynthesis method.
- It estimates a carrier mask from self-canonicalization residuals, perturbs
  the estimated carrier subspace, and binary-searches perturbation strength to
  target stego-vs-attacked PSNR 30 dB.
- It does not yet use a diffusion or VAE residual resynthesis stage.

Run root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/scad_lite_10_20260605
```

Methods:

```text
GSD CIFAR10, MAS/GRDH, MDDM-128 pilot, Pulsar region/ECC
```

## Results

| Method | Records | Failures | Bit accuracy | BER / destruction | PSNR | LPIPS |
|---|---:|---:|---:|---:|---:|---:|
| GSD CIFAR10 | 10 | 0 | 0.6974 | 0.3026 | 29.9997 | 0.0522 |
| MAS/GRDH | 10 | 0 | 0.8856 | 0.1144 | 29.9675 | 0.1055 |
| MDDM-128 pilot | 10 | 0 | 0.9752 | 0.0248 | 30.0000 | 0.1888 |
| Pulsar | 0 | 10 | 0.0000 | 1.0000 | 30.0000 | 0.3916 |

Pulsar rows are native reveal failures after saved attacked images were
produced, so they are counted as complete payload-recovery failures under the
workspace scoring convention.

## Interpretation

- The PSNR controller works: all methods land at approximately 30 dB.
- GSD damage is moderate: BER about 0.303, comparable to median blur at the
  PSNR-30 point, but weaker than the current Regen-VAE/JPEG target-PSNR
  candidates.
- MAS/GRDH damage is modest: BER about 0.114.
- MDDM pilot remains highly robust to this first SCAD-lite prototype.
- Pulsar is fully broken, but LPIPS is too high, so this is not yet a clean
  paper-quality Pulsar result.

Current conclusion:

```text
SCAD-lite is a useful mechanism smoke test, but not yet SOTA.
The next version needs diffusion/VAE residual resynthesis or a smoother
carrier transport step to lower LPIPS while keeping BER high.
```

## Artifacts

```text
scripts/attack_common.py
/data2/liyanlei/stego_attack_data/attack_runs/scad_lite_10_20260605/scad_lite_summary.csv
/data2/liyanlei/stego_attack_data/attack_runs/scad_lite_10_20260605/logs/scad_queue_driver.log
/data2/liyanlei/stego_attack_data/attack_runs/scad_lite_10_20260605/logs/mas_grdh_scad_30_10_rerun.log
```

## Verification

```text
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python -m py_compile scripts/attack_common.py scripts/run_quality_budget_attacks.py scripts/select_quality_budget_attacks.py scripts/run_gsd_identity.py scripts/run_mas_grdh_identity.py scripts/run_mddm_identity.py scripts/run_pulsar_identity.py
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python -m unittest discover -s tests -v
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH python scripts/select_quality_budget_attacks.py /data2/liyanlei/stego_attack_data/attack_runs/scad_lite_10_20260605 --device cpu --output /data2/liyanlei/stego_attack_data/attack_runs/scad_lite_10_20260605/scad_lite_summary.csv
```
