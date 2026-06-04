---
status: complete
created: 2026-06-05
---

# Bit-Payload-Only Attack Scope

Remove image-payload steganography methods from the current attack comparison
scope and continue with bit-payload methods only.

Scope:

- Keep CRoSS and RGS implementations/history intact, but exclude them from the
  active target-PSNR and paper-table scope.
- Active bit-payload targets: GSD CIFAR10, MAS/GRDH, Pulsar, and MDDM
  128-byte pilot.
- Preserve MDDM's `native_third_party`/pilot caveat.
- Generate bit-only target-PSNR CSV artifacts from the existing 10-sample
  calibration data; do not launch a full formal queue.
