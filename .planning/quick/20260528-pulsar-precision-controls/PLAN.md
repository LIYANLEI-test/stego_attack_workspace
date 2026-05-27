---
status: complete
created: 2026-05-28
completed: 2026-05-28T00:00:00+08:00
---

# Pulsar Precision Controls

Run 10-sample Pulsar controls to separate native 16-bit storage, 8-bit
quantization, and 16-bit-preserving image-domain perturbations.

## Scope

- Method: Pulsar only.
- Count: 10 samples per control.
- Controls:
  - storage with native `uint16` PNG.
  - storage with `uint8` PNG.
  - resize 1.25 preserving `uint16` PNG bit depth.
  - median blur kernel 3 preserving `uint16` PNG bit depth.
  - Gaussian blur kernel 3 preserving `uint16` PNG bit depth.
- Output root:
  `/data2/liyanlei/stego_attack_data/attack_runs/pulsar_10_precision_controls_20260528`.

## Acceptance

- Confirm whether `uint8` quantization alone breaks Pulsar reveal.
- Confirm whether resize/blur still break Pulsar when avoiding the old RGB
  `uint8` attack path.
- Keep the run limited to 10 samples and Pulsar only.
