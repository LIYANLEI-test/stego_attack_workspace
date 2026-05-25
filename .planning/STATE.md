# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-25)

**Core value:** Produce reproducible, paper-aligned attack experiments that preserve native baseline semantics and honest provenance labels.
**Current focus:** Phase 1 - Identity Baseline Finalization

## Current Position

Phase: 1 of 5 (Identity Baseline Finalization)
Plan: 1 of 3 in current phase
Status: In progress
Last activity: 2026-05-26 - Started continuous non-RGS attack sweep queue after resize/storage pilots.

Progress: [=---------] 5%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: N/A
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Identity Baseline Finalization | 0/3 | N/A | N/A |

**Recent Trend:**
- Last 5 plans: N/A
- Trend: N/A

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Use native original repository implementations whenever practical.
- Keep MDDM labeled `native_third_party`; do not call it official.
- Keep Diffusion-Stego labeled `nsdser_reference`; projection-only checks are not full image recovery.
- Commit and push task updates to GitHub after meaningful state changes.

### Current Identity Snapshot

Result root: `/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522`

- Pulsar: complete, 461 exact successes and 39 native failures across 500 samples.
- CRoSS: complete, 100/100 records, mean recovery PSNR about 21.956 dB, mean SSIM about 0.675.
- GSD CIFAR10: complete, 500/500 records, mean bit accuracy about 0.874.
- MAS/GRDH: complete, 500/500 records, mean bit accuracy about 0.958.
- MDDM 128-byte pilot: complete as pilot only, 50/50 records, 32 exact, mean bit accuracy about 0.999.
- Diffusion-Stego projection variants: complete projection-only checks, 500/500 exact for MN/MB/MC/Multi-bits.
- RGS: running, 97/100 records as of 2026-05-26 CST; PID 22714; mean recovery PSNR about 23.257 dB. RGS attacks are skipped for now because it is too slow.

### Current Unified Resize Attack Snapshot

Result root: `/data2/liyanlei/stego_attack_data/attack_runs/unified_resize_20260526`

Attack protocol: shared RGB image-domain resize round trip using PIL bilinear
interpolation, factors `0.5`, `0.75`, `1.25`, and `1.5`, 10 samples per
method/factor.

- CRoSS: complete all four factors, 10/10 rows and 0 failures each; mean recovery PSNR 18.619120 / 20.542374 / 21.086257 / 19.920919 dB.
- MAS/GRDH: complete all four factors, 10/10 rows and 0 failures each; mean bit accuracy 0.878314 / 0.926898 / 0.943085 / 0.941510.
- GSD CIFAR10: complete all four factors, 10/10 rows and 0 failures each; mean bit accuracy 0.592936 / 0.685417 / 0.781608 / 0.785319.
- Pulsar: complete all four factors as failures; 0 result rows and 10 native reveal failures per factor.
- MDDM 128-byte pilot: complete all four factors, 10/10 rows and 0 failures each; mean bit accuracy 0.983398 / 0.994336 / 0.998145 / 0.998145.
- RGS: not included in this quick pilot; needs a dedicated in-memory attack branch and is long-running.
- Diffusion-Stego: not included because the current workspace path is projection-only, not full generated-image reveal.

### Current Unified Storage Attack Snapshot

Result root: `/data2/liyanlei/stego_attack_data/attack_runs/unified_storage_20260526`

Attack protocol: lossless PNG storage round trip before native reveal/recovery,
10 samples per method. Pulsar uses its native 16-bit PNG save/reload path rather
than generic 8-bit RGB PIL conversion.

- CRoSS: complete, 10/10 rows and 0 failures; mean recovery PSNR 20.520565 dB and mean recovery SSIM 0.655835.
- MAS/GRDH: complete, 10/10 rows and 0 failures; mean bit accuracy 0.951678.
- GSD CIFAR10: complete, 10/10 rows and 0 failures; mean bit accuracy 0.891048.
- Pulsar: complete, 10/10 rows and 0 failures; mean bit accuracy 1.000000 and exact 10/10.
- MDDM 128-byte pilot: complete, 10/10 rows and 0 failures; mean bit accuracy 0.998535 and exact 7/10.
- RGS: skipped per user instruction because it is too slow for attack runs on the current machine.
- Diffusion-Stego: not included because the current workspace path is projection-only, not full generated-image reveal.

### Active Continuous Attack Queue

GSD quick task: `.planning/quick/20260526-continuous-attack-sweeps/`

Next queued non-RGS image-domain attacks:

- JPEG quality 90, 70, 50.
- Median blur kernel 3, 5, 7.
- Gaussian blur kernel 3, 5, 7.

Methods in queue: CRoSS, MAS/GRDH, GSD CIFAR10, Pulsar, and MDDM 128-byte
pilot. Each queue item starts at 10 samples and uses idle GPUs as available.

### Quick Tasks Completed

| Date | Task | Result |
|------|------|--------|
| 2026-05-25 | MAS/GRDH resize attack pilot | 10/10 rows, 0 failures, factor 0.5, mean bit accuracy 0.890216 vs same-sample identity 0.953400 |
| 2026-05-26 | Unified resize attack pilot | Shared resize factors 0.5/0.75/1.25/1.5 ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; Pulsar failed native reveal for all attacked samples |
| 2026-05-26 | Unified storage attack pilot | Shared storage round trip ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; all non-RGS methods completed 10/10 rows with 0 failures |

### Pending Todos

None in `.planning/todos/pending/` yet.

### Blockers/Concerns

- `gsd-sdk` wrapper at `/home/liyanlei/bin/gsd-sdk` currently imports a missing `/tmp/get-shit-done-codex-install/sdk/dist/cli.js`; use manual `.planning/` updates or fallback tools until repaired.
- RGS full identity run is long-running and not yet complete.
- `gsd-sdk` is still broken, so this quick task was recorded manually in `.planning/quick/`.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Tooling | Repair `gsd-sdk` wrapper or document fallback CLI | Deferred to Phase 5 unless it blocks planning | Initialization |

## Session Continuity

Last session: 2026-05-26 CST
Stopped at: Continuous non-RGS attack sweep queue started; resize/storage complete, JPEG/blur sweeps next.
Resume file: None
