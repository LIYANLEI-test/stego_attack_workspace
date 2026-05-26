---
status: complete
created: 2026-05-27
completed: 2026-05-27T15:40:00+08:00
---

# Quality-Budget Attack Selection

Select fair attack parameters for each runnable generation/recovery method
under a shared stego-vs-attacked image-quality budget.

## Tasks

1. Patch result capture so attacked image paths are available for quality
   metrics, including Pulsar native reveal failures.
2. Run 10-sample grids for the confirmed attacks and methods under a fixed
   quality budget.
3. Select the strongest in-budget parameter per method/attack, document the
   results, and update project state.

## Quality Budget

```text
PSNR >= 30 dB
LPIPS <= 0.10
```

## Acceptance

- Runners save stego and attacked image paths where needed.
- Native reveal failures after saved attacked images count as payload recovery
  failures, not missing records.
- The selection CSV and docs identify the chosen parameter per method/attack.
- Large generated artifacts remain under `/data2/liyanlei/...`, outside git.
