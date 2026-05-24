# Native Code Audit

Audit date: 2026-05-24

This workspace is for steganographic message-destruction research. The current
task is the identity / clean-recovery baseline before attack experiments.

The project rule is:

```text
use native original-repository generation whenever practical
```

This audit checks whether the workspace code follows that rule and records the
places where local compatibility changes are required.

## Task Fit

The workspace matches the current task framing:

- bit-payload identity runs use protocol `native_identity_v1_20260522`;
- the shared seed is `stego-attack-native-identity-v1-20260522`;
- generated data, model weights, Hugging Face caches, and experiment results
  live under `/data2/liyanlei/...`;
- top-level scripts are thin runners, protocol builders, or manifest writers;
- no workspace replacement implementation under `src/stego_baselines` is
  present;
- Diffusion-Stego is explicitly labelled as an NS-DSer reference integration,
  not as an official native checkout;
- MDDM is explicitly labelled as third-party code, not official author code.

The accurate claim is therefore:

```text
native original-repository generation as far as practical, with documented
third-party/reference exceptions and local compatibility patches
```

It should not be described as every reference checkout being pristine.

## Reference Checkouts

| Method | Label | Local path | Origin | Commit | Status |
|---|---|---|---|---|---|
| CRoSS | `native_official` | `references/CRoSS` | `https://github.com/yujiwen/CRoSS.git` | `ebc85c363eb60166efda7417f415e13e2038694f` | clean |
| Pulsar | `native_official` | `references/pulsar` | `https://github.com/spacelab-ccny/pulsar.git` | `52c2639767705922e9686d1d06d831fd167b98e1` | clean |
| GSD | `native_official` | `references/GSD` | `https://github.com/zqqq2/Improved-Generative-Steganography-Based-on-Diffusion-Model-code-2025.git` | `6012e9d19dafbda23bc56536c2bd3c8628026832` | untracked local checkpoint/config links under `out/logs/` |
| MAS/GRDH | `native_official` | `references/mas_GRDH` | `https://github.com/HXX5656/mas_GRDH.git` | `540cc36c54ab7161930d12973a4bfa7c38168541` | untracked compatibility shim `ldm/lr_scheduler.py` |
| MDDM | `native_third_party` | `references/MDDM-thirdparty` | `https://github.com/RGlodAkshat/MDDM-Generative-Image-Steganography-Based-on-Diffusion-Models.git` | `240a1de4d2d78a8c168b7b89577f4762af42a8c8` | clean |
| RGS | `native_official` | `references/RGS` | `https://github.com/FBW-JNU/RGS.git` | `56708d6b2a2d019ae436eb6f0b8c7f53cadaa751` | local compatibility changes plus generated caches/weights |

## Method Notes

### CRoSS

`scripts/generate_cross_sample.py` calls the official `references/CRoSS/demo.py`
entry point. The wrapper only sets model cache paths, passes demo arguments, and
writes a manifest.

This is a native official path for smoke and image-payload baseline generation.

### Pulsar

`scripts/pulsar_native_utils.py`, `scripts/run_pulsar_native_regions_sample.py`,
and `scripts/run_pulsar_identity.py` import `references/pulsar/pulsar.py` and
use the official `Pulsar.estimate_regions`,
`Pulsar.generate_with_regions`, and `Pulsar.reveal_with_regions` path with
Sage.

`scripts/run_pulsar_identity.py` now records per-sample failures in
`identity_failures.csv` and continues the run. This is runner robustness, not a
method change.

### GSD

`scripts/run_gsd_native_smoke.sh` runs `references/GSD/main.py` with
`--sample --reverse_dct`, which dispatches to the repository's native
`sample_reverse_dct` path in `references/GSD/runners/diffusion.py`.

The untracked `references/GSD/out/logs/...` files are local runtime checkpoint
links/configs required by the public repository layout. They should remain
ignored and documented, not committed into the nested repository.

### MAS/GRDH

`scripts/run_mas_grdh_native_smoke.sh` calls the official
`references/mas_GRDH/scripts/txt2img.py` entry point. The helper
`scripts/prepare_mas_grdh_native.py` copies the official YAML structure and
points the CLIP path at the local `/data2` model directory.

The public checkout references `ldm.lr_scheduler.LambdaLinearScheduler`, but the
file is absent from the checkout. The local file
`references/mas_GRDH/ldm/lr_scheduler.py` is a Stable Diffusion LDM-compatible
scheduler shim. It only satisfies the config import and is stored as
`patches/mas-grdh-lr-scheduler-shim.patch`.

### MDDM

`scripts/run_mddm_thirdparty_sample.py` and `scripts/run_mddm_identity.py` use
`references/MDDM-thirdparty/backend/pipeline.py` directly.

The repository is not confirmed as official author code. The workspace labels it
`native_third_party`, which is correct.

### Diffusion-Stego

`scripts/run_diffusion_stego_nsdser_sample.py` imports the supplied NS-DSer
reference implementation from:

```text
/home/liyanlei/work/NS-DSer-master/NS-DSer-master/utils/projection.py
/home/liyanlei/work/NS-DSer-master/NS-DSer-master/ldm/models/diffusion/heun.py
```

This remains labelled `nsdser_reference`, not `native_official`.

### RGS

`scripts/run_rgs_native_sample.py` calls `references/RGS/hide_and_reveal.py`.
The local RGS checkout has compatibility edits stored in
`patches/rgs-local-compat.patch`:

- model paths are parameterized through environment variables;
- `HF_TOKEN` is optional when local weights are used;
- CLIP output dtype is converted to the UNet dtype;
- output directory, JPEG quality, Gaussian variance, step count,
  `--hide_only`, and `--identity_only` are command-line options.

These edits keep the official hide-and-reveal algorithm path but make it usable
in this workspace and with local assets.

## Identity Baseline State

The identity protocol files exist under:

```text
/data2/liyanlei/stego_attack_data/protocols/native_identity_v1_20260522
```

Current implemented identity runners:

- Pulsar: `scripts/run_pulsar_identity.py`
- MDDM: `scripts/run_mddm_identity.py`

Other methods currently have native smoke/sample runners and protocol payload
files, but not all have completed full 500-sample identity runners yet. That is
the next implementation gap before a complete identity table can be claimed.

## Git Management Decision

Use a top-level git repository for the workspace code and documentation. Track
the public repositories as submodules/gitlinks at their audited commits. Keep
large assets, generated results, caches, `__pycache__`, nested repository
runtime output, and `/data2` data out of git.

Local reference compatibility changes are stored as patch files under
`patches/` and can be re-applied with `scripts/apply_reference_patches.sh`.
