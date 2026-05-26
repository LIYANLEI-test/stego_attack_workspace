---
status: complete
created: 2026-05-26
completed: 2026-05-26T14:36:00+08:00
---

# Summary

Found and integrated a stronger attack baseline candidate:
`regen_vae_watermarkattacker_adapted`, based on the official
`XuandongZhao/WatermarkAttacker` code for the NeurIPS 2024 paper *Invisible
Image Watermarks Are Provably Removable Using Generative AI*.

The implementation adds a size-preserving CompressAI Regen-VAE adapter and
enables `--attack-kind regen_vae`. GSD CIFAR10 10-sample smoke completed 10/10
with 0 failures. Mean bit accuracy was 0.524089, BER was 0.475911, mean
stego-vs-attacked PSNR was 25.176627 dB, and mean runtime was 33.58 s/sample.

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/regen_vae_smoke_20260526/gsd_cifar10_bmshj2018_factorized_q3_10
```

Docs:

```text
docs/strong_attack_baseline_survey_20260526.md
```
