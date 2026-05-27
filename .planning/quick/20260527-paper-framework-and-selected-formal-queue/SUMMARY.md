---
status: complete
created: 2026-05-27
completed: 2026-05-27T16:20:00+08:00
---

# Summary

Added the paper-grade selected-attack framework:

```text
docs/paper_experiment_framework_20260527.md
scripts/selected_attack_matrix.py
scripts/run_selected_attack_queue.py
scripts/monitor_selected_attack_queue.py
scripts/summarize_selected_attack_runs.py
```

The formal queue runs 18 selected quality-budget attack jobs:

```text
CRoSS: 5 attacks x 100 samples
GSD CIFAR10: 4 attacks x 500 samples
MAS/GRDH: 3 attacks x 500 samples
MDDM 128-byte pilot: 1 attack x 50 samples
Pulsar: 5 attacks x 500 samples
```

Verification completed:

```text
python -m py_compile selected queue/summary scripts and method runners
scripts/run_selected_attack_queue.py --dry-run
scripts/summarize_selected_attack_runs.py on empty output root
scripts/monitor_selected_attack_queue.py --once
git diff --check
```

The framework is ready to launch the formal selected-attack queue under:

```text
/data2/liyanlei/stego_attack_data/attack_runs/selected_quality_budget_20260527
```

As of the follow-up update, the queue has been launched and the monitor can
refresh live reports and write final reports when the queue finishes.
