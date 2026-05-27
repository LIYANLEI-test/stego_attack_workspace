---
status: complete
created: 2026-05-27
completed: 2026-05-27T14:24:00+08:00
---

# Pulsar 100-Sample Selected Attack Smoke

Run only Pulsar selected quality-budget attack candidates at 100 samples to test whether the 10-sample Pulsar failure pattern holds at a larger, user-approved scope.

## Scope

- Method: Pulsar only.
- Count: 100 samples per selected attack.
- Attacks: resize 1.25, JPEG 95, median blur 3, Gaussian blur 3, Regen-VAE quality 6.
- Output root: `/data2/liyanlei/stego_attack_data/attack_runs/pulsar_100_selected_20260527`.
- Do not resume or launch any multi-method full-scale queue.

## Acceptance

- Exactly 5 Pulsar jobs are launched.
- No non-Pulsar jobs run.
- Results are summarized as result rows, native reveal failures, and quality metrics where available.
- State is updated and pushed to GitHub after completion or if a runner failure occurs.
