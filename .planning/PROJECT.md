# Stego Attack Workspace

## What This Is

This is a research workspace for steganographic message-destruction experiments. It integrates native or native-like generation/recovery paths for CRoSS, Pulsar, GSD, MAS/GRDH, MDDM, and RGS, then uses their generated stego artifacts as attack targets.

Identity baselines are now recorded for the runnable native/native-like paths.
The immediate work is 10-sample quality-budget smoke validation for candidate
attack methods. Full-scale selected-attack queues are available in the
framework, but require explicit user approval before launch or resume.

## Core Value

Produce reproducible, paper-aligned attack experiments that preserve each baseline's native semantics and clearly separate official, third-party, reference, pilot, and non-paper variants.

## Requirements

### Validated

- [x] Native/public baseline checkouts are tracked under `references/` and called through thin workspace runners.
- [x] Workspace-level SD1.5/SD3 reimplementations have been removed from the current baseline path.
- [x] A deterministic identity protocol exists at `/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522`.
- [x] Pulsar identity run records all 500 sample indices with 461 exact successes and 39 native failures.

### Active

- [x] Finish and summarize current runnable native identity baselines, including RGS 100-image identity.
- [x] Preserve method-native payload shape, capacity, embedding, sampling, inversion, decoding, ECC, and metric semantics.
- [x] Design quality-budget attack protocols that degrade hidden messages without rewriting baseline generation logic.
- [x] Implement resumable attack runners over the generated stego artifacts and existing identity metadata.
- [ ] Evaluate message destruction, image quality, and recovery degradation against each method's identity baseline.
- [ ] Keep scripts, configs, docs, summaries, and planning state in GitHub; keep large data, models, and run outputs under `/data2`.

### Out of Scope

- Reintroducing workspace-level baseline reimplementations as formal native results - this would violate the current native-original-repository rule.
- Treating MDDM as official author code - the integrated path is `native_third_party` until an official checkout is selected and audited.
- Reintroducing Diffusion-Stego from the old NS-DSer projection-only reference path - it was removed from the active project because it was not a full image-generation/reveal baseline.
- Committing large models, datasets, generated images, or result CSVs to GitHub - those belong under `/data2`.

## Context

The current repository is `/home/liyanlei/work/stego_attack_workspace`, with remote `git@github.com:LIYANLEI-test/stego_attack_workspace.git`.

Current baseline labels:

| Method | Label | Runner |
|--------|-------|--------|
| CRoSS | `native_official` | `scripts/run_cross_identity.py` |
| Pulsar | `native_official` | `scripts/run_pulsar_identity.py` |
| GSD | `native_official` | `scripts/run_gsd_identity.py` |
| MAS/GRDH | `native_official` | `scripts/run_mas_grdh_identity.py` |
| MDDM | `native_third_party` | `scripts/run_mddm_identity.py` |
| RGS | `native_official` | `scripts/run_rgs_identity.py` |

Identity protocol summary:

- Bit-payload methods use 500 samples.
- Image-payload methods, currently CRoSS and RGS, use 100 fixed FFHQ secret images.
- Bit payloads are deterministic per method/sample using `SHAKE256(protocol_seed | method | sample_index | payload_length)`.
- Payload length remains method-specific instead of being normalized across methods.

Current result root:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522
```

As of 2026-05-27, completed identity records include:

- Pulsar: 461 exact successes, 39 native failures, all 500 sample indices recorded.
- CRoSS: 100/100 records, mean recovery PSNR about 21.956 dB, mean SSIM about 0.675, exact pixel match 0/100.
- GSD CIFAR10: 500/500 records, mean bit accuracy about 0.874, exact 0/500.
- MAS/GRDH: 500/500 records, mean bit accuracy about 0.958, exact 0/500.
- MDDM 128-byte pilot: 50/50 records, mean bit accuracy about 0.999, exact 32/50; capacity exploration only.
- RGS: 100/100 records, 0 failures, mean recovery PSNR about 23.316 dB.

Formal attack evaluation:

- Parameters were selected on calibration sample indices `0-9` under
  stego-vs-attacked PSNR >= 30 dB and LPIPS <= 0.10.
- Formal paper summaries exclude `0-9` by default. For the current bit-payload
  scope this leaves held-out counts of GSD/MAS/GRDH/Pulsar `490` and MDDM
  pilot `40`.
- Current main-table candidates are GSD CIFAR10, MAS/GRDH, and Pulsar. MDDM
  remains bit-payload appendix-only, CRoSS/RGS are excluded as image-payload
  methods, and Diffusion-Stego is removed from current claims.

## Constraints

- **Native semantics**: Local compatibility changes may handle paths, caches, logging, checkpoint links, and import shims, but must not alter embedding, sampling, inversion, decoding, ECC, payload mapping, or metric logic without labeling the run as a variant.
- **Data placement**: Large models, datasets, generated images, CSVs, and logs stay under `/data2/liyanlei/...`; GitHub tracks code, small configs, docs, summaries, and planning state.
- **Provenance**: Method status labels must remain explicit: `native_official`, `native_third_party`, `pilot`, or `removed` as appropriate.
- **Reproducibility**: Runners must be deterministic, resumable, and log failures instead of aborting full sweeps when native method failures occur.
- **Git workflow**: Task updates should be committed and pushed to `origin/main` unless a future task explicitly calls for a branch.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use native original-repository implementations whenever practical | Attack results must be comparable to the paper methods rather than workspace rewrites | Good |
| Allow local compatibility only outside method semantics | Public research code often needs path/cache/import fixes to run locally | Good |
| Keep payload shape method-native | Forcing one common payload would make identity and attack results less paper-aligned | Good |
| Label MDDM as `native_third_party` | The integrated backend is not official author code | Good |
| Remove Diffusion-Stego from the active project | Only a projection-only NS-DSer reference path was available, not a full image-generation/reveal baseline | Good |
| Use GSD planning state for future work | The previous chat lost continuity during compaction/reconnect | Good |
| Fix an advance quality budget of PSNR >= 30 dB and LPIPS <= 0.10 | Quality-constrained payload destruction is comparable across attacks | Good |
| Exclude calibration indices `0-9` from paper summaries | Prevent attack-parameter selection leakage into evaluation | Good |
| Count failed recovery as zero only after a measurable attacked image exists | Avoid reporting runner failures as attack effectiveness | Good |

---
*Last updated: 2026-05-28 after removing Diffusion-Stego from the active project.*
