# UnMarker Attack Candidate Smoke - 2026-05-26

## Suitability Decision

`andrekassis/ai-watermark` is not suitable as an additional hiding or
steganography baseline. It is the official code for **UnMarker: A Universal
Attack on Defensive Image Watermarking** (IEEE S&P 2025), so its correct role in
this project is an **attack-method candidate**.

It is potentially useful for the paper comparison because UnMarker is a recent,
published, detector-feedback-free image-domain attack against robust defensive
watermarks. The caveat is important: the original paper evaluates watermark
detectors, not hidden-message recovery for generative steganography. Any result
here must be labeled as an adapted steganographic recovery attack, not as a
native UnMarker paper result.

Reference checkout:

```text
references/ai-watermark
https://github.com/andrekassis/ai-watermark
commit 58ba69259dd1bd3391bf9c8b0fe93912df0125b1
```

## Local Adapter

The adapter is intentionally thin:

```text
scripts/unmarker_attack.py
scripts/run_gsd_identity.py --attack-kind unmarker
```

It imports the official UnMarker coordinate optimization core from
`references/ai-watermark/modules/attack/unmark/cw.py`, then exposes it as a
black-box image transform between stego generation and native recovery.

The adapter does **not** use the original repository's watermark-scheme harness,
because that harness first creates defensive watermarks and then evaluates
watermark detectors. That would not match this workspace's native stego
identity/recovery protocol.

## Smoke Run

Because the UnMarker README asks for a high-end GPU with at least 32 GB memory
and this machine has 12 GB GPUs, the first smoke used the lightweight GSD
CIFAR10 path rather than 512x512 image methods.

Command:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH CUDA_VISIBLE_DEVICES=0 \
  /data2/liyanlei/envs/stego_attack/bin/python scripts/run_gsd_identity.py \
  --count 10 \
  --timesteps 1000 \
  --device cuda \
  --attack-kind unmarker \
  --unmarker-stage high \
  --unmarker-profile smoke \
  --unmarker-iterations 25 \
  --save-images \
  --force \
  --output-dir /data2/liyanlei/stego_attack_data/attack_runs/unmarker_smoke_20260526/gsd_cifar10_unmarker_high_smoke_10
```

Result root:

```text
/data2/liyanlei/stego_attack_data/attack_runs/unmarker_smoke_20260526/gsd_cifar10_unmarker_high_smoke_10
```

## Result Summary

| Method | Attack | Rows | Failures | Main metric | Runtime |
|--------|--------|------|----------|-------------|---------|
| GSD CIFAR10 `native_official` | UnMarker-core high-frequency smoke | 10 | 0 | mean bit accuracy 0.765430 | mean 34.61 s/sample |

Additional image perturbation metrics over saved stego/attacked pairs:

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| stego-vs-attacked PSNR | 45.083339 dB | 45.036498 dB | 45.175992 dB |
| stego-vs-attacked MAE | 1.336328 | 1.322266 | 1.344401 |

For context, the formal GSD CIFAR10 identity mean bit accuracy is about 0.874.
This smoke reduced the 10-sample mean to 0.765430, so it has a real degradation
signal while preserving high image PSNR on 32x32 outputs.

## Interpretation

This is enough to keep UnMarker as a serious attack-method candidate. It is not
yet enough for a paper table:

- The run is a 10-sample smoke on GSD CIFAR10 only.
- The profile is a local lightweight `smoke` configuration, not the full
  scheme-specific UnMarker paper configuration.
- The original UnMarker objective targets defensive watermark removal; our
  metric is native hidden-message recovery after attack.
- Full 512x512 methods may need a larger GPU or carefully staged low/high
  frequency settings.

## Next Decision

Include UnMarker in the stronger attack design as:

```text
attack label: unmarker_core_adapted
role: attack baseline candidate
provenance: official-core adapted
status: smoke-only until full-size settings are validated
```

Do not describe it as an additional steganography baseline.
