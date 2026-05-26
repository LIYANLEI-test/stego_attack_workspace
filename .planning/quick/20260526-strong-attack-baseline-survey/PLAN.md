---
status: complete
created: 2026-05-26
completed: 2026-05-26T14:36:00+08:00
---

# Strong Attack Baseline Survey

Find a stronger published/open-source hidden-information destruction attack
baseline beyond resize/storage/JPEG/blur, integrate the best feasible candidate,
and run a 10-image smoke.

## Decision

Selected WatermarkAttacker Regen-VAE as the first stronger baseline candidate:

```text
attack label: regen_vae_watermarkattacker_adapted
paper: Invisible Image Watermarks Are Provably Removable Using Generative AI
venue: NeurIPS 2024
reference: https://github.com/XuandongZhao/WatermarkAttacker
```

Reasons:

- Directly targets invisible watermark removal.
- Official public code exists.
- The VAE/CompressAI path is feasible on the current 12 GB GPUs.
- It is detector-free and can be used as a black-box image transform before
  each native reveal/recovery path.

Second-stage candidate after cross-method Regen-VAE smoke: CtrlRegen
(`yepengliu/CtrlRegen`, ICLR 2025), which is newer but heavier because it
requires diffusion/control model plumbing.

## Execution

- Added `references/WatermarkAttacker` as a pinned submodule.
- Added `scripts/regen_attack.py` for size-preserving Regen-VAE transforms.
- Added `--attack-kind regen_vae` support to the GSD runner.
- Added generic `regen_vae` attack support to `attack_common.py` and runner
  choices for CRoSS, MAS/GRDH, MDDM, and Pulsar for follow-on smoke tests.
- Ran GSD CIFAR10 10-sample smoke with `bmshj2018-factorized` quality 3.

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/regen_vae_smoke_20260526/gsd_cifar10_bmshj2018_factorized_q3_10
```

## Result

| Method | Attack | Rows | Failures | Main metric |
|--------|--------|------|----------|-------------|
| GSD CIFAR10 | Regen-VAE `bmshj2018-factorized` q=3 | 10 | 0 | mean bit accuracy 0.524089, BER 0.475911 |

Saved attacked-image quality:

```text
mean stego-vs-attacked PSNR: 25.176627 dB
mean stego-vs-attacked MAE: 10.614681
mean runtime: 33.58 s/sample
```

## Caveats

- This is a 10-sample smoke, not the final paper table.
- The local adapter preserves native image size instead of forcing the official
  demo's 512x512 resize, so label it as adapted.
- Strong payload destruction comes with visible perturbation on 32x32 samples;
  report image quality alongside recovery degradation.
