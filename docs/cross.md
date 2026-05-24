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

The workspace runner calls the official `demo.py` directly and only adds cache,
output-directory, and manifest handling:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/generate_cross_sample.py
```

Default output:

```text
/data2/liyanlei/stego_attack_data/baselines/cross/native_official/sample_000001/gt.png
/data2/liyanlei/stego_attack_data/baselines/cross/native_official/sample_000001/hide.png
/data2/liyanlei/stego_attack_data/baselines/cross/native_official/sample_000001/reverse.png
/data2/liyanlei/stego_attack_data/baselines/cross/native_official/sample_000001/manifest.json
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

## Notes

CRoSS is image-based. A single smoke run needs one input image plus private and
public text keys. The Stego260 dataset mentioned in the official README is for
larger evaluation, not for the basic native demo.

For this workspace's image-payload experiments, use the fixed FFHQ secret
image set:

```text
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/images
```
