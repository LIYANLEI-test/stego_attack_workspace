# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-25)

**Core value:** Produce reproducible, paper-aligned attack experiments that preserve native baseline semantics and honest provenance labels.
**Current focus:** Paper-grade selected-attack framework and formal quality-budget sweeps for runnable non-RGS methods.

## Current Position

Phase: 1 of 5 (Identity Baseline Finalization)
Plan: 1 of 3 in current phase
Status: Formal selected-attack framework ready; long queue may be launched/resumed under `/data2`
Last activity: 2026-05-27 - Added paper framework, selected attack matrix, formal queue, and summary scripts.

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
- Do not resume formal attack sweeps until the baseline set is re-evaluated and strengthened; the current matrix is useful as pilot/checkpoint data, not final comparative evidence.
- Treat `andrekassis/ai-watermark`/UnMarker as an attack-method candidate only, not a hiding/steganography baseline.
- Treat `XuandongZhao/WatermarkAttacker` Regen-VAE as a stronger adapted attack-method candidate, not a hiding/steganography baseline.
- Treat `and-mill/semantic-forgery` as related semantic-watermark attack work, not a current hidden-payload destruction baseline.
- For fair attack comparison, select attack parameters under a fixed stego-vs-attacked image-quality budget: PSNR >= 30 dB and LPIPS <= 0.10. Within budget, choose the strongest payload-destruction setting per method/attack.

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

### Paused Identity-Scale Attack Queue

GSD quick task: `.planning/quick/20260526-identity-scale-attack-sweeps/`

Result root: `/data2/liyanlei/stego_attack_data/attack_runs/unified_identity_scale_20260526`

Queue status: intentionally stopped on 2026-05-26 13:23 CST after the user said the baseline set is too small/weak.

Original queue process: PID `8858`, launched 2026-05-26 05:33 CST with GPUs `0,1,2,3`.
Driver log:
`/data2/liyanlei/stego_attack_data/attack_runs/unified_identity_scale_20260526/logs/queue_driver.log`

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

Stop checkpoint, 2026-05-26 13:23 CST:

- `resize_0.5` completed for all queued non-RGS methods.
  - CRoSS: 100/100 rows, 0 failures, mean recovery PSNR 19.996824 dB.
  - GSD CIFAR10: 500/500 rows, 0 failures, mean bit accuracy 0.588711.
  - MAS/GRDH: 500/500 rows, 0 failures, mean bit accuracy 0.896614.
  - Pulsar: 500/500 total records, 7 zero-bit rows and 493 native reveal failures.
  - MDDM 128-byte pilot: 50/50 rows, 0 failures, mean bit accuracy 0.981445.
- `resize_0.75` completed for all queued non-RGS methods.
  - CRoSS: 100/100 rows, 0 failures, mean recovery PSNR 20.921217 dB.
  - GSD CIFAR10: 500/500 rows, 0 failures, mean bit accuracy 0.676061.
  - MAS/GRDH: 500/500 rows, 0 failures, mean bit accuracy 0.937157.
  - Pulsar: 500/500 total records, 7 zero-bit rows and 493 native reveal failures.
  - MDDM 128-byte pilot: 50/50 rows, 0 failures, mean bit accuracy 0.994941.
- `resize_1.25` is partial because the queue was stopped intentionally.
  - CRoSS: 100/100 rows, 0 failures, mean recovery PSNR 21.743084 dB.
  - GSD CIFAR10: 181/500 rows, 0 failures, mean bit accuracy 0.763598.
  - MAS/GRDH: 309/500 rows, 0 failures, mean bit accuracy 0.952522.
  - Pulsar: 195/500 total records, 3 zero-bit rows and 192 native reveal failures.
  - MDDM 128-byte pilot: 50/50 rows, 0 failures, mean bit accuracy 0.998320.
- `resize_1.5` is partial because the queue was stopped intentionally.
  - CRoSS: 11/100 rows, 0 failures, mean recovery PSNR 19.955780 dB.
- Formal-scale storage, JPEG, median blur, and Gaussian blur queue items were not started before the pause.
- No duplicate sample IDs have been detected by `scripts/summarize_unified_attack_runs.py`.
- No matching attack queue or method runner processes remained after stopping; GPUs were idle or near-idle at the pause check.

### Baseline Re-Scope Gate

The user explicitly paused further attacks because the baseline set is currently
too small/weak for a convincing comparison. Treat the completed pilots and the
formal resize 0.5/0.75 results as checkpoint data only.

Before restarting any formal attack queue:

- Reassess which stronger official/public baselines should be added.
- Decide whether to replace or supplement current `native_third_party` MDDM with an official implementation.
- Decide whether Diffusion-Stego needs a full image-generation/reveal implementation or should stay excluded from image attacks.
- Keep RGS skipped from attacks only if the user accepts the runtime tradeoff after the stronger baseline plan is clear.
- Update `.planning/` and push the accepted baseline plan before running more long sweeps.

