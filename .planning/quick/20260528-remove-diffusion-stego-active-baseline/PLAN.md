---
status: complete
created: 2026-05-28
completed: 2026-05-28T00:00:00+08:00
---

# Remove Diffusion-Stego Active Baseline

Remove Diffusion-Stego from the active project after deciding not to reproduce
it. The available implementation was only an NS-DSer projection reference, not
a full generated-image reveal path suitable for image-domain attack evaluation.

## Scope

- Delete active Diffusion-Stego runner scripts.
- Remove Diffusion-Stego payload specs from newly generated identity protocols.
- Remove the active method doc.
- Update project, requirements, state, handoff, and main docs so
  Diffusion-Stego is marked `removed`, not `nsdser_reference`.
- Leave historical `/data2` outputs and old pilot docs as archival records only.

## Acceptance

- No active script entry point remains for Diffusion-Stego.
- New protocol generation no longer emits Diffusion-Stego message payload files.
- Main project status no longer lists Diffusion-Stego as an active baseline.
