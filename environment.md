# Project Environment

Use one shared environment for this workspace:

```text
/data2/liyanlei/envs/stego_attack
```

Common commands:

```sh
conda activate stego_attack
```

or without activation:

```sh
env -u LD_LIBRARY_PATH PATH=/data2/liyanlei/envs/stego_attack/bin:$PATH /data2/liyanlei/envs/stego_attack/bin/python <script.py>
```

This environment includes:

- Python 3.10
- PyTorch CUDA 12.1
- Diffusers / Transformers / Accelerate
- OpenCV / Pillow / NumPy
- Pulsar dependencies
- GSD native smoke dependencies: Torch-DCT / LMDB / TensorBoard / gdown
- MAS/GRDH native smoke dependencies: OmegaConf / Einops / Kornia /
  PyTorch-Lightning 1.9.5 / Albumentations / pudb
- NS-DSer Diffusion-Stego reference runner dependencies: Click / Timm
- SageMath 10.5

Large Hugging Face caches are kept under:

```text
/data2/liyanlei/huggingface
```

Large method-specific model assets are kept under:

```text
/data2/liyanlei/stego_attack_models
```
