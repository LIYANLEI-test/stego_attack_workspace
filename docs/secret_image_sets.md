# Secret Image Sets

Image-payload steganography methods need secret images as payloads. These are
not training datasets for the diffusion models.

## FFHQ 100 512

Prepared set:

```text
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/images
```

Metadata:

```text
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/manifest.json
/data2/liyanlei/stego_attack_data/secret_images/ffhq_100_512/manifest.csv
```

Source:

```text
/data2/liyanlei/stego_attack_data/source_images/00000
```

This local source contains `1024x1024` RGB PNG images in FFHQ-style numbering.
The prepared set keeps a deterministic 100-image sample and resizes each image
to `512x512` PNG for CRoSS and RGS image-payload experiments.

Selection and preprocessing:

```text
count: 100
selection: deterministic random sample
seed: 20260522
preprocess: RGB conversion, centered square crop, LANCZOS resize
output size: 512x512 PNG
```

This set is intended for CRoSS and RGS identity/attack experiments.

The previous aligned-CelebA sample is no longer the active secret set. It was
moved to:

```text
/data2/liyanlei/stego_attack_data/secret_images/_deprecated/celeba_100_512
```