### Current UnMarker Attack Candidate Smoke

GSD quick task: `.planning/quick/20260526-unmarker-attack-candidate-smoke/`

Doc: `docs/unmarker_attack_smoke_20260526.md`

Result root:
`/data2/liyanlei/stego_attack_data/attack_runs/unmarker_smoke_20260526/gsd_cifar10_unmarker_high_smoke_10`

- Decision: `andrekassis/ai-watermark` is not a steganography baseline; it is an attack-method candidate.
- Adapter: `scripts/unmarker_attack.py` imports the official UnMarker coordinate optimization core from `references/ai-watermark`.
- Smoke: GSD CIFAR10, 10 samples, high-frequency UnMarker core, local `smoke` profile, 25 iterations.
- Result: 10/10 rows, 0 failures, mean bit accuracy 0.765430, mean stego-vs-attacked PSNR 45.083339 dB, mean runtime 34.61 s/sample.
- Caveat: smoke-only adapted attack result; do not present as full UnMarker paper reproduction.

### Current Strong Attack Baseline Candidate Smoke

GSD quick task: `.planning/quick/20260526-strong-attack-baseline-survey/`

Doc: `docs/strong_attack_baseline_survey_20260526.md`

Result root:
`/data2/liyanlei/stego_attack_data/attack_runs/regen_vae_smoke_20260526/gsd_cifar10_bmshj2018_factorized_q3_10`

- Decision: `XuandongZhao/WatermarkAttacker` is an attack-method reference, not a steganography baseline.
- Provenance: official public code for *Invisible Image Watermarks Are Provably Removable Using Generative AI*, NeurIPS 2024.
- Adapter: `scripts/regen_attack.py` implements a size-preserving Regen-VAE transform using the same CompressAI model family as the reference repository.
- GSD hook: `scripts/run_gsd_identity.py --attack-kind regen_vae --regen-model bmshj2018-factorized --regen-quality 3`.
- Generic attack helper support: `attack_common.py` supports `regen_vae`, and CRoSS, MAS/GRDH, MDDM, and Pulsar runner choices now accept it for follow-on smoke tests.
- Smoke: GSD CIFAR10, 10 samples, `bmshj2018-factorized` quality 3.
- Result: 10/10 rows, 0 failures, mean bit accuracy 0.524089, BER 0.475911, mean stego-vs-attacked PSNR 25.176627 dB, mean runtime 33.58 s/sample.
- Caveat: smoke-only adapted attack result; do not present as a full WatermarkAttacker paper reproduction.

### Current Semantic Forgery Suitability Check

GSD quick task: `.planning/quick/20260527-semantic-forgery-suitability/`

Doc: `docs/semantic_forgery_suitability_20260527.md`

- Decision: `and-mill/semantic-forgery` is not included in the current attack matrix.
- Provenance: official public code for *Black-Box Forgery Attacks on Semantic Watermarks for Diffusion Models*, CVPR 2025 Oral.
- Reason: the native attacks target Tree-Ring/Gaussian-Shading semantic watermarks and their verifiers. The scripts generate or reprompt semantic-watermarked diffusion images rather than applying a detector-independent, content-preserving transform to arbitrary stego artifacts before native reveal.
- No 10-image smoke was run because it would measure a different task, not hidden-payload destruction under the current quality-budget protocol.

### Current Quality-Budget Attack Selection

GSD quick task: `.planning/quick/20260527-quality-budget-attack-selection/`

Doc: `docs/quality_budget_attack_selection_20260527.md`

Result root:
`/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527`

Budget:

```text
stego-vs-attacked PSNR >= 30 dB
stego-vs-attacked LPIPS <= 0.10
10 samples per method/factor
```

Selected CSVs:

```text
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary.csv
/data2/liyanlei/stego_attack_data/attack_runs/quality_budget_20260527/quality_budget_summary_selected.csv
```

Selection rule: lower bit accuracy is stronger for bit-payload methods; lower
recovered-secret PSNR is stronger for image-payload methods. Native recovery
failure after a saved attacked image is counted as complete payload recovery
failure while still computing quality from the saved stego/attacked image pair.

Selected parameters:

- CRoSS: resize 1.5, JPEG 50, median blur 3, Gaussian blur 3, Regen-VAE q=5.
- GSD CIFAR10: resize 1.25, JPEG 80, Regen-VAE q=6, UnMarker high-smoke-25.
- MAS/GRDH: resize 1.5, JPEG 50, Regen-VAE q=6.
- MDDM 128-byte pilot: JPEG 70 only; resize, blur, and Regen-VAE had no in-budget destructive candidate in this 10-sample calibration.
- Pulsar: resize 1.25, JPEG 95, median blur 3, Gaussian blur 3, Regen-VAE q=6. All selected Pulsar attacks caused native reveal failure on the 10 samples while staying inside the quality budget.

Caveats:

