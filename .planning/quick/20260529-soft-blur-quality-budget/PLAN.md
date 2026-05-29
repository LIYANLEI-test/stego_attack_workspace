---
status: complete
created: 2026-05-29
---

# Soft Blur Quality-Budget Extension

Add weaker blur amplitudes for methods whose minimum kernel-3 median/Gaussian
blur exceeded the shared quality budget.

Scope:

- Keep the attack family names `mblur` and `gblur` so reporting and formal
  queue logic remain compatible.
- Interpret `mblur` factors below 1 as alpha blends with kernel-3 median blur.
- Interpret `gblur` factors below 3 as radius-based Gaussian blur.
- Run only 10-sample calibration for GSD CIFAR10, MAS/GRDH, and MDDM-128 pilot.
- Recompute quality-budget selection and update the selected attack matrix.

Quality budget:

```text
stego-vs-attacked PSNR >= 30 dB
stego-vs-attacked LPIPS <= 0.10
```
