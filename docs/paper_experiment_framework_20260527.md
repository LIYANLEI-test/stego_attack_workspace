# Paper Experiment Framework - 2026-05-27

## Goal

Build a defensible paper-grade evaluation for attacks that destroy or degrade
hidden information in generative-image steganography outputs while preserving
each generation method's native semantics.

The framework separates three things that are easy to mix up:

1. Identity recovery: how well each method recovers its payload without attack.
2. Attack quality budget: how much visible/perceptual image distortion the
   attack is allowed to introduce.
3. Payload destruction: how much the native reveal/recovery metric degrades
   after applying the attack.

## Current Main-Table Candidates

Use these methods in the main paper table only if the user explicitly approves
a full-scale selected-attack run after 10-sample smoke validation, and if those
runs complete at the planned counts:

| Method | Payload type | Label | Raw generated | Formal held-out | Main recovery metric |
|--------|--------------|-------|---------------|-----------------|----------------------|
| CRoSS | image payload | `native_official` | 100 | 90 | recovered-secret PSNR |
| GSD CIFAR10 | bit payload | `native_official` | 500 | 490 | bit accuracy |
| MAS/GRDH | bit payload | `native_official` | 500 | 490 | bit accuracy |
| Pulsar | bit payload | `native_official` | 500 | 490 | bit accuracy and native failure rate |

MDDM should remain outside the primary claim unless an official implementation
is integrated or the text clearly labels it as `native_third_party` pilot:

| Method | Payload type | Label | Raw / held-out | Use |
|--------|--------------|-------|----------------|-----|
| MDDM 128-byte | text/bit payload | `native_third_party` | 50 / 40 | pilot/appendix only |

Currently excluded from attack main tables:

| Method | Reason |
|--------|--------|
| RGS | official identity complete but attack runtime is too high for current queue |
| Diffusion-Stego | current workspace path is projection-only, not full image generation/reveal |

## Attack Families

Selected attacks are fixed by the quality-budget calibration in
`docs/quality_budget_attack_selection_20260527.md`.

Quality budget:

```text
stego-vs-attacked PSNR >= 30 dB
stego-vs-attacked LPIPS <= 0.10
```

## Formal Split And Quality Contract

Attack parameters were selected using calibration sample indices `0-9`.
Although the queue produces the full deterministic raw set for traceability,
paper summaries and paired identity deltas exclude these ten indices by
default. The formal held-out set is therefore `10-99` for CRoSS, `10-49` for
MDDM pilot, and `10-499` for the 500-sample methods. Use
`--include-calibration` only for diagnostic reconstruction of the raw queue,
not in paper tables.

The quality budget is evaluated as the mean stego-vs-attacked PSNR and mean
LPIPS over every recorded held-out sample for a method/attack row. Native
reveal failures remain in this quality calculation using their saved attacked
image. Final reports must have PSNR and LPIPS coverage equal to the held-out
row count. If a preselected parameter fails either held-out quality threshold,
the row is marked out of budget and excluded from budget-constrained claims;
it is not retuned on the held-out set.

A reveal/recovery failure is scored as zero payload recovery only when the
attacked image and corresponding stego image were successfully saved and can
be measured. Failures before that point are `unscorable_failures`: they
invalidate completeness for that row and require diagnosis or a documented
rerun, rather than being reported as attack success.

Selected formal matrix source of truth:

```text
scripts/selected_attack_matrix.py
```

Formal queue, gated:

Do not launch or resume this queue during candidate validation. The current
default scope is 10-sample smoke testing. Full-scale execution requires
explicit user approval because a stale handoff previously caused an accidental
6550-record planned run to continue.

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  HF_HOME=/data2/liyanlei/huggingface TORCH_HOME=/data2/liyanlei/torch \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_selected_attack_queue.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527 \
  --gpus 0,1,2,3
```

Dry run:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_selected_attack_queue.py --dry-run
```

Summary:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/summarize_selected_attack_runs.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527 \
  --output /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527/selected_attack_summary.csv
```

Use `--include-lpips` only when a full LPIPS recomputation is needed. It is
slower because it reloads saved images.

Identity-vs-attacked delta table:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/summarize_attack_deltas.py \
  --attack-root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527 \
  --output /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527/selected_attack_deltas.csv
```

The delta table computes paired overlap between identity and attacked sample
indices. This should be the preferred table for claims about degradation
relative to each method's no-attack baseline.

Paper table rendering:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/render_paper_tables.py \
  --summary /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527/selected_attack_summary.csv \
  --deltas /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527/selected_attack_deltas.csv \
  --output-md /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527/paper_tables.md \
  --output-tex /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527/paper_tables.tex
```

Queue monitor:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/monitor_selected_attack_queue.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527 \
  --queue-pid 8246 \
  --poll-seconds 300 \
  --finalize-when-done
```

The monitor does not launch or stop attack jobs. It refreshes live summary,
delta, Markdown/LaTeX tables, paper-readiness audit, live manifest, and
`queue_progress_snapshot.{json,md}`. If all selected jobs complete, it writes
the final non-`_live` reports and recomputes LPIPS for the final summary. For a
new queue, replace `--queue-pid` with the new driver PID or omit it to let the
monitor detect matching queue processes by experiment root.

