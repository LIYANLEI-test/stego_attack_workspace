---
status: paused
created: 2026-05-26
paused: 2026-05-26T13:23:18+08:00
pause_reason: user judged the current baseline set too small/weak for final comparison
---

# Identity-Scale Attack Sweeps

Run the comparable non-RGS attack matrix beyond the 10-sample pilots, using
the current identity/pilot scale for each runnable method.

This task is now paused. The user judged the current baseline set too
small/weak, so the queue must not be resumed until the baseline set is
reassessed and strengthened.

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

Stopped queue:

```text
stopped: 2026-05-26 13:23 CST
reason: user paused because the baseline set is too small/weak
status: no matching queue or method runner processes remained at the pause check
```

Checkpoint:

```text
2026-05-26 13:23 CST:
resize_0.5 and resize_0.75 completed for CRoSS, GSD CIFAR10, MAS/GRDH, Pulsar, and MDDM pilot.
resize_1.25 is partial; CRoSS and MDDM pilot are complete, GSD/MAS/GRDH/Pulsar are partial.
resize_1.5 is partial with CRoSS only.
storage/JPEG/median-blur/Gaussian-blur formal-scale items did not start in this queue.
No duplicate sample IDs detected by summarize_unified_attack_runs.py.
```

Paused summary:

| Method | Attack | Factor | Done | Failures/Empty | Primary metric |
|--------|--------|--------|------|----------------|----------------|
| CRoSS | resize | 0.5 | 100/100 | 0 | recovery PSNR 19.996824 |
| CRoSS | resize | 0.75 | 100/100 | 0 | recovery PSNR 20.921217 |
| CRoSS | resize | 1.25 | 100/100 | 0 | recovery PSNR 21.743084 |
| CRoSS | resize | 1.5 | 11/100 | 0 | recovery PSNR 19.955780 |
| GSD CIFAR10 | resize | 0.5 | 500/500 | 0 | bit accuracy 0.588711 |
| GSD CIFAR10 | resize | 0.75 | 500/500 | 0 | bit accuracy 0.676061 |
| GSD CIFAR10 | resize | 1.25 | 181/500 | 0 | bit accuracy 0.763598 |
| MAS/GRDH | resize | 0.5 | 500/500 | 0 | bit accuracy 0.896614 |
| MAS/GRDH | resize | 0.75 | 500/500 | 0 | bit accuracy 0.937157 |
| MAS/GRDH | resize | 1.25 | 309/500 | 0 | bit accuracy 0.952522 |
| MDDM 128-byte pilot | resize | 0.5 | 50/50 | 0 | bit accuracy 0.981445 |
| MDDM 128-byte pilot | resize | 0.75 | 50/50 | 0 | bit accuracy 0.994941 |
| MDDM 128-byte pilot | resize | 1.25 | 50/50 | 0 | bit accuracy 0.998320 |
| Pulsar | resize | 0.5 | 500/500 | 493 failures, 7 zero-bit rows | no meaningful bit-accuracy mean |
| Pulsar | resize | 0.75 | 500/500 | 493 failures, 7 zero-bit rows | no meaningful bit-accuracy mean |
| Pulsar | resize | 1.25 | 195/500 | 192 failures, 3 zero-bit rows | no meaningful bit-accuracy mean |

## Baseline Re-Scope Gate

Do not resume the command above until the baseline set has been accepted as
strong enough for the intended comparison. At minimum, the next planning step
should decide:

- Which additional official/public steganography baselines to add.
- Whether current MDDM should be replaced/supplemented with official code.
- Whether Diffusion-Stego should be implemented as full generation/reveal or
  excluded from image-domain attacks.
- Whether RGS attacks should stay skipped for speed or be included after all.
- How to label each method so native, third-party, pilot, and projection-only
  results are never mixed silently.

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
