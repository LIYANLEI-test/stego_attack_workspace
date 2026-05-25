# Requirements: Stego Attack Workspace

**Defined:** 2026-05-25
**Core Value:** Produce reproducible, paper-aligned attack experiments that preserve each baseline's native semantics and clearly separate official, third-party, reference, pilot, and non-paper variants.

## v1 Requirements

### Baseline Provenance

- [ ] **BASE-01**: Each baseline runner calls the native/public repository implementation or is explicitly labeled as third-party/reference/pilot.
- [ ] **BASE-02**: Local adaptations are documented and limited to path, cache, checkpoint, import, logging, and runner plumbing unless marked as a non-paper variant.
- [ ] **BASE-03**: Payload capacity and shape follow each method's native/paper path rather than a cross-method artificial payload.
- [ ] **BASE-04**: Docs identify which outputs are formal identity records, pilot records, smoke tests, or projection-only checks.

### Identity Baselines

- [ ] **ID-01**: Pulsar identity status records all 500 samples, including native failures, without claiming failed samples as successful recovery.
- [ ] **ID-02**: CRoSS identity status records 100 fixed FFHQ image-payload samples with recovery PSNR/SSIM and exact-match metrics.
- [ ] **ID-03**: RGS identity status records 100 fixed FFHQ image-payload samples with indice accuracy, PSNR/SSIM, and exact-match metrics.
- [ ] **ID-04**: GSD CIFAR10 identity status records 500 method-native bit-payload samples with bit accuracy and exact-match metrics.
- [ ] **ID-05**: MAS/GRDH identity status records 500 method-native bit-payload samples with bit accuracy and exact-match metrics.
- [ ] **ID-06**: Diffusion-Stego identity status records MN, MB, MC, and Multi-bits projection checks as projection-only, not full image recovery.
- [ ] **ID-07**: MDDM status remains a `native_third_party` capacity/pilot result until an exact formal path is established.
- [ ] **ID-08**: A concise identity summary document points to result roots, logs, commands, and method-specific caveats without committing large data.

### Attack Protocol

- [ ] **ATT-01**: Attack layers are defined separately from baseline generation and recovery logic.
- [ ] **ATT-02**: Each attack specifies target artifact type, allowed perturbation budget, image-quality metrics, and expected message-destruction metric.
- [ ] **ATT-03**: Attack evaluation compares attacked recovery against the corresponding identity baseline for the same sample index and method.
- [ ] **ATT-04**: Method-specific constraints are documented where a baseline exposes image payloads, bit payloads, latent payloads, ECC, or native failure modes.

### Attack Runners

- [ ] **RUN-01**: Attack runners are resumable and skip already completed sample/method/attack combinations.
- [ ] **RUN-02**: Attack runners write structured manifests, per-sample CSV rows, and failure CSV rows.
- [ ] **RUN-03**: Attack runners never silently rewrite identity results or native baseline code.
- [ ] **RUN-04**: Attack runners support smoke-scale execution before long sweeps.

### Evaluation And Reporting

- [ ] **EVAL-01**: Evaluation reports message recovery degradation using bit accuracy, exact match, image recovery PSNR/SSIM, and method-native metrics where applicable.
- [ ] **EVAL-02**: Evaluation reports image quality or perceptual distortion for attacked stego artifacts.
- [ ] **EVAL-03**: Reports separate official/native, third-party, reference, pilot, projection-only, and failed-native samples.
- [ ] **EVAL-04**: Paper comparison notes include exact settings and explain deviations from original papers.

### Operations

- [ ] **OPS-01**: Large data, generated artifacts, model weights, and logs remain outside git under `/data2/liyanlei/...`.
- [ ] **OPS-02**: Code, configs, docs, summaries, and `.planning/` state are committed and pushed after task updates.
- [ ] **OPS-03**: Future work starts by reading `.planning/STATE.md`, `.planning/PROJECT.md`, and the relevant method docs.
- [ ] **OPS-04**: Broken GSD SDK/tooling is tracked as an operations issue but does not block maintaining `.planning/` state.

## v2 Requirements

### Extended Baselines

- **EXT-01**: Add an official MDDM checkout if one is identified and audit it separately from the current third-party backend.
- **EXT-02**: Replace Diffusion-Stego NS-DSer reference integration with a selected official/public method checkout if required by the final comparison.
- **EXT-03**: Add additional attacks or robustness settings after v1 attack evaluation is reproducible.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Git-tracking generated images, model weights, or full CSV result dumps | These artifacts are large and already belong under `/data2`. |
| Normalizing all methods to one identical payload length | This conflicts with method-native capacity and paper semantics. |
| Calling MDDM official without an audited official repository | Current integrated implementation is third-party. |
| Treating Diffusion-Stego projection checks as full image-generation identity results | Projection checks validate payload mapping only. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BASE-01 | Phase 1 | In Progress |
| BASE-02 | Phase 1 | In Progress |
| BASE-03 | Phase 1 | In Progress |
| BASE-04 | Phase 1 | In Progress |
| ID-01 | Phase 1 | Complete |
| ID-02 | Phase 1 | Complete |
| ID-03 | Phase 1 | In Progress |
| ID-04 | Phase 1 | Complete |
| ID-05 | Phase 1 | Complete |
| ID-06 | Phase 1 | Complete |
| ID-07 | Phase 1 | Complete |
| ID-08 | Phase 1 | Pending |
| ATT-01 | Phase 2 | Pending |
| ATT-02 | Phase 2 | Pending |
| ATT-03 | Phase 2 | Pending |
| ATT-04 | Phase 2 | Pending |
| RUN-01 | Phase 3 | Pending |
| RUN-02 | Phase 3 | Pending |
| RUN-03 | Phase 3 | Pending |
| RUN-04 | Phase 3 | Pending |
| EVAL-01 | Phase 4 | Pending |
| EVAL-02 | Phase 4 | Pending |
| EVAL-03 | Phase 4 | Pending |
| EVAL-04 | Phase 4 | Pending |
| OPS-01 | Phase 5 | Pending |
| OPS-02 | Phase 5 | In Progress |
| OPS-03 | Phase 5 | In Progress |
| OPS-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0

---
*Requirements defined: 2026-05-25*
*Last updated: 2026-05-25 after manual GSD initialization*
