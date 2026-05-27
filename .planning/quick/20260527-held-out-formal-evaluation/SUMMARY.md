---
status: complete
created: 2026-05-27
completed: 2026-05-27T09:55:00+08:00
---

# Summary

Separated attack calibration from formal evaluation.

The selected attack parameters were chosen using sample indices `0-9`. Formal
summary, delta, paper-table, and audit paths now exclude those indices by
default. With the existing deterministic protocol, held-out table sizes are:

```text
CRoSS: 90
GSD CIFAR10: 490
MAS/GRDH: 490
MDDM 128-byte pilot: 40
Pulsar: 490
```

The active generation queue still writes its planned `100/500/50` outputs so
the calibration records remain available for traceability; they are not
included in formal claims.

The queue progress snapshot now exposes raw generated counts separately from
formal held-out counts, so a live run cannot accidentally be cited with the
calibration records included.

Failure scoring is also tightened: native failure contributes zero payload
recovery only when the stego/attacked image pair exists for quality
measurement. Other failures are surfaced as unscorable and keep a formal row
incomplete. Reports now distinguish baseline implementation provenance from
adapted attack provenance and include a conditional delta over identity
successes for methods with native identity failures. The readiness audit also
retains incomplete and unscorable rows so failed experiments cannot disappear
from final review; the rendered readiness tables follow the same rule.

Verification:

```text
scripts/summarize_selected_attack_runs.py: completed CRoSS rows report 90/90
scripts/summarize_attack_deltas.py: completed CRoSS overlap reports 90
python -m py_compile selected reporting and runner scripts
python -m unittest discover -s tests -v
git diff --check
```