- These are 10-sample calibration choices, not final paper-scale tables.
- RGS remains excluded from attacks for runtime reasons.
- Diffusion-Stego remains excluded because the current workspace path is projection-only.
- MDDM remains `native_third_party`.
- UnMarker is currently integrated only for GSD and is an adapted attack-method candidate.

### Current Paper Framework And Formal Queue

GSD quick task: `.planning/quick/20260527-paper-framework-and-selected-formal-queue/`

Doc: `docs/paper_experiment_framework_20260527.md`

Selected matrix source:

```text
scripts/selected_attack_matrix.py
```

Formal selected-attack queue:

```text
scripts/run_selected_attack_queue.py
```

Formal selected-attack summary:

```text
scripts/summarize_selected_attack_runs.py
```

Planned formal root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527
```

Formal queue size:

- CRoSS: 5 selected attacks x 100 samples.
- GSD CIFAR10: 4 selected attacks x 500 samples.
- MAS/GRDH: 3 selected attacks x 500 samples.
- MDDM 128-byte pilot: 1 selected attack x 50 samples.
- Pulsar: 5 selected attacks x 500 samples.

Launch command:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  HF_HOME=/data2/liyanlei/huggingface TORCH_HOME=/data2/liyanlei/torch \
  /data2/liyanlei/envs/stego_attack/bin/python scripts/run_selected_attack_queue.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527 \
  --gpus 0,1,2,3
```

Summary command:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python scripts/summarize_selected_attack_runs.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527 \
  --output /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527/selected_attack_summary.csv
```

Paper framework decisions:

- Main-table candidates: CRoSS, GSD CIFAR10, MAS/GRDH, Pulsar.
- MDDM remains pilot/appendix unless official code is integrated.
- RGS remains identity-only until runtime budget is explicitly accepted.
- Diffusion-Stego remains projection-only and excluded from image-attack claims.
- Regen-VAE and UnMarker are adapted attack baselines, not full paper reproductions.

### Quick Tasks Completed

| Date | Task | Result |
|------|------|--------|
| 2026-05-25 | MAS/GRDH resize attack pilot | 10/10 rows, 0 failures, factor 0.5, mean bit accuracy 0.890216 vs same-sample identity 0.953400 |
| 2026-05-26 | Unified resize attack pilot | Shared resize factors 0.5/0.75/1.25/1.5 ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; Pulsar failed native reveal for all attacked samples |
| 2026-05-26 | Unified storage attack pilot | Shared storage round trip ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; all non-RGS methods completed 10/10 rows with 0 failures |
| 2026-05-26 | Continuous JPEG/blur attack sweeps | Shared JPEG, median blur, and Gaussian blur ran on CRoSS, MAS/GRDH, GSD, Pulsar, and MDDM pilot; 45/45 method/factor directories completed with 10 records each |
| 2026-05-26 | UnMarker attack candidate smoke | `andrekassis/ai-watermark` kept as adapted attack candidate, not hiding baseline; GSD CIFAR10 10/10 rows, 0 failures, mean bit accuracy 0.765430 |
| 2026-05-26 | Strong attack baseline survey | WatermarkAttacker Regen-VAE selected and integrated as adapted attack candidate; GSD CIFAR10 10/10 rows, 0 failures, mean bit accuracy 0.524089 |
| 2026-05-27 | Semantic Forgery suitability check | `and-mill/semantic-forgery` classified as related semantic-watermark attack work, not a current hidden-payload destruction baseline |
| 2026-05-27 | Quality-budget attack selection | Selected 10-sample fair-budget attack parameters under PSNR >= 30 dB and LPIPS <= 0.10 for CRoSS, GSD, MAS/GRDH, MDDM pilot, and Pulsar |
| 2026-05-27 | Paper framework and selected formal queue | Added selected attack matrix, formal queue, summary script with CI columns, and paper claim-boundary documentation |

### Pending Todos

None in `.planning/todos/pending/` yet.

### Blockers/Concerns

- `gsd-sdk` wrapper at `/home/liyanlei/bin/gsd-sdk` currently imports a missing `/tmp/get-shit-done-codex-install/sdk/dist/cli.js`; use manual `.planning/` updates or fallback tools until repaired.
- RGS attack runs remain intentionally skipped for speed unless explicitly requested.
- `gsd-sdk` is still broken, so quick tasks are recorded manually in `.planning/quick/`.
- Baseline adequacy is now a blocking methodological concern; do not resume queued attacks until the baseline set is re-scoped.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Tooling | Repair `gsd-sdk` wrapper or document fallback CLI | Deferred to Phase 5 unless it blocks planning | Initialization |

## Session Continuity

Last session: 2026-05-26 CST
Stopped at: Identity-scale non-RGS attack queue intentionally stopped. Resize 0.5 and 0.75 are complete; resize 1.25 and 1.5 are partial; formal storage/JPEG/blur scale did not start under this queue. Next action is baseline re-scope before any more attack execution.
Resume file: `.planning/.continue-here.md`
