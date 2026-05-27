---
status: complete
created: 2026-05-27
completed: 2026-05-27T09:55:00+08:00
---

# Held-Out Formal Evaluation

Prevent parameter-selection leakage in the selected quality-budget paper
tables.

## Tasks

1. Treat `sample_index 0-9` as calibration-only because those samples selected
   the fixed attack parameters.
2. Make selected formal summary and paired delta tables exclude calibration
   samples by default.
3. Record the evaluation split in result CSVs and experiment manifests.
4. Audit PSNR/LPIPS coverage so failures cannot silently disappear from the
   image-quality budget.
5. Score failed reveals as zero only when a saved attacked image pair exists,
   and expose attack versus baseline provenance separately.

## Acceptance

- Formal rows default to held-out indices `10+`.
- Completed CRoSS selected attacks report `90/90`, not `100/100`.
- Quality-budget audit reports missing LPIPS as partial during live monitoring
  and checks complete PSNR/LPIPS coverage in final reports.
- Unscorable runner failures do not count as payload destruction or formal
  completeness.
- The active queue remains untouched; only reporting semantics change.
