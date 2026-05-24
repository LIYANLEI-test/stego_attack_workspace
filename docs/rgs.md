# RGS Baseline

RGS refers to the published TIFS 2025 method:

```text
Robust Generative Steganography for Image Hiding Using Concatenated Mappings
```

Official code:

```text
references/RGS
https://github.com/FBW-JNU/RGS
```

## Suitability

RGS is suitable as an attack object for this project. It hides a full-size
secret image into a diffusion-generated stego image and then recovers the secret
image through its reveal pipeline. That gives a concrete hidden payload to
destroy.

## Native Path

Run through the identity runner:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_rgs_identity.py \
  --count 100 --steps 50 \
  --output-dir /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/rgs
```

The wrapper calls the official:

```text
references/RGS/hide_and_reveal.py
```

Local compatibility patch only parameterizes hardcoded model/output paths,
step count, output directory, and whether built-in JPEG/Gaussian robustness
attacks are skipped. The identity run uses `--identity_only`, so it reveals the
unmodified stego image.

Verified smoke output:

```text
/data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step/results/00000/00000_stego.png
/data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step/results/00000/00000_secret.png
/data2/liyanlei/stego_attack_data/baselines/rgs/native_official_hideonly_2step/results/00000/00000_noise.pkl
```

The verified smoke used `--steps 2 --hide-only`, so it proves the official hide
path can generate a stego image and save the latent/noise side data. For reveal
quality tests, use the same runner with more steps and without `--hide-only`.

The 2-step identity reveal smoke completed with `indice_acc` about `0.80078`
and recovery PSNR about `19.434`. That is a short-step pilot, not a formal
quality claim.

## Assets

Downloaded/prepared:

```text
/data2/liyanlei/stego_attack_models/rgs/vqgan_code1024.pth
/data2/liyanlei/stego_attack_models/rgs/sd15-bin
/data2/liyanlei/stego_attack_models/mas_grdh/clip/clip-vit-large-patch14-local
```

The VQGAN checkpoint comes from the official RGS GitHub release.

## Notes

The official script reports that one image can take about 5 minutes. Use the
wrapper for single-image smoke tests first, then scale only when needed.

For this workspace's image-payload experiments, use the fixed FFHQ secret
image set:

```text
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/images
```
