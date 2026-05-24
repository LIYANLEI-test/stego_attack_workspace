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
  scripts/run_diffusion_stego_identity.py \
  --mapping mn --count 500 --skip-image \
  --output-dir /data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/diffusion_stego_mn_projection
```

Default output:

```text
/data2/liyanlei/stego_attack_data/identity_runs/native_identity_20260522/diffusion_stego_<mapping>_projection
```

## Label

Keep this labelled:

```text
nsdser_reference
```

It is not `native_official`, because the current integration follows
NS-DSer's bundled comparison implementation rather than a separate official
Diffusion-Stego repository.

## Identity Results

Projection-only identity is complete for all variants:

```text
diffusion_stego_mn_projection:         500/500 exact
diffusion_stego_mb_projection:         500/500 exact
diffusion_stego_mc_projection:         500/500 exact
diffusion_stego_multi_bits_projection: 500/500 exact
```

These runs verify the reference `Projection.encode_message` and
`Projection.decode_message` mappings with protocol payloads. They intentionally
skip SD image generation and inversion. Full image-path pilots at 2 steps ran,
but had low bit accuracy; do not report them as paper-level recovery results.
