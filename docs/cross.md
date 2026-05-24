# CRoSS Baseline

CRoSS is a published steganography baseline:

```text
CRoSS: Diffusion Model Makes Controllable, Robust and Secure Image Steganography
NeurIPS 2023
```

Official code:

```text
references/CRoSS
https://github.com/yujiwen/CRoSS
```

## Native Path

The identity runner imports the official `demo.py`, constructs
`demo.ODESolve`, and calls the same image-to-noise-to-image and reveal sequence
used by the official demo. It only adds protocol image selection, cache setup,
output-directory handling, CSV rows, and a manifest:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_cross_identity.py \
  --count 100 --num-steps 50 \
  --output-dir /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/cross
```

Default output:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/cross/samples/<index>/gt.png
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/cross/samples/<index>/hide.png
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/cross/samples/<index>/reverse.png
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/cross/identity_results.csv
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/cross/manifest.json
```

The compatibility shell entry is:

```sh
scripts/run_cross_official_demo.sh
```

## Verified Smoke

Previous quick smoke:

```text
/data2/liyanlei/stego_attack_data/baselines/cross/native_official_smoke_2step/hide.png
/data2/liyanlei/stego_attack_data/baselines/cross/native_official_smoke_2step/reverse.png
/data2/liyanlei/stego_attack_data/baselines/cross/native_official_smoke_2step/manifest.json
```

The 2-step identity smoke produced non-exact pixel recovery with PSNR around
`22.859`, which is expected for a very short DDIM run and is not a runner
failure.

## Notes

CRoSS is image-based. A single smoke run needs one input image plus private and
public text keys. The Stego260 dataset mentioned in the official README is for
larger evaluation, not for the basic native demo.

For this workspace's image-payload experiments, use the fixed FFHQ secret
image set:

```text
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/images
```
