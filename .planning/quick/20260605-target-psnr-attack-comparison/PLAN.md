---
status: complete
created: 2026-06-05
---

# Target-PSNR Attack Comparison

Reframe the current 10-sample attack-method comparison so that each
method/attack parameter is selected by closeness to mean stego-vs-attacked PSNR
30 dB, then compare payload destruction and LPIPS.

Scope:

- Reuse the existing quality-budget calibration CSV; do not launch any new
  formal queue.
- Add an explicit selector for target-PSNR comparison rather than replacing the
  existing `PSNR >= 30, LPIPS <= 0.10` strongest-in-budget selector.
- Report bit-payload destruction as BER (`1 - bit_accuracy`) and keep CRoSS
  image-payload recovery as recovered-secret PSNR.
- Preserve Pulsar reveal failures as a separate rate because they dominate
  cross-target bit averages.
