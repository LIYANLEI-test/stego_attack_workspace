#!/usr/bin/env python3
"""Regeneration attack adapters for image-domain stego destruction.

The primary reference method is WatermarkAttacker:
  Invisible Image Watermarks Are Provably Removable Using Generative AI
  https://github.com/XuandongZhao/WatermarkAttacker

This module exposes the paper's Regen-VAE family as a thin reusable transform.
It calls the same CompressAI model family used by the official repository, but
keeps the caller's image size unless the caller explicitly resizes elsewhere.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from PIL import Image


SUPPORTED_REGEN_VAE_MODELS = {
    "bmshj2018-factorized",
    "bmshj2018-hyperprior",
    "mbt2018-mean",
    "mbt2018",
    "cheng2020-anchor",
}


def _normalize_device(device: str | torch.device) -> str:
    torch_device = torch.device(device)
    if torch_device.type == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return str(torch_device)


@lru_cache(maxsize=16)
def load_regen_vae_model(model_name: str, quality: int, device: str):
    """Load and cache a CompressAI model used by WatermarkAttacker Regen-VAE."""

    if model_name not in SUPPORTED_REGEN_VAE_MODELS:
        supported = ", ".join(sorted(SUPPORTED_REGEN_VAE_MODELS))
        raise ValueError(f"unsupported Regen-VAE model {model_name!r}; supported: {supported}")
    if quality < 1:
        raise ValueError(f"regen quality must be >= 1, got {quality}")

    from compressai.zoo import (
        bmshj2018_factorized,
        bmshj2018_hyperprior,
        cheng2020_anchor,
        mbt2018,
        mbt2018_mean,
    )

    constructors = {
        "bmshj2018-factorized": bmshj2018_factorized,
        "bmshj2018-hyperprior": bmshj2018_hyperprior,
        "mbt2018-mean": mbt2018_mean,
        "mbt2018": mbt2018,
        "cheng2020-anchor": cheng2020_anchor,
    }
    model = constructors[model_name](quality=quality, pretrained=True)
    model = model.eval().to(device)
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    return model


def apply_regen_vae_tensor(
    tensor_bchw: torch.Tensor,
    *,
    model_name: str = "bmshj2018-factorized",
    quality: int = 3,
    device: str | torch.device | None = None,
) -> torch.Tensor:
    """Apply Regen-VAE to a [0,1] RGB tensor and return a tensor on input device.

    WatermarkAttacker's demo resizes every input to 512x512 before reconstruction.
    For this workspace, the native stego protocol already defines the evaluation
    image size, so this adapter preserves the tensor shape.
    """

    if tensor_bchw.ndim != 4 or tensor_bchw.shape[1] != 3:
        raise ValueError(f"expected [B,3,H,W] tensor, got {tuple(tensor_bchw.shape)}")

    input_device = tensor_bchw.device
    input_dtype = tensor_bchw.dtype
    model_device = _normalize_device(device or input_device)
    model = load_regen_vae_model(model_name, int(quality), model_device)

    x = tensor_bchw.detach().float().clamp(0, 1).to(device=model_device)
    with torch.no_grad():
        out = model(x)
        attacked = out["x_hat"].clamp(0, 1)
    return attacked.to(device=input_device, dtype=input_dtype)


def pil_to_tensor_0_1(image: Image.Image, device: str | torch.device = "cpu") -> torch.Tensor:
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0).to(device=device)


def tensor_0_1_to_pil(tensor_bchw: torch.Tensor) -> Image.Image:
    tensor_chw = tensor_bchw.detach().float().cpu().squeeze(0).clamp(0, 1)
    array = (tensor_chw.permute(1, 2, 0).numpy() * 255.0).round().astype(np.uint8)
    return Image.fromarray(array, "RGB")


def apply_regen_vae_pil(
    image: Image.Image,
    *,
    model_name: str = "bmshj2018-factorized",
    quality: int = 3,
    device: str | torch.device = "cuda",
) -> Image.Image:
    tensor = pil_to_tensor_0_1(image, _normalize_device(device))
    attacked = apply_regen_vae_tensor(tensor, model_name=model_name, quality=quality, device=device)
    return tensor_0_1_to_pil(attacked)


def apply_regen_vae_file(
    input_path: Path,
    output_path: Path,
    *,
    model_name: str = "bmshj2018-factorized",
    quality: int = 3,
    device: str | torch.device = "cuda",
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    attacked = apply_regen_vae_pil(Image.open(input_path), model_name=model_name, quality=quality, device=device)
    attacked.save(output_path)
