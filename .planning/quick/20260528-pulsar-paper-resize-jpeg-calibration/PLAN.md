---
status: complete
created: 2026-05-28
completed: 2026-05-28T00:00:00+08:00
---

# Pulsar Paper Resize/JPEG Calibration

Reproduce the resize and JPEG behavior reported by the ADS Pulsar-defense
paper on 10 samples, to check whether this workspace's Pulsar integration is
in the same regime as the paper.

## Scope

- Method: official Pulsar raw generate/reveal path, not the workspace
  region/ECC identity runner.
- Model: `google/ddpm-church-256`.
- Scheduler: DDIM, 50 steps.
- Key: `E * 64`.
- Payload: 8192 bytes.
- Samples: 10.
- Attacks:
  - identity.
  - resize 256 -> 224 -> 256.
  - JPEG Q90.
  - JPEG Q70.
- Success/failure rule: paper-style success is `BER <= 0.48`.
- Output root:
  `/data2/liyanlei/stego_attack_data/attack_runs/pulsar_paper_baseline_10_20260528`.

## Acceptance

- Confirm identity BER is close to the paper's raw Pulsar identity BER.
- Confirm resize224 and JPEG Q90/Q70 failure behavior is close enough to the
  paper to rule out a gross Pulsar integration error.
- Keep the run limited to 10 samples.
