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
  scripts/run_mddm_identity.py
```

Default output:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/mddm
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

## Identity Pilot Guidance

The protocol's full MDDM payload is 2048 printable ASCII bytes. Current pilots
show that high payload sizes are not reliably exact in this third-party path:

```text
2048-byte smoke: bit_accuracy about 0.909851, not exact.
256-byte 10-sample smoke: mean bit_accuracy about 0.948438, exact 3/10.
128-byte 2-step smoke: 1/1 exact.
```

Run larger low-payload pilots before any full-size MDDM claim, for example:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_mddm_identity.py \
  --count 50 --steps 20 --guidance-scale 1.0 --payload-bytes 128 \
  --output-dir /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/mddm_128_pilot
```

The 128-byte, 20-step pilot is a capacity exploration. Early rows were high
accuracy but not all exact, so it must not be reported as a completed formal
identity baseline.
