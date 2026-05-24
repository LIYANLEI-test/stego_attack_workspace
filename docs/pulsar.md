# Pulsar Baseline

Pulsar is a published generative steganography baseline:

```text
Pulsar: Secure Steganography through Diffusion Models
```

Official code:

```text
references/pulsar
https://github.com/spacelab-ccny/pulsar
```

## Native Path

Pulsar does not need an image dataset to generate attack objects. It uses an
unconditional DDPM model, a key, a seed, and a message.

The official repository uses public Hugging Face DDPMs, for example:

```text
google/ddpm-church-256
google/ddpm-celebahq-256
google/ddpm-bedroom-256
google/ddpm-cat-256
```

The native Sage/region path is exposed through:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_pulsar_native_regions_sample.py \
  --steps 50 --region-estimate-samples 1 --hist-bins 100
```

The helper `scripts/pulsar_native_utils.py` only handles cache setup, importing
the official checkout, and pointing the official Sage wrapper at
`references/pulsar/sage`.

## Sage Check

SageMath is installed at:

```text
/data2/liyanlei/envs/stego_attack/bin/sage
```

Run a tiny official encode/decode check with:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/pulsar_sage_smoke.py
```

## Verified Smoke

Previous native smoke:

```text
output: /data2/liyanlei/stego_attack_data/baselines/pulsar/native_regions_verify_50step
estimated capacity: 228 bytes
bit accuracy: 1.0
message match: true
```

Large model files are cached under `/data2/liyanlei/huggingface`.
