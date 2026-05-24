# MDDM Baseline

MDDM refers to the ICML 2025 method:

```text
MDDM: Practical Message-Driven Generative Image Steganography Based on Diffusion Models
```

Paper:

```text
https://proceedings.mlr.press/v267/xu25ah.html
```

## Reference Code Status

No official author repository has been found locally. The currently integrated
path is a third-party public repository:

```text
references/MDDM-thirdparty
https://github.com/RGlodAkshat/MDDM-Generative-Image-Steganography-Based-on-Diffusion-Models
```

Keep this labelled:

```text
native_third_party
```

not `native_official`.

The third-party backend pipeline follows the public MDDM mechanism: Cardan
grille latent positions, sign-separated truncated Gaussian tails, Stable
Diffusion generation, DDIM inversion, and sign-based extraction.

## Native Third-Party Path

Run:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_mddm_thirdparty_sample.py
```

Default output:

```text
/data2/liyanlei/stego_attack_data/baselines/mddm/thirdparty_native
```

## Verified Smoke

Previous third-party native smoke:

```text
/data2/liyanlei/stego_attack_data/baselines/mddm/thirdparty_native_smoke_2step
bit_accuracy=1.000000
exact_match=True
```

This is suitable as an attack object only with the clear
`native_third_party` label.
