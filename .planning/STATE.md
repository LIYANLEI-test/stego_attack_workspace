# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-25)

**Core value:** Produce reproducible, paper-aligned attack experiments that preserve native baseline semantics and honest provenance labels.
**Current focus:** Phase 1 - Identity Baseline Finalization

## Current Position

Phase: 1 of 5 (Identity Baseline Finalization)
Plan: 1 of 3 in current phase
Status: In progress
Last activity: 2026-05-26 - Started identity-scale non-RGS attack sweep queue after completing 10-sample pilots.

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
- RGS: complete, 100/100 records, 0 failures, mean recovery PSNR about 23.316 dB. RGS attacks are skipped for now because it is too slow.

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

### Current Unified JPEG And Blur Attack Snapshot

GSD quick task: `.planning/quick/20260526-continuous-attack-sweeps/`

Result root: `/data2/liyanlei/stego_attack_data/attack_runs/unified_image_attacks_20260526`

Attack protocol: shared image-domain JPEG, median blur, and Gaussian blur
attacks before native reveal/recovery. Factors follow the MAS/GRDH README:
JPEG quality `90/70/50`, median blur kernel `3/5/7`, and Gaussian blur kernel
`3/5/7`, 10 samples per method/factor.

- CRoSS: complete all 9 settings, 10/10 rows and 0 failures each; recovery PSNR range 17.780781-20.209000 dB.
- MAS/GRDH: complete all 9 settings, 10/10 rows and 0 failures each; bit accuracy range 0.748199-0.927435.
- GSD CIFAR10: complete all 9 settings, 10/10 rows and 0 failures each; bit accuracy range 0.528385-0.701009.
- Pulsar: complete all 9 settings as attacked reveal failures; 0 result rows and 10 native reveal failures per setting.
- MDDM 128-byte pilot: complete all 9 settings, 10/10 rows and 0 failures each; bit accuracy range 0.933496-0.996680.
- RGS: skipped per user instruction because it is too slow for attack runs on the current machine.
- Diffusion-Stego: not included because the current workspace path is projection-only, not full generated-image reveal.

### Active Identity-Scale Attack Queue

GSD quick task: `.planning/quick/20260526-identity-scale-attack-sweeps/`

Result root: `/data2/liyanlei/stego_attack_data/attack_runs/unified_identity_scale_20260526`

Queue protocol: same shared image-domain attack insertion as the 10-sample
pilots, scaled to the current runnable identity/pilot counts per method:
CRoSS 100, GSD CIFAR10 500, MAS/GRDH 500, Pulsar 500, and MDDM 128-byte pilot
50. RGS remains excluded for speed. Diffusion-Stego remains excluded because it
is projection-only in this workspace.

Queued attack settings:

- Resize factors `0.5`, `0.75`, `1.25`, and `1.5`.
- Storage lossless PNG round trip.
- JPEG quality `90`, `70`, and `50`.
- Median blur kernel `3`, `5`, and `7`.
- Gaussian blur kernel `3`, `5`, and `7`.

### Quick Tasks Completed

| Date | Task | Result |
|------|------|--------|
| 2026-05-25 | MAS/GRDH resize attack pilot | 10/10 rows, 0 failures, factor 0.5, mean bit accuracy 0.890216 vs same-sample identity 0.953400 |
| 2026-05-26 | Unified resize attack pilot | Shared resize factors 0.5/0.75/1.25/1.5 ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; Pulsar failed native reveal for all attacked samples |
| 2026-05-26 | Unified storage attack pilot | Shared storage round trip ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; all non-RGS methods completed 10/10 rows with 0 failures |
| 2026-05-26 | Continuous JPEG/blur attack sweeps | Shared JPEG, median blur, and Gaussian blur ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; 45/45 method/factor directories completed with 10 records each |

### Pending Todos

None in `.planning/todos/pending/` yet.

### Blockers/Concerns

- `gsd-sdk` wrapper at `/home/liyanlei/bin/gsd-sdk` currently imports a missing `/tmp/get-shit-done-codex-install/sdk/dist/cli.js`; use manual `.planning/` updates or fallback tools until repaired.
- RGS attack runs remain intentionally skipped for speed unless explicitly requested.
- `gsd-sdk` is still broken, so quick tasks are recorded manually in `.planning/quick/`.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Tooling | Repair `gsd-sdk` wrapper or document fallback CLI | Deferred to Phase 5 unless it blocks planning | Initialization |

## Session Continuity

Last session: 2026-05-26 CST
Stopped at: Identity-scale non-RGS attack queue prepared; next action is run and monitor `/data2/liyanlei/stego_attack_data/attack_runs/unified_identity_scale_20260526`.
Resume file: None
