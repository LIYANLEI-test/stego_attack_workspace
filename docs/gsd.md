# GSD Baseline

GSD is the published method from:

```text
Improved Generative Steganography Based on Diffusion Model
```

Public code:

```text
references/GSD
https://github.com/zqqq2/Improved-Generative-Steganography-Based-on-Diffusion-Model-code-2025
```

## Native Path

The public GSD repository is based on a DDIM/DDPM codebase. Its steganographic
sampling entry is `--reverse_dct`, implemented by `sample_reverse_dct` in:

```text
references/GSD/runners/diffusion.py
```

Native GSD uses dataset-specific diffusion checkpoints. It is not a Stable
Diffusion prompt-to-image method. No image dataset is needed for sampling once
the checkpoint is available.

Run the native smoke:

```sh
cd /home/liyanlei/work/stego_attack_workspace
bash scripts/run_gsd_native_smoke.sh
```

Default output:

```text
/data2/liyanlei/stego_attack_data/baselines/gsd/native_smoke
```

## Available Checkpoints

Available DDPM checkpoints:

```text
/data2/liyanlei/stego_attack_models/gsd/ddim_cache/diffusion_models_converted/ema_diffusion_cifar10_model/model-790000.ckpt
/data2/liyanlei/stego_attack_models/gsd/ddim_cache/diffusion_models_converted/ema_diffusion_lsun_bedroom_model/model-2388000.ckpt
```

The GSD README also asks for a CelebA-64 own-model checkpoint. It is available
on the data disk:

```text
/data2/liyanlei/stego_attack_models/gsd/celeba-64/ckpt.pth
```

It is linked to the README path:

```text
references/GSD/out/logs/celeba-64/ckpt.pth
```

The public sampling code's `CELEBA + 64` branch actually reads this hardcoded
path, so the same file is linked there as well:

```text
references/GSD/out/logs/bedroom-64/ckpt.pth
```

This is a path compatibility link only; it does not alter the GSD method.

## Verified Smoke

Previous CIFAR10 native smoke completed `--reverse_dct` sampling with 2
timesteps and printed bit accuracy around `0.9166`. This is a wiring check; use
the intended native checkpoint/config and more timesteps for formal evaluation.

## Identity Runner

The identity runner mirrors the official `sample_reverse_dct` logic: DCT-domain
sign payload, DDPM sampling, image quantization, DDIM reverse, and DCT sign
extraction. The only semantic substitution is that protocol bits replace the
official function's `np.random.randint` secret so samples are deterministic and
comparable.

Formal CIFAR10 command:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_gsd_identity.py \
  --count 500 --timesteps 1000 --save-images \
  --output-dir /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/gsd_cifar10
```

Output:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/gsd_cifar10/identity_results.csv
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/gsd_cifar10/manifest.json
```
