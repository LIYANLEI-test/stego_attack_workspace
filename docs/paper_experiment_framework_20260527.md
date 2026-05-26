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

Use these methods in the main paper table if the formal selected-attack runs
complete at the planned counts:

| Method | Payload type | Label | Formal count | Main recovery metric |
|--------|--------------|-------|--------------|----------------------|
| CRoSS | image payload | `native_official` | 100 | recovered-secret PSNR |
| GSD CIFAR10 | bit payload | `native_official` | 500 | bit accuracy |
| MAS/GRDH | bit payload | `native_official` | 500 | bit accuracy |
| Pulsar | bit payload | `native_official` | 500 | bit accuracy and native failure rate |

MDDM should remain outside the primary claim unless an official implementation
is integrated or the text clearly labels it as `native_third_party` pilot:

| Method | Payload type | Label | Count | Use |
|--------|--------------|-------|-------|-----|
| MDDM 128-byte | text/bit payload | `native_third_party` | 50 | pilot/appendix only |

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

Selected formal matrix source of truth:

```text
scripts/selected_attack_matrix.py
```

Formal queue:

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
- Identity baseline and attacked samples use the same deterministic sample
  indices.
- Failures are included in aggregate payload-destruction metrics.
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

1. Run the selected attack queue at formal counts.
2. Add identity-vs-attacked delta tables per method.
3. Add a failure-rate table for methods that throw native reveal failures.
4. Decide whether to spend compute on RGS selected attacks or explicitly keep
   it as identity-only due to runtime.
5. Either integrate an official MDDM implementation or keep MDDM out of main
   claims.
6. Revisit Diffusion-Stego only after implementing full generated-image reveal,
   not projection-only encode/decode.
