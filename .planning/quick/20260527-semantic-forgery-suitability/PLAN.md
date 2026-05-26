---
status: complete
created: 2026-05-27
completed: 2026-05-27T00:00:00+08:00
---

# Semantic Forgery Suitability Check

Assess whether `and-mill/semantic-forgery` is suitable as a hidden-information
destruction baseline, and run 10 samples only if it matches the current attack
protocol.

## Finding

`semantic-forgery` is strong related work, but it is not a good current baseline
for this workspace.

The method targets semantic watermarks for diffusion models, specifically
Tree-Ring and Gaussian Shading. Its native scripts generate or verify those
semantic-watermarked images and optimize against their semantic watermark
detectors. They do not expose a method-native, detector-independent transform
that takes one of our arbitrary stego images and returns a content-preserving
attacked image for native reveal.

## Decision

Do not run the 10-image smoke and do not include it in the current attack
matrix. Keep it as related work / future candidate if semantic watermarking
baselines are added.

Documentation:

```text
docs/semantic_forgery_suitability_20260527.md
```
