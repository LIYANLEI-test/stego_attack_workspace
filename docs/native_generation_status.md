# Native Generation Status

Current project rule:

```text
native original-repository generation only, as far as practical
```

The generated stego images are attack objects for message-destruction research.
The steganography generation side should stay as close as possible to each
published method's own public code. Earlier workspace-level SD1.5/SD3
adaptations have been removed. Diffusion-Stego has also been removed from the
active project because the available NS-DSer path was projection-only, not a
full image-generation/reveal baseline.

Local compatibility adaptations are acceptable only when they preserve the
original method semantics and expected paper behavior. Path plumbing, cache
locations, checkpoint links, missing import shims, runner logging, and exposing
existing paper parameters as CLI options are acceptable. Changes to embedding,
sampling, inversion, decoding, ECC, payload mapping, or metric logic are not
acceptable unless explicitly recorded as a non-paper variant.

## Summary

| Method | Status | Runnable entry | Large assets |
|---|---|---|---|
| CRoSS | `native_official` | `scripts/run_cross_identity.py` | SD1.5 diffusers cache under `/data2/liyanlei/huggingface` |
| Pulsar | `native_official` | `scripts/run_pulsar_identity.py` | Google DDPM cache under `/data2/liyanlei/huggingface` |
| GSD | `native_official` | `scripts/run_gsd_identity.py` | DDPM and CelebA-64 checkpoints under `/data2/liyanlei/stego_attack_models/gsd` |
| MAS/GRDH | `native_official` | `scripts/run_mas_grdh_identity.py` | SD1.5 `.ckpt` and CLIP under `/data2/liyanlei/stego_attack_models/mas_grdh` |
| MDDM | `native_third_party` | `scripts/run_mddm_identity.py` | SD1.5 diffusers cache under `/data2/liyanlei/huggingface` |
| RGS | `native_official` | `scripts/run_rgs_identity.py` | VQGAN, SD1.5-bin, and CLIP under `/data2/liyanlei/stego_attack_models` |
| Diffusion-Stego | `removed` | none | old projection-only outputs are archival only |

## Identity Run Status

Protocol:

```text
/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522
```

Result root:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522
```

Completed formal or formal-like identity records:

```text
pulsar/identity_results.csv
  461 successful samples, all exact; 39 native failures recorded in identity_failures.csv.
  Total recorded: 500/500 sample indices.

cross/identity_results.csv
  100/100 image-payload samples; mean recovered-secret PSNR 21.955770 dB.

rgs/identity_results.csv
  100/100 image-payload samples with 0 failures; mean recovered-secret PSNR 23.316454 dB.

gsd_cifar10/identity_results.csv
  500/500 bit-payload samples; mean bit accuracy 0.874217.

mas_grdh/identity_results.csv
  500/500 bit-payload samples; mean bit accuracy 0.958325.

mddm_128_pilot/identity_results.csv
  50/50 records; mean bit accuracy 0.999180.
  This remains a native_third_party pilot/appendix result.
```

Removed archival records:

```text
diffusion_stego_*_projection/identity_results.csv
  Old NS-DSer Projection encode/decode checks only. These are no longer active
  identity baselines and must not be used in attack tables.
```

Identity logs and retained PID-file locations:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/cross_identity.log
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/cross_identity.pid
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/rgs_identity.log
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/rgs_identity.pid
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/gsd_cifar10_identity.log
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/gsd_cifar10_identity.pid
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/mas_grdh_identity.log
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/mas_grdh_identity.pid
```

MDDM remains a third-party pilot path. Earlier 2048-byte and 256-byte runs were
not reliably exact, so do not treat full-size MDDM identity as complete without
a larger successful pilot and a clear `native_third_party` label.

Completed MDDM pilot:

```text
mddm_128_pilot 50 messages, 128 printable ASCII bytes, steps 20, guidance scale 1.0
log: /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/mddm_128_pilot.log
pid: /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/logs/mddm_128_pilot.pid
```

This pilot is not a formal official identity baseline. It includes
high-accuracy non-exact recoveries, so MDDM stays outside primary claims unless
an official implementation is selected and audited separately.

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

Diffusion-Stego is removed from active baselines. The former NS-DSer projection
checks did not provide a full generated-image reveal path.
