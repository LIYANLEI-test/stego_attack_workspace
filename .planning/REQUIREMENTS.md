# Requirements: Stego Attack Workspace

**Defined:** 2026-05-25
**Core Value:** Produce reproducible, paper-aligned attack experiments that preserve each baseline's native semantics and clearly separate official, third-party, reference, pilot, and non-paper variants.

## v1 Requirements

### Baseline Provenance

- [x] **BASE-01**: Each baseline runner calls the native/public repository implementation or is explicitly labeled as third-party/reference/pilot.
- [x] **BASE-02**: Local adaptations are documented and limited to path, cache, checkpoint, import, logging, and runner plumbing unless marked as a non-paper variant.
- [x] **BASE-03**: Payload capacity and shape follow each method's native/paper path rather than a cross-method artificial payload.
- [x] **BASE-04**: Docs identify which outputs are formal identity records, pilot records, smoke tests, or projection-only checks.

### Identity Baselines

- [x] **ID-01**: Pulsar identity status records all 500 samples, including native failures, without claiming failed samples as successful recovery.
- [x] **ID-02**: CRoSS identity status records 100 fixed FFHQ image-payload samples with recovery PSNR/SSIM and exact-match metrics.
- [x] **ID-03**: RGS identity status records 100 fixed FFHQ image-payload samples with indice accuracy, PSNR/SSIM, and exact-match metrics.
- [x] **ID-04**: GSD CIFAR10 identity status records 500 method-native bit-payload samples with bit accuracy and exact-match metrics.
- [x] **ID-05**: MAS/GRDH identity status records 500 method-native bit-payload samples with bit accuracy and exact-match metrics.
- [x] **ID-06**: Diffusion-Stego is removed from active identity and attack baselines because only projection-only NS-DSer checks were available.
- [x] **ID-07**: MDDM status remains a `native_third_party` capacity/pilot result until an exact formal path is established.
- [x] **ID-08**: A concise identity summary document points to result roots, logs, commands, and method-specific caveats without committing large data.

### Attack Protocol

- [x] **ATT-01**: Attack layers are defined separately from baseline generation and recovery logic.
- [x] **ATT-02**: Each attack specifies target artifact type, allowed perturbation budget, image-quality metrics, and expected message-destruction metric.
- [x] **ATT-03**: Attack evaluation compares attacked recovery against the corresponding identity baseline for the same sample index and method.
- [x] **ATT-04**: Method-specific constraints are documented where a baseline exposes image payloads, bit payloads, latent payloads, ECC, or native failure modes.

### Attack Runners

- [x] **RUN-01**: Attack runners are resumable and skip already completed sample/method/attack combinations.
- [x] **RUN-02**: Attack runners write structured manifests, per-sample CSV rows, and failure CSV rows.
- [x] **RUN-03**: Attack runners never silently rewrite identity results or native baseline code.
- [x] **RUN-04**: Attack runners support smoke-scale execution before long sweeps.

### Evaluation And Reporting

- [ ] **EVAL-01**: Evaluation reports message recovery degradation using bit accuracy, exact match, image recovery PSNR/SSIM, and method-native metrics where applicable.
- [ ] **EVAL-02**: Evaluation reports image quality or perceptual distortion for attacked stego artifacts.
- [ ] **EVAL-03**: Reports separate official/native, third-party, reference, pilot, projection-only, and failed-native samples.
- [ ] **EVAL-04**: Paper comparison notes include exact settings and explain deviations from original papers.

### Operations

- [x] **OPS-01**: Large data, generated artifacts, model weights, and logs remain outside git under `/data2/liyanlei/...`.
- [ ] **OPS-02**: Code, configs, docs, summaries, and `.planning/` state are committed and pushed after task updates.
- [ ] **OPS-03**: Future work starts by reading `.planning/STATE.md`, `.planning/PROJECT.md`, and the relevant method docs.
- [ ] **OPS-04**: Broken GSD SDK/tooling is tracked as an operations issue but does not block maintaining `.planning/` state.

## v2 Requirements

### Extended Baselines

- **EXT-01**: Add an official MDDM checkout if one is identified and audit it separately from the current third-party backend.
- **EXT-02**: Reconsider Diffusion-Stego only if a selected official/public full image-generation/reveal implementation is identified and audited.
- **EXT-03**: Add additional attacks or robustness settings after v1 attack evaluation is reproducible.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Git-tracking generated images, model weights, or full CSV result dumps | These artifacts are large and already belong under `/data2`. |
| Normalizing all methods to one identical payload length | This conflicts with method-native capacity and paper semantics. |
| Calling MDDM official without an audited official repository | Current integrated implementation is third-party. |
| Reintroducing Diffusion-Stego projection checks as active identity results | Projection checks validate payload mapping only and are no longer part of the project. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BASE-01 | Phase 1 | Complete |
| BASE-02 | Phase 1 | Complete |
| BASE-03 | Phase 1 | Complete |
| BASE-04 | Phase 1 | Complete |
| ID-01 | Phase 1 | Complete |
| ID-02 | Phase 1 | Complete |
| ID-03 | Phase 1 | Complete |
| ID-04 | Phase 1 | Complete |
| ID-05 | Phase 1 | Complete |
| ID-06 | Phase 1 | Complete |
| ID-07 | Phase 1 | Complete |
| ID-08 | Phase 1 | Complete |
| ATT-01 | Phase 2 | Complete |
| ATT-02 | Phase 2 | Complete |
| ATT-03 | Phase 2 | Complete |
| ATT-04 | Phase 2 | Complete |
| RUN-01 | Phase 3 | Complete |
| RUN-02 | Phase 3 | Complete |
| RUN-03 | Phase 3 | Complete |
| RUN-04 | Phase 3 | Complete |
| EVAL-01 | Phase 4 | In Progress |
| EVAL-02 | Phase 4 | In Progress |
| EVAL-03 | Phase 4 | In Progress |
| EVAL-04 | Phase 4 | Pending |
| OPS-01 | Phase 5 | Complete |
| OPS-02 | Phase 5 | In Progress |
| OPS-03 | Phase 5 | In Progress |
| OPS-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0

---
*Requirements defined: 2026-05-25*
*Last updated: 2026-05-28 after removing Diffusion-Stego from active baselines*
