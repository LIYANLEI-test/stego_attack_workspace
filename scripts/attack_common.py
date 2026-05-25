#!/usr/bin/env python3
"""Shared image-domain attack helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image


RESIZE_INTERPOLATION = Image.Resampling.BILINEAR


def resize_roundtrip_pil(image: Image.Image, factor: float) -> Image.Image:
    """Resize by factor and back to the original size with fixed interpolation."""
    if factor <= 0:
        raise ValueError(f"resize factor must be positive, got {factor}")
    rgb = image.convert("RGB")
    width, height = rgb.size
    attack_width = max(1, int(round(width * factor)))
    attack_height = max(1, int(round(height * factor)))
    attacked = rgb.resize((attack_width, attack_height), RESIZE_INTERPOLATION)
    return attacked.resize((width, height), RESIZE_INTERPOLATION)


def resize_roundtrip_array_rgb(image: np.ndarray, factor: float) -> np.ndarray:
    attacked = resize_roundtrip_pil(Image.fromarray(image.astype(np.uint8), "RGB"), factor)
    return np.asarray(attacked, dtype=np.uint8)


def resize_roundtrip_file(input_path: Path, output_path: Path, factor: float) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    attacked = resize_roundtrip_pil(Image.open(input_path), factor)
    attacked.save(output_path)


def tensor_minus1_1_to_pil(tensor_chw: torch.Tensor) -> Image.Image:
    array = (
        ((tensor_chw.detach().float().cpu() / 2.0 + 0.5).clamp(0, 1) * 255.0)
        .round()
        .to(torch.uint8)
        .permute(1, 2, 0)
        .numpy()
    )
    return Image.fromarray(array, "RGB")


def pil_to_tensor_minus1_1(image: Image.Image, device: torch.device | str, dtype: torch.dtype) -> torch.Tensor:
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)
    return (tensor * 2.0 - 1.0).to(device=device, dtype=dtype)


def resize_roundtrip_tensor_minus1_1(tensor_bchw: torch.Tensor, factor: float) -> torch.Tensor:
    if tensor_bchw.ndim != 4 or tensor_bchw.shape[0] != 1 or tensor_bchw.shape[1] != 3:
        raise ValueError(f"expected tensor shape [1,3,H,W], got {tuple(tensor_bchw.shape)}")
    attacked = resize_roundtrip_pil(tensor_minus1_1_to_pil(tensor_bchw[0]), factor)
    return pil_to_tensor_minus1_1(attacked, tensor_bchw.device, tensor_bchw.dtype)


def tensor_0_1_to_pil(tensor_chw: torch.Tensor) -> Image.Image:
    array = (
        (tensor_chw.detach().float().cpu().clamp(0, 1) * 255.0)
        .round()
        .to(torch.uint8)
        .permute(1, 2, 0)
        .numpy()
    )
    return Image.fromarray(array, "RGB")


def pil_to_tensor_0_1(image: Image.Image, device: torch.device | str, dtype: torch.dtype) -> torch.Tensor:
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0).to(device=device, dtype=dtype)


def resize_roundtrip_tensor_0_1(tensor_bchw: torch.Tensor, factor: float) -> torch.Tensor:
    if tensor_bchw.ndim != 4 or tensor_bchw.shape[0] != 1 or tensor_bchw.shape[1] != 3:
        raise ValueError(f"expected tensor shape [1,3,H,W], got {tuple(tensor_bchw.shape)}")
    attacked = resize_roundtrip_pil(tensor_0_1_to_pil(tensor_bchw[0]), factor)
    return pil_to_tensor_0_1(attacked, tensor_bchw.device, tensor_bchw.dtype)
