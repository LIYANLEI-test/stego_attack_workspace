---
status: complete
completed: 2026-05-25
---

# Resize Attack Pilot Summary

The MAS/GRDH native resize attack pilot completed on GPU 0.

Run:

```text
method=mas_grdh
attack_layer=resize
attack_factor=0.5
count=10
dpm_gen_steps=20
dpm_inv_steps=20
scale=5.0
```

Results:

```text
rows=10
failures=0
identity_mean_bit_accuracy_samples_0_9=0.953400
resize_mean_bit_accuracy_samples_0_9=0.890216
mean_delta=-0.063184
resize_exact=0/10
mean_runtime_s=21.49
```

Output root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/resize_pilot_20260525/mas_grdh_resize_0_5_10
```

Code change:

```text
scripts/run_mas_grdh_identity.py now creates the temporary directory before calling official robust_eval attack layers.
```
