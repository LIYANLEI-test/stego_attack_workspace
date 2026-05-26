# Semantic Forgery Suitability Check - 2026-05-27

## Candidate

Repository:

```text
https://github.com/and-mill/semantic-forgery
commit ca68950cd7b53b8438a49580f134b2a0db28d778
```

Paper:

```text
Black-Box Forgery Attacks on Semantic Watermarks for Diffusion Models
CVPR 2025 Oral
```

## Decision

Do **not** include `semantic-forgery` as a current steganographic information
destruction baseline.

It is relevant related work, but its attack target and evaluation contract do
not match this workspace's current comparison protocol.

## Why It Is Not A Drop-In Baseline

The repository attacks semantic watermarks for diffusion models, specifically
Tree-Ring and Gaussian Shading. These watermarks are embedded by preparing the
initial latent input and verified through inversion. The workspace methods under
test are heterogeneous generative steganography systems with native payload
recovery paths.

The provided scripts are not generic transforms of an arbitrary stego image:

- `run_imprint_forgery.py` transfers a semantic watermark imprint from a
  target watermarked reference to a cover image.
- `run_imprint_removal.py` first generates a Tree-Ring/Gaussian-Shading
  watermarked target image, then optimizes that image to evade the semantic
  watermark verifier.
- `run_reprompting.py` inverts and regenerates a target image with a different
  prompt, which changes semantic content and is not a fair same-quality-budget
  perturbation for hidden-message recovery.

Because our GSD, MAS/GRDH, Pulsar, CRoSS, MDDM, and RGS artifacts are not
Tree-Ring/Gaussian-Shading semantic-watermarked images, the repository's
success criterion would not measure whether our native hidden payload survived.
Adapting the optimization objective to arbitrary stego images would create a
new variant rather than using the paper's native attack semantics.

## Practical Fit

The README reports testing on an A40 with 45 GB VRAM. The current machine has
12 GB GPUs. Some paths may run with smaller models, but full imprinting attacks
are expected to be expensive, and Reprompting is not content-preserving enough
for the planned quality-budget comparison.

## Status

Label for future notes:

```text
semantic_forgery_related_work_not_baseline
```

Revisit only if the project adds semantic watermarking baselines such as
Tree-Ring or Gaussian Shading, or if a separate experiment studies semantic
watermark attribution rather than steganographic payload destruction.
