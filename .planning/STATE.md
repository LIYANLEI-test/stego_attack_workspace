# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-25)

**Core value:** Produce reproducible, paper-aligned attack experiments that preserve native baseline semantics and honest provenance labels.
**Current focus:** Phase 1 - Identity Baseline Finalization

## Current Position

Phase: 1 of 5 (Identity Baseline Finalization)
Plan: 1 of 3 in current phase
Status: In progress
Last activity: 2026-05-25 - Ran MAS/GRDH native resize attack pilot and documented results.

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
- RGS: running, 82/100 records as of 2026-05-25 23:16 CST; PID 22714; mean recovery PSNR about 23.119 dB and mean indice accuracy about 0.994.

### Quick Tasks Completed

| Date | Task | Result |
|------|------|--------|
| 2026-05-25 | MAS/GRDH resize attack pilot | 10/10 rows, 0 failures, factor 0.5, mean bit accuracy 0.890216 vs same-sample identity 0.953400 |

### Pending Todos

None in `.planning/todos/pending/` yet.

### Blockers/Concerns

- `gsd-sdk` wrapper at `/home/liyanlei/bin/gsd-sdk` currently imports a missing `/tmp/get-shit-done-codex-install/sdk/dist/cli.js`; use manual `.planning/` updates or fallback tools until repaired.
- RGS full identity run is long-running and not yet complete.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Tooling | Repair `gsd-sdk` wrapper or document fallback CLI | Deferred to Phase 5 unless it blocks planning | Initialization |

## Session Continuity

Last session: 2026-05-25 23:16 CST
Stopped at: MAS/GRDH resize pilot documented; next action is decide whether to expand to more resize factors or a larger sample count.
Resume file: None
