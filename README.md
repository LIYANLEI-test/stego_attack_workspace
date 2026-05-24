# Stego Attack Workspace

This is the working directory for steganographic message-destruction research.

The current baseline rule is:

```text
use native original-repository implementations whenever possible
```

Local compatibility adaptations are allowed when they only make the public code
runnable in this workspace, for example model/cache path configuration, output
directory plumbing, checkpoint links, missing import shims, or runner failure
logging. These adaptations must not change the method's core embedding,
sampling, inversion, decoding, ECC, payload mapping, or metric logic. Formal
results should be interpreted against the original paper settings and any
deviation must be documented.

Do not use `/home/liyanlei/work/NS-DSer-master` as an implementation source.
That code was only a reference from another unpublished project. This workspace
should keep published baselines under `references/` from their own public
repositories and call those repositories directly through thin runner scripts.
The exception is Diffusion-Stego, which you explicitly asked to integrate from
the supplied NS-DSer reference implementation.

## Current Attack Targets

Integrated native or native-like paths:

```text
CRoSS      official repository wrapper
Pulsar     official repository Sage/region path
GSD        official/public repository DDPM path
MAS/GRDH   official repository txt2img path
MDDM       third-party repository backend path, not official author code
Diffusion-Stego  NS-DSer reference implementation for MN/MB/MC/Multi-bits
RGS        official repository hide-and-reveal path
```

Removed from the current workspace:

```text
unified SD1.5/SD3 adaptation scripts
workspace reimplementations under src/stego_baselines
```

## Important Directories

```text
scripts/      thin runners for native repository code
configs/      native runner configs and small prompt files
docs/         method notes and local asset status
references/   public baseline repository checkouts
data/         small manifests or links only
```

Large files stay on the data disk:

```text
/data2/liyanlei/huggingface
/data2/liyanlei/stego_attack_models
/data2/liyanlei/stego_attack_data
```

Image-payload secret set for CRoSS/RGS:

```text
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/images
```

## Status

See:

```text
docs/native_generation_status.md
```
