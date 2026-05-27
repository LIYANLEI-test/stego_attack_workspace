# Roadmap: Stego Attack Workspace

## Overview

The v1 path starts by closing the native identity baseline ledger, then defines attack protocols that sit outside baseline generation logic, implements resumable attack runners, evaluates message destruction against the identity baseline, and finishes with reproducibility documentation plus GitHub-visible planning state.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): planned milestone work.
- Decimal phases (2.1, 2.2): urgent insertions if needed.

- [x] **Phase 1: Identity Baseline Finalization** - Finish RGS, consolidate identity summaries, and lock provenance labels.
- [x] **Phase 2: Attack Protocol Design** - Define attack layers, budgets, metrics, and method-specific constraints.
- [x] **Phase 3: Attack Runner Implementation** - Build resumable attack execution over stego artifacts and identity metadata.
- [ ] **Phase 4: Evaluation And Analysis** - Compute message destruction and quality metrics against identity baselines.
- [ ] **Phase 5: Reproducibility And Release Hygiene** - Make results inspectable through docs, manifests, checks, and pushed Git state.

## Phase Details

### Phase 1: Identity Baseline Finalization
**Goal**: All current native/native-like baselines have honest, documented identity status with result roots, caveats, and current/final metrics.
**Depends on**: Nothing (first phase)
**Requirements**: BASE-01, BASE-02, BASE-03, BASE-04, ID-01, ID-02, ID-03, ID-04, ID-05, ID-06, ID-07, ID-08
**Success Criteria** (what must be TRUE):
  1. RGS either reaches 100/100 records or is explicitly documented as interrupted/resumable with the exact last sample and process state.
  2. `docs/native_generation_status.md` and a concise summary identify completed, pilot, projection-only, and failed-native records.
  3. All method labels match implementation provenance and no MDDM/Diffusion-Stego result is overstated.
  4. GitHub contains only scripts, configs, docs, and summary/planning state, not large generated artifacts.
**Plans**: 3 plans

Plans (completed through quick tasks and status updates):
- [x] 01-01: Monitor or resume RGS and capture final or current status.
- [x] 01-02: Generate/update identity summary documentation from result CSVs and logs.
- [x] 01-03: Audit provenance labels, docs, and git-tracked files before committing.

### Phase 2: Attack Protocol Design
**Goal**: Define a paper-aligned message-destruction protocol that can be executed without changing baseline method semantics.
**Depends on**: Phase 1
**Requirements**: ATT-01, ATT-02, ATT-03, ATT-04
**Success Criteria** (what must be TRUE):
  1. Each attack layer has a target artifact, perturbation budget, and metric contract.
  2. Each baseline has a method-specific attack/recovery evaluation path tied to identity sample indices.
  3. Protocol docs explain how native failures, pilot results, and projection-only checks are handled.
  4. Smoke-scale acceptance criteria exist before long attack sweeps.
**Plans**: 3 plans

Plans (completed through quick tasks):
- [x] 02-01: Specify common attack schema and metric contracts.
- [x] 02-02: Map attack feasibility and constraints per baseline.
- [x] 02-03: Define smoke and formal sweep configurations.

### Phase 3: Attack Runner Implementation
**Goal**: Implement runners that apply selected attacks to stego artifacts and evaluate recovery degradation with structured outputs.
**Depends on**: Phase 2
**Requirements**: RUN-01, RUN-02, RUN-03, RUN-04
**Success Criteria** (what must be TRUE):
  1. Attack runners are deterministic, resumable, and write manifests/results/failures.
  2. Smoke runs complete for at least one bit-payload and one image-payload method.
  3. Runner code reads identity metadata rather than mutating identity outputs.
  4. Failures are logged per sample without aborting entire sweeps.
**Plans**: 4 plans

Plans (completed through quick tasks):
- [x] 03-01: Add shared attack metadata/result utilities.
- [x] 03-02: Implement first image-payload attack runner path.
- [x] 03-03: Implement first bit-payload attack runner path.
- [x] 03-04: Add smoke commands and failure/resume checks.

### Phase 4: Evaluation And Analysis
**Goal**: Produce interpretable attack results showing message destruction, image quality, and deviations from identity baselines.
**Depends on**: Phase 3
**Requirements**: EVAL-01, EVAL-02, EVAL-03, EVAL-04
**Success Criteria** (what must be TRUE):
  1. Evaluation scripts aggregate per-method identity and attacked metrics.
  2. Reports separate exact recovery, bit/image recovery quality, stego perturbation quality, native failures, and pilots.
  3. Paper comparison notes include settings and explain differences from original reported metrics.
  4. Summary docs are sufficient to restart or review experiments without reading raw logs first.
**Plans**: 3 plans

Plans:
- [ ] 04-01: Build aggregation scripts for identity-vs-attacked metrics.
- [ ] 04-02: Generate method tables and caveat-aware summaries.
- [ ] 04-03: Add paper comparison notes and interpretation.

### Phase 5: Reproducibility And Release Hygiene
**Goal**: Keep the project recoverable across sessions and reviewable on GitHub without leaking large artifacts into git.
**Depends on**: Phase 4
**Requirements**: OPS-01, OPS-02, OPS-03, OPS-04
**Success Criteria** (what must be TRUE):
  1. `.planning/STATE.md` points to current phase, result roots, and next commands.
  2. README/docs explain how to reproduce key smokes and where large outputs live.
  3. Git status is clean after docs/scripts/planning updates are committed and pushed.
  4. The broken GSD SDK wrapper is either repaired or documented with a workaround.
**Plans**: 3 plans

Plans:
- [ ] 05-01: Refresh project docs and run manifests.
- [ ] 05-02: Verify git ignores and no large artifacts are staged.
- [ ] 05-03: Repair or document GSD SDK fallback path.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Identity Baseline Finalization | 3/3 | Complete | 2026-05-27 |
| 2. Attack Protocol Design | 3/3 | Complete | 2026-05-27 |
| 3. Attack Runner Implementation | 4/4 | Complete | 2026-05-27 |
| 4. Evaluation And Analysis | 1/3 | In progress | - |
| 5. Reproducibility And Release Hygiene | 1/3 | In progress | - |
