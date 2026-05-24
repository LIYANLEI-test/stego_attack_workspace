# Native Generation Status

Current project rule:

```text
native original-repository generation only, as far as practical
```

The generated stego images are attack objects for message-destruction research.
The steganography generation side should stay as close as possible to each
published method's own public code. Earlier workspace-level SD1.5/SD3
adaptations have been removed. Diffusion-Stego is the one exception here: it is
integrated from the supplied NS-DSer reference implementation because no
separate official repository is currently selected.

## Summary

| Method | Status | Runnable entry | Large assets |
|---|---|---|---|
| CRoSS | `native_official` | `scripts/generate_cross_sample.py` | SD1.5 diffusers cache under `/data2/liyanlei/huggingface` |
| Pulsar | `native_official` | `scripts/run_pulsar_native_regions_sample.py` | Google DDPM cache under `/data2/liyanlei/huggingface` |
| GSD | `native_official` | `scripts/run_gsd_native_smoke.sh` | DDPM and CelebA-64 checkpoints under `/data2/liyanlei/stego_attack_models/gsd` |
| MAS/GRDH | `native_official` | `scripts/run_mas_grdh_native_smoke.sh` | SD1.5 `.ckpt` and CLIP under `/data2/liyanlei/stego_attack_models/mas_grdh` |
| MDDM | `native_third_party` | `scripts/run_mddm_thirdparty_sample.py` | SD1.5 diffusers cache under `/data2/liyanlei/huggingface` |
| Diffusion-Stego | `nsdser_reference` | `scripts/run_diffusion_stego_nsdser_sample.py` | NS-DSer local SD1.5 and `/data2/liyanlei/huggingface` |
| RGS | `native_official` | `scripts/run_rgs_native_sample.py` | VQGAN, SD1.5-bin, and CLIP under `/data2/liyanlei/stego_attack_models` |

## Verified Smokes

Pulsar official Sage/region path:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH HF_HOME=/data2/liyanlei/huggingface \
  HUGGINGFACE_HUB_CACHE=/data2/liyanlei/huggingface/hub \
  HF_ENDPOINT=https://hf-mirror.com \
  PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_pulsar_native_regions_sample.py \
  --steps 50 --region-estimate-samples 1 --hist-bins 100 \
  --model bedroom --scheduler ddim \
  --output-dir /data2/liyanlei/stego_attack_data/baselines/pulsar/native_regions_verify_50step
```

Previous result:

```text
capacity_bytes=228
bit_accuracy=1.000000
message_matches=True
```

MAS/GRDH official script smoke:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  bash scripts/run_mas_grdh_native_smoke.sh
```

Previous result:

```text
official txt2img.py loaded SD1.5 ckpt
average accuracy: about 0.898 in the latest 2-step storage smoke
output image: /data2/liyanlei/stego_attack_data/baselines/mas_grdh/native_official_smoke/tmp_001_storage_00.png
manifest: /data2/liyanlei/stego_attack_data/baselines/mas_grdh/native_official_smoke/manifest.json
```

MDDM third-party pipeline:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_mddm_thirdparty_sample.py \
  --steps 2 --seed 2 \
  --output-dir /data2/liyanlei/stego_attack_data/baselines/mddm/thirdparty_native_smoke_2step
```

Previous result:

```text
bit_accuracy=1.000000
exact_match=True
```

GSD native CIFAR10 DDPM:

```sh
cd /home/liyanlei/work/stego_attack_workspace
bash scripts/run_gsd_native_smoke.sh
```

Previous smoke completed native `--reverse_dct` sampling and reported bit
accuracy around `0.9166` with 2 timesteps.

CRoSS official demo wrapper:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/generate_cross_sample.py \
  --num-steps 2 \
  --output-dir /data2/liyanlei/stego_attack_data/baselines/cross/native_official_smoke_2step
```

Previous result:

```text
stego image: /data2/liyanlei/stego_attack_data/baselines/cross/native_official_smoke_2step/hide.png
recovered image: /data2/liyanlei/stego_attack_data/baselines/cross/native_official_smoke_2step/reverse.png
manifest: /data2/liyanlei/stego_attack_data/baselines/cross/native_official_smoke_2step/manifest.json
```

Diffusion-Stego NS-DSer reference runner:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_diffusion_stego_nsdser_sample.py \
  --mapping mn --steps 2 --seeds 0
```

Use `--mapping mn`, `--mapping mb`, `--mapping mc`, or
`--mapping multi_bits`.

RGS official hide-and-reveal path:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_rgs_native_sample.py \
  --steps 2 --hide-only \
  --output-dir /data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step
```

Current smoke result:

```text
secret image: /data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step/results/00000/00000_secret.png
stego image: /data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step/results/00000/00000_stego.png
noise file: /data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step/results/00000/00000_noise.pkl
manifest: /data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step/manifest.json
size: 512x512 RGB
```

The official README says one full hide-and-reveal image can take about 5
minutes. The 2-step `--hide-only` command above is only a capability smoke; use
more steps and omit `--hide-only` when evaluating reveal quality.

## Downloaded / Prepared Assets

MAS/GRDH native assets:

```text
/data2/liyanlei/stego_attack_models/mas_grdh/v1-5-pruned.ckpt
/data2/liyanlei/stego_attack_models/mas_grdh/sd15/v1-5-pruned-emaonly.ckpt
/data2/liyanlei/stego_attack_models/mas_grdh/clip/clip-vit-large-patch14-local
/home/liyanlei/work/stego_attack_workspace/configs/mas_grdh_native_ldm.yaml
```

GSD native DDPM assets:

```text
/data2/liyanlei/stego_attack_models/gsd/ddim_cache/diffusion_models_converted/ema_diffusion_cifar10_model/model-790000.ckpt
/data2/liyanlei/stego_attack_models/gsd/ddim_cache/diffusion_models_converted/ema_diffusion_lsun_bedroom_model/model-2388000.ckpt
/data2/liyanlei/stego_attack_models/gsd/celeba-64/ckpt.pth
```

The CelebA-64 checkpoint is linked into the public GSD checkout at both paths
needed by the repository:

```text
references/GSD/out/logs/celeba-64/ckpt.pth
references/GSD/out/logs/bedroom-64/ckpt.pth
```

RGS native assets:

```text
/data2/liyanlei/stego_attack_models/rgs/vqgan_code1024.pth
/data2/liyanlei/stego_attack_models/rgs/sd15-bin
/data2/liyanlei/stego_attack_models/mas_grdh/clip/clip-vit-large-patch14-local
```

## Notes

MAS/GRDH official code references `ldm.lr_scheduler.LambdaLinearScheduler`, but
the public checkout did not include `ldm/lr_scheduler.py`. A small compatibility
shim exists at:

```text
references/mas_GRDH/ldm/lr_scheduler.py
```

This is not a method reimplementation; it only satisfies the official YAML
target so the public script can load.

MDDM official author code was not found. The `RGlodAkshat` repository remains
labelled `native_third_party`, not `native_official`.

Diffusion-Stego uses the NS-DSer reference code at:

```text
/home/liyanlei/work/NS-DSer-master/NS-DSer-master/utils/projection.py
```

Keep it labelled `nsdser_reference`, not `native_official`.
