---
status: in_progress
created: 2026-05-26
---

# Identity-Scale Attack Sweeps

Run the comparable non-RGS attack matrix beyond the 10-sample pilots, using
the current identity/pilot scale for each runnable method.

## Scope

- Keep RGS attack runs excluded unless explicitly re-enabled; RGS identity is
  complete but each attack run is too slow for the current queue.
- Keep Diffusion-Stego excluded from image attacks because the integrated path
  is projection-only, not full generated-image reveal.
- Preserve native method payloads, embedding, sampling, and reveal/recovery
  semantics; only insert a shared image-domain attack between stego generation
  and native recovery.
- Keep large outputs under `/data2/liyanlei/stego_attack_data/attack_runs/`.
- Commit and push scripts/planning/docs after meaningful updates.

## Queue

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unified_identity_scale_20260526
```

Method counts:

| Method | Count | Reason |
|--------|-------|--------|
| CRoSS | 100 | Formal image-payload identity set size |
| GSD CIFAR10 | 500 | Formal bit-payload identity set size |
| MAS/GRDH | 500 | Formal bit-payload identity set size |
| Pulsar | 500 | Formal identity ledger size, including native failures |
| MDDM 128-byte pilot | 50 | Current audited pilot size |

Attack settings:

| Attack | Factors |
|--------|---------|
| resize | 0.5, 0.75, 1.25, 1.5 |
| storage | lossless PNG round trip |
| jpeg | 90, 70, 50 |
| mblur | 3, 5, 7 |
| gblur | 3, 5, 7 |

Runner command:

```bash
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python scripts/run_unified_attack_queue.py \
  --root /data2/liyanlei/stego_attack_data/attack_runs/unified_identity_scale_20260526 \
  --identity-scale \
  --attacks resize,storage,jpeg,mblur,gblur \
  --gpus 0,1,2,3 \
  --poll-seconds 10
```

Launched queue:

```text
started: 2026-05-26 05:33 CST
pid: 8858
driver log: /data2/liyanlei/stego_attack_data/attack_runs/unified_identity_scale_20260526/logs/queue_driver.log
initial jobs: cross_resize_0_5_100, gsd_cifar10_resize_0_5_500, mas_grdh_resize_0_5_500, pulsar_resize_0_5_500
```

Checkpoint:

```text
2026-05-26 10:43 CST:
resize_0.5 completed for CRoSS, GSD CIFAR10, MAS/GRDH, Pulsar, and MDDM pilot.
resize_0.75 is partially complete/in progress; resize_1.25 has started with CRoSS.
No duplicate sample IDs detected by summarize_unified_attack_runs.py.
```

## Verification

- `scripts/run_unified_attack_queue.py` compiles.
- Queue expansion passes a command-shape check for resize, storage, and lossy
  attack flags.
- `scripts/summarize_unified_attack_runs.py` summarizes live or completed run
  roots and excludes zero-bit Pulsar rows from bit-accuracy means.
- Result directories are considered complete when results plus failures equal
  the per-method target count and sample IDs have no duplicates.
- Final docs summarize counts, failures, and primary metrics without committing
  raw CSVs or generated images.
