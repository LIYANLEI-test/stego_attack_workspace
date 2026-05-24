# MAS/GRDH Baseline

MAS/GRDH refers to the published TIFS 2024 method:

```text
Establishing Robust Generative Image Steganography via Popular Stable Diffusion
```

Official code:

```text
references/mas_GRDH
https://github.com/HXX5656/mas_GRDH
```

## Native Path

The official code path uses the original Stable Diffusion `ldm` layout and its
DPM-Solver sampler script:

```text
references/mas_GRDH/scripts/txt2img.py
```

Run the native smoke with:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  bash scripts/run_mas_grdh_native_smoke.sh
```

Prepared native assets:

```text
/data2/liyanlei/stego_attack_models/mas_grdh/v1-5-pruned.ckpt
/data2/liyanlei/stego_attack_models/mas_grdh/clip/clip-vit-large-patch14-local
/home/liyanlei/work/stego_attack_workspace/configs/mas_grdh_native_ldm.yaml
```

The runner calls `scripts/prepare_mas_grdh_native.py` first to create the local
config that points the official code at the prepared checkpoint and CLIP files.

## Verified Smoke

Previous 2-step smoke loaded the official `txt2img.py`, generated an image
under:

```text
/data2/liyanlei/stego_attack_data/baselines/mas_grdh/native_official_smoke
```

It printed average accuracy around `0.898`. This is only a wiring check; use
larger DPM steps and more prompts for formal native evaluation.

## Identity Runner

The identity runner follows the official `txt2img.py` path: mapping-module
secret encoding, DPM-Solver generation, selected attack layer, VAE encode,
DPM-Solver inversion, mapping-module decode, and official `cal_acc` reporting.
The local runner supplies deterministic protocol bits instead of the official
script's random secret.

Formal command:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_mas_grdh_identity.py \
  --count 500 --dpm-steps 20 --scale 5.0 \
  --attack-layer identity --attack-factor 0.0 --save-images \
  --output-dir /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/mas_grdh
```

Output:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/mas_grdh/identity_results.csv
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/mas_grdh/manifest.json
```

## Note

The public checkout did not include `ldm/lr_scheduler.py`, while the official
YAML target references `ldm.lr_scheduler.LambdaLinearScheduler`. The workspace
contains a small compatibility shim at:

```text
references/mas_GRDH/ldm/lr_scheduler.py
```

This does not change the embedding method.
