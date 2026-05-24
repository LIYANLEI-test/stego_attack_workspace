# Diffusion-Stego Baseline

Diffusion-Stego here refers to:

```text
Diffusion-Stego: Training-free Diffusion Generative Steganography via Message Projection
```

No official standalone repository is currently integrated in this workspace.
The local path is based on the implementation inside the authors' supplied
NS-DSer reference code:

```text
/home/liyanlei/work/NS-DSer-master/NS-DSer-master/utils/projection.py
```

Supported variants:

```text
mn
mb
mc
multi_bits
```

## Runner

Use:

```sh
cd /home/liyanlei/work/stego_attack_workspace
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH \
  /data2/liyanlei/envs/stego_attack/bin/python \
  scripts/run_diffusion_stego_nsdser_sample.py \
  --mapping mn --steps 2 --seeds 0
```

Default output:

```text
/data2/liyanlei/stego_attack_data/baselines/diffusion_stego/nsdser_reference/<mapping>/
```

## Label

Keep this labelled:

```text
nsdser_reference
```

It is not `native_official`, because the current integration follows
NS-DSer's bundled comparison implementation rather than a separate official
Diffusion-Stego repository.
