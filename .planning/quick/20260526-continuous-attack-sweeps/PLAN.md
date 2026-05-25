---
status: in_progress
created: 2026-05-26
---

# Continuous Attack Sweeps

Keep running attack pilots until the non-RGS attack result matrix is filled.

## Scope

- RGS attacks remain excluded for now because the user said RGS is too slow.
- Resize and storage pilots are already complete.
- Next unified attack families are the MAS/GRDH README image-domain attacks:
  `jpeg`, `mblur`, and `gblur`.
- Run 10 samples per method/factor first, using any idle GPU.
- Preserve native embedding, sampling, recovery, and payload semantics; only
  insert the shared image-domain attack before native reveal/recovery.
- Commit and push code/docs/planning updates after meaningful progress.

## Current Queue

| Attack | Factors | Methods |
|--------|---------|---------|
| jpeg | 90, 70, 50 | CRoSS, MAS/GRDH, GSD, Pulsar, MDDM pilot |
| mblur | 3, 5, 7 | CRoSS, MAS/GRDH, GSD, Pulsar, MDDM pilot |
| gblur | 3, 5, 7 | CRoSS, MAS/GRDH, GSD, Pulsar, MDDM pilot |

## Verification

- Python runners compile after each attack-family implementation.
- Each result directory has 10 total sample records across result/failure CSVs.
- Results are summarized in docs and `.planning/STATE.md`.
