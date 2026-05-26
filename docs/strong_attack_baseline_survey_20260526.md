# Strong Attack Baseline Survey - 2026-05-26

## Goal

The resize/storage/JPEG/blur pilots are useful sanity checks, but they are too
generic to carry a paper comparison by themselves. This survey looked for
published, open-source image-domain attacks that are closer to the real problem:
destroying invisible watermark or hidden payload signals while preserving the
visible image enough to remain a plausible post-processing attack.

## Candidate Ranking

| Candidate | Venue/status | Fit for this workspace | Decision |
|-----------|--------------|------------------------|----------|
| WatermarkAttacker / Regen-VAE | NeurIPS 2024, official public code | Directly targets invisible watermark removal using regeneration. The VAE path is light enough for 12 GB GPUs and does not require a watermark detector. | Integrated first |
| UnMarker | IEEE S&P 2025, official public code | Recent detector-feedback-free watermark attack, already smoke-tested through an adapted core. | Keep as attack candidate |
| CtrlRegen | ICLR 2025, official public code | Potentially strong and newer, but much heavier because it needs diffusion/control pipelines and control checkpoints. | Second-stage candidate |
| Watermark transfer/surrogate-detector attacks | ICLR 2025, official public code | Strong for detector evasion, but depends on surrogate watermark detectors and is less direct for native stego payload recovery across our heterogeneous methods. | Do not prioritize now |
| Steganalysis/population attacks | Various | Usually require clean/stego paired populations or detectors, not a drop-in image transform before native reveal. | Not immediate |

## Selected Method

Selected attack label:

```text
regen_vae_watermarkattacker_adapted
```

Reference checkout:

```text
references/WatermarkAttacker
https://github.com/XuandongZhao/WatermarkAttacker
commit 2637dd2c3b84a3037dd3940b401090e8bcebe1f6
```

Paper:

```text
Invisible Image Watermarks Are Provably Removable Using Generative AI
NeurIPS 2024
```

The original repository's `VAEWMAttacker` uses CompressAI learned compression
models and notes that lower quality values create stronger removal pressure. The
local adapter calls the same CompressAI model family, but preserves the native
image size instead of forcing the repository demo's 512x512 resize. This keeps
the attack variable focused on learned compression/regeneration when testing
GSD CIFAR10 32x32 samples.

## Local Integration

New adapter:

```text
scripts/regen_attack.py
```

Runner support:

```text
scripts/run_gsd_identity.py --attack-kind regen_vae --regen-model bmshj2018-factorized --regen-quality 3
```

The generic attack helper also accepts `regen_vae` through `attack_factor` as
the quality value, defaulting to quality 3 when omitted. CRoSS, MAS/GRDH, MDDM,
and Pulsar runner choices now include `regen_vae` so method-specific smoke tests
can be run next. GSD has explicit `--regen-*` flags because it was the first
end-to-end smoke target.

## GSD CIFAR10 Smoke

Command:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  HF_HOME=/data2/liyanlei/huggingface TORCH_HOME=/data2/liyanlei/torch \
  CUDA_VISIBLE_DEVICES=0 \
  /data2/liyanlei/envs/stego_attack/bin/python scripts/run_gsd_identity.py \
  --count 10 \
  --timesteps 1000 \
  --device cuda \
  --attack-kind regen_vae \
  --regen-model bmshj2018-factorized \
  --regen-quality 3 \
  --save-images \
  --force \
  --output-dir /data2/liyanlei/stego_attack_data/attack_runs/regen_vae_smoke_20260526/gsd_cifar10_bmshj2018_factorized_q3_10
```

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/regen_vae_smoke_20260526/gsd_cifar10_bmshj2018_factorized_q3_10
```

## Result Summary

| Method | Attack | Rows | Failures | Main metric | Runtime |
|--------|--------|------|----------|-------------|---------|
| GSD CIFAR10 `native_official` | Regen-VAE `bmshj2018-factorized` quality 3 | 10 | 0 | mean bit accuracy 0.524089, BER 0.475911 | mean 33.58 s/sample |

Additional image perturbation metrics over saved stego/attacked pairs:

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| stego-vs-attacked PSNR | 25.176627 dB | 22.960160 dB | 27.492785 dB |
| stego-vs-attacked MAE | 10.614681 | 8.286458 | 13.666667 |
| stego-vs-attacked MSE | 207.837272 | 115.824867 | 328.900391 |

Per-sample bit accuracy range:

```text
min 0.511719, max 0.547526, exact 0/10
```

For context, the formal GSD CIFAR10 identity mean bit accuracy is about 0.874.
This smoke pushes recovery close to random guessing on 10 samples, so it is a
much stronger destruction baseline than resize/storage/JPEG/blur for GSD.

## Interpretation

Regen-VAE is a strong attack baseline candidate and should be included in the
next attack matrix before resuming large sweeps. It has a clear paper pedigree
and a stronger degradation signal than the simple image transforms. The tradeoff
is visible image distortion on small 32x32 outputs: PSNR around 25 dB is much
lower than the UnMarker smoke's 45 dB, so tables should report both payload
destruction and stego-vs-attacked image quality.

Recommended next attack settings:

```text
regen_vae bmshj2018-factorized q=3 as the first unified setting
regen_vae bmshj2018-factorized q=1 as a stronger stress setting if q=3 is not destructive enough on larger methods
unmarker_core_adapted as a complementary high-PSNR attack candidate
```

Second-stage candidate:

```text
CtrlRegen / yepengliu/CtrlRegen, ICLR 2025
```

Do not present this as a full reproduction of WatermarkAttacker; present it as
an adapted attack baseline using the official method family and public reference
checkout.
