# Resize Attack Pilot - 2026-05-25

## Scope

First resize-attack pilot on a native baseline path.

Method:

```text
MAS/GRDH (`native_official`)
```

Runner:

```text
scripts/run_mas_grdh_identity.py
```

Native attack layer:

```text
references/mas_GRDH/scripts/robust_eval.py::resize
```

The local runner only creates the temporary output directory before calling the
official attack function. This is runner path plumbing and does not change the
resize attack semantics.

## Command

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH CUDA_VISIBLE_DEVICES=0 \
  HF_HOME=/data2/liyanlei/huggingface \
  HUGGINGFACE_HUB_CACHE=/data2/liyanlei/huggingface/hub \
  TRANSFORMERS_CACHE=/data2/liyanlei/huggingface/transformers \
  HF_ENDPOINT=https://hf-mirror.com \
  PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_mas_grdh_identity.py \
  --count 10 --dpm-steps 20 --scale 5.0 \
  --attack-layer resize --attack-factor 0.5 \
  --gpu cuda:0 \
  --output-dir /data2/liyanlei/stego_attack_data/attack_runs/resize_pilot_20260525/mas_grdh_resize_0_5_10 \
  --force
```

Output:

```text
/data2/liyanlei/stego_attack_data/attack_runs/resize_pilot_20260525/mas_grdh_resize_0_5_10
```

Log:

```text
/data2/liyanlei/stego_attack_data/attack_runs/resize_pilot_20260525/logs/mas_grdh_resize_0_5_10.log
```

## Result

Compared against the same MAS/GRDH identity samples 0-9:

| Metric | Value |
|--------|-------|
| Samples | 10 |
| Failures | 0 |
| Resize factor | 0.5 |
| DPM gen/inv steps | 20 / 20 |
| Scale | 5.0 |
| Identity mean bit accuracy, samples 0-9 | 0.953400 |
| Resize mean bit accuracy, samples 0-9 | 0.890216 |
| Mean delta vs identity | -0.063184 |
| Resize median bit accuracy | 0.905121 |
| Resize min bit accuracy | 0.792542 |
| Resize max bit accuracy | 0.934875 |
| Resize exact match | 0/10 |
| Mean runtime | 21.49 s/sample |

Per-sample comparison:

| Sample | Identity bit acc | Resize bit acc | Delta |
|--------|------------------|----------------|-------|
| 0 | 0.953979 | 0.876038 | -0.077942 |
| 1 | 0.965881 | 0.915161 | -0.050720 |
| 2 | 0.980164 | 0.934875 | -0.045288 |
| 3 | 0.993530 | 0.921631 | -0.071899 |
| 4 | 0.933655 | 0.837280 | -0.096375 |
| 5 | 0.945801 | 0.895081 | -0.050720 |
| 6 | 0.846680 | 0.792542 | -0.054138 |
| 7 | 0.957764 | 0.883667 | -0.074097 |
| 8 | 0.969910 | 0.929138 | -0.040771 |
| 9 | 0.986633 | 0.916748 | -0.069885 |

## Interpretation

This is only a 10-sample pilot, not a formal sweep. It confirms that the native
MAS/GRDH resize attack path runs end-to-end in this workspace and degrades
message recovery relative to same-sample identity by about 6.3 percentage
points at factor 0.5.

The official MAS/GRDH README lists resize factors `0.5`, `0.75`, `1.25`, and
`1.5`. A formal comparison should run all factors with the selected sample
count after the attack protocol is locked.