Experiment manifest:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/capture_experiment_manifest.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527
```

The manifest records the git commit, GPU inventory, quality budget, evaluation
split, raw and formal counts, and script entry points for reproducibility.
Keep it under `/data2`; do not commit the generated JSON, CSV, Markdown, or
TeX result artifacts.

Paper-readiness audit:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/audit_selected_attack_results.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527
```

The audit marks rows as main/appendix/excluded, flags adapted attacks and pilot
baselines, and checks whether PSNR/LPIPS evidence is present for the quality
budget. Live summaries without LPIPS recomputation are marked `partial`, not
treated as fully budget-verified. Pending, incomplete, and unscorable rows
remain in readiness reports so a failed experiment cannot silently disappear
from final review. Rendered Markdown/LaTeX readiness tables also retain these
rows; only claim-bearing presentation tables may later select verified
budget-passing rows with the exclusion stated explicitly.

## Reporting Rules

Main table columns:

| Column | Meaning |
|--------|---------|
| Method | native generation/recovery method |
| Attack | selected attack family and parameter |
| Quality PSNR | mean stego-vs-attacked PSNR |
| Quality LPIPS | mean stego-vs-attacked LPIPS, if computed |
| Recovery metric | bit accuracy or recovered-secret PSNR |
| 95% CI | normal-approximation CI over samples |
| Failures | native reveal/recovery failures after attack |

All table counts refer to the held-out subset unless explicitly labeled
`raw generated`.

Delta table columns:

| Column | Meaning |
|--------|---------|
| identity_overlap_mean | no-attack baseline metric over the same sample IDs |
| attack_overlap_mean | attacked metric over the same sample IDs |
| delta_mean | identity minus attacked metric |
| delta_ci95 | normal-approximation 95% CI for per-sample deltas |
| relative_drop | `delta_mean / identity_overlap_mean` |

Because Pulsar has native failures even without attacks, delta reports also
include a conditional comparison restricted to sample indices whose identity
run successfully recovered a payload. The unconditional aggregate reflects
end-to-end usability; the conditional delta more directly isolates
attack-induced degradation from pre-existing native failure.

For bit payload methods:

```text
Attack success increases as bit accuracy decreases.
Native reveal failure after saved attacked image = bit accuracy 0 for aggregate scoring.
```

For image payload methods:

```text
Attack success increases as recovered-secret PSNR decreases.
Native recovery failure after saved attacked image = recovered-secret PSNR 0 for aggregate scoring.
```

For Pulsar:

```text
Report both bit accuracy and failure rate. Current calibration suggests the
method is very fragile to mild image-domain perturbation; do not hide that in
an average-only table.
```

For adapted attacks:

```text
Label Regen-VAE and UnMarker as adapted attack baselines. Do not claim full
paper reproduction of WatermarkAttacker or UnMarker unless their complete
scheme-specific evaluation harness is reproduced separately.
```

## Fairness Checklist

- Payloads remain method-native in shape and capacity.
- Attack is inserted after stego image generation and before native
  reveal/recovery.
- Image quality is measured between stego and attacked images.
- Parameter choice is fixed before formal-scale sweeps.
- Calibration indices `0-9` are excluded from all formal paper estimates.
- Identity baseline and attacked samples use the same deterministic sample
  indices.
- Native reveal/recovery failures after a saved attacked image are included in
  aggregate payload-destruction metrics as zero recovery.
- A held-out row that fails its quality budget is reported but excluded from
  fixed-budget comparisons without retuning on that set.
- Large outputs stay under `/data2/liyanlei/...`; Git tracks scripts, docs, and
  planning state only.

## Claim Boundaries

Safe claim if formal runs complete:

```text
Under a fixed image-quality budget, selected image-domain perturbations and
regeneration attacks substantially degrade native hidden-payload recovery across
multiple generative steganography baselines.
```

Claims that need more work:

```text
The attack is universal across all generative steganography methods.
```

RGS and full Diffusion-Stego are not yet in the attack table.

```text
MDDM is an official baseline.
```

The current MDDM path is third-party and pilot-scale.

```text
UnMarker/WatermarkAttacker are fully reproduced.
```

The current integration adapts their attack primitive as black-box image
transforms under this workspace's native-reveal protocol.

## Next Work To Strengthen Publishability

1. Complete the running selected-attack queue and final held-out reports.
2. Use identity-vs-attacked delta tables and explicit failure-rate reporting in
   the paper analysis.
3. Add robust uncertainty estimates and aggregate attack-family comparisons
   only after quality-budget audit passes.
4. Decide whether to spend compute on RGS selected attacks or explicitly keep
   it as identity-only due to runtime.
5. Either integrate an official MDDM implementation or keep MDDM out of main
   claims.
6. Revisit Diffusion-Stego only after implementing full generated-image reveal,
   not projection-only encode/decode.
