#!/usr/bin/env python3
"""Thin adapter for UnMarker-style image-domain attacks.

The source method is:
  UnMarker: A Universal Attack on Defensive Image Watermarking
  https://github.com/andrekassis/ai-watermark

This adapter intentionally uses the public repository as a reference checkout,
but does not use its watermarking-scheme evaluation harness. It exposes the
spectral optimization primitive as a black-box image transform so our native
stego recovery runners can test whether it is a useful attack candidate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from torchvision import transforms


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UNMARKER_ROOT = WORKSPACE_ROOT / "references" / "ai-watermark"


def _patch_optional_imports() -> None:
    """Provide tiny compatibility shims for optional UnMarker imports.

    The official `cw.py` imports `pytorch_forecasting.utils.unsqueeze_like`.
    We only need that helper, so a local shim avoids pulling in the full
    forecasting stack for this adapter.
    """

    if "pytorch_forecasting.utils" in sys.modules:
        return
    import types

    pkg = types.ModuleType("pytorch_forecasting")
    utils = types.ModuleType("pytorch_forecasting.utils")

    def unsqueeze_like(source: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        while source.ndim < target.ndim:
            source = source.unsqueeze(-1)
        return source

    utils.unsqueeze_like = unsqueeze_like
    pkg.utils = utils
    sys.modules.setdefault("pytorch_forecasting", pkg)
    sys.modules.setdefault("pytorch_forecasting.utils", utils)


class FFTLoss(torch.nn.Module):
    def __init__(self, norm: int = 1, power: int = 1) -> None:
        super().__init__()
        self.norm = norm
        self.power = power

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        x_f = torch.fft.fftshift(torch.fft.fft2(torch.fft.ifftshift(x, dim=(-1, -2))), dim=(-1, -2))
        y_f = torch.fft.fftshift(torch.fft.fft2(torch.fft.ifftshift(y, dim=(-1, -2))), dim=(-1, -2))
        diff = x_f - y_f
        flat = diff.reshape(diff.shape[0], -1)
        return torch.pow(torch.linalg.vector_norm(flat, ord=self.norm, dim=1), self.power).view(-1, 1) / x[0].numel()


class MeanLoss(torch.nn.Module):
    def __init__(self, kernels: list[tuple[int, int]] | None = None) -> None:
        super().__init__()
        self.kernels = kernels or [(5, 5)]

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        losses = []
        for kernel in self.kernels:
            pad = (kernel[1] // 2, kernel[1] // 2, kernel[0] // 2, kernel[0] // 2)
            x_pool = F.avg_pool2d(F.pad(x, pad, mode="reflect"), kernel_size=kernel, stride=1)
            y_pool = F.avg_pool2d(F.pad(y, pad, mode="reflect"), kernel_size=kernel, stride=1)
            losses.append((x_pool - y_pool).abs().flatten(1).mean(1, keepdim=True))
        return torch.stack(losses, dim=0).sum(0)


class NormLoss(torch.nn.Module):
    def __init__(self, norm: int = 2, power: int = 2) -> None:
        super().__init__()
        self.norm = norm
        self.power = power

    def forward(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        flat = (x - y).reshape(x.shape[0], -1)
        return torch.pow(torch.linalg.vector_norm(flat, ord=self.norm, dim=1), self.power).view(-1, 1) / x[0].numel()


def pil_to_tensor(image, device: torch.device) -> torch.Tensor:
    tensor = transforms.ToTensor()(image.convert("RGB")).unsqueeze(0)
    return tensor.to(device=device, dtype=torch.float32)


def tensor_to_pil(tensor: torch.Tensor):
    return transforms.ToPILImage()(tensor.detach().cpu().squeeze(0).clamp(0, 1))


def load_special_cw(unmarker_root: Path = DEFAULT_UNMARKER_ROOT):
    _patch_optional_imports()
    module_root = unmarker_root / "modules" / "attack" / "unmark"
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))
    from cw import SpecialCWCoordinate  # type: ignore

    return SpecialCWCoordinate


def apply_unmarker_core_tensor(
    tensor_bchw: torch.Tensor,
    *,
    stage: str = "high",
    profile: str = "smoke",
    max_iterations: int | None = None,
    binary_search_steps: int = 1,
    loss_thresh: float | None = None,
    unmarker_root: Path = DEFAULT_UNMARKER_ROOT,
) -> torch.Tensor:
    """Apply an UnMarker-style spectral perturbation to a [0,1] image tensor.

    `profile="smoke"` intentionally keeps iterations low for feasibility checks
    on 12GB GPUs. Full paper-scale UnMarker parameters are much heavier and are
    scheme-specific.
    """

    if tensor_bchw.ndim != 4 or tensor_bchw.shape[1] != 3:
        raise ValueError(f"expected [B,3,H,W] tensor, got {tuple(tensor_bchw.shape)}")
    if stage not in {"high", "low"}:
        raise ValueError(f"stage must be high or low, got {stage!r}")
    if profile not in {"smoke", "paper_like"}:
        raise ValueError(f"profile must be smoke or paper_like, got {profile!r}")

    SpecialCWCoordinate = load_special_cw(unmarker_root)
    device = tensor_bchw.device
    x = tensor_bchw.detach().float().clamp(0, 1)

    if stage == "high":
        est = NormLoss(norm=2, power=2).to(device) if profile == "smoke" else FFTLoss(norm=1, power=1).to(device)
        dist = FFTLoss(norm=1, power=1).to(device)
        optimizer_args = {
            "type": "Adam",
            "regularization": {"type": "l2", "factor": 0.6, "thresh": 1.0e-4},
            "max_grad_l_inf": 0.005,
            "learning_rate": {"values": [0.0002], "scheduler": None},
            "tanh_space": False,
            "scale_mode": "fp32",
        }
        stage_args = {
            "modifier_type": "RGB",
            "filter_args": {
                "loss_factor": 0,
                "box": (1, 1),
                "kernels": None,
                "sigma_color": 0.1,
                "norm": 1,
                "pad_mode": "reflect",
                "filter_mode": False,
                "loss_norm": 2,
            },
            "max_iterations": max_iterations or (25 if profile == "smoke" else 500),
            "initial_const": 1.0e6,
        }
        threshold = loss_thresh if loss_thresh is not None else 1.0e-4
    else:
        est = NormLoss(norm=2, power=2).to(device)
        dist = MeanLoss(kernels=[(3, 3)] if profile == "smoke" else [(5, 5)]).to(device)
        kernels = [(5, 5)] if profile == "smoke" else [(21, 5), (5, 5), (17, 33), (7, 7), (47, 5), (33, 17), (17, 17), (5, 5), (3, 3)]
        optimizer_args = {
            "type": "Adam",
            "regularization": {"type": "l2", "factor": 2.5e-4},
            "max_grad_l_inf": 1.0,
            "learning_rate": {"values": [0.01 for _ in range(len(kernels) + 1)], "scheduler": None},
            "scale_mode": "fp32",
        }
        stage_args = {
            "modifier_type": "RGB",
            "filter_args": {
                "loss_factor": 0.5 if profile == "smoke" else 5,
                "box": (1, 1),
                "kernels": kernels,
                "sigma_color": 0.05,
                "norm": 1,
                "pad_mode": "reflect",
                "filter_mode": False,
                "loss_norm": 2,
            },
            "max_iterations": max_iterations or (25 if profile == "smoke" else 500),
            "initial_const": 1.0e6,
        }
        threshold = loss_thresh if loss_thresh is not None else 1.0e-3

    attack = SpecialCWCoordinate(
        est,
        dist,
        evalu=None,
        optimizer_args=optimizer_args,
        binary_search_steps=binary_search_steps,
        clip_min=0.0,
        clip_max=1.0,
        tanh_space=optimizer_args.get("tanh_space", True),
        # Official Bar currently assumes the tqdm object exists even when
        # `verbose=False`, so keep it enabled for this thin adapter.
        progress_bar_args={"verbose": True},
        device=str(device),
        **stage_args,
    )
    return attack(x, x, ox=x, thresh=float(threshold))


def apply_unmarker_core_pil(
    image,
    *,
    stage: str = "high",
    profile: str = "smoke",
    max_iterations: int | None = None,
    binary_search_steps: int = 1,
    loss_thresh: float | None = None,
    device: str = "cuda",
    unmarker_root: Path = DEFAULT_UNMARKER_ROOT,
):
    torch_device = torch.device(device if torch.cuda.is_available() else "cpu")
    tensor = pil_to_tensor(image, torch_device)
    attacked = apply_unmarker_core_tensor(
        tensor,
        stage=stage,
        profile=profile,
        max_iterations=max_iterations,
        binary_search_steps=binary_search_steps,
        loss_thresh=loss_thresh,
        unmarker_root=unmarker_root,
    )
    return tensor_to_pil(attacked)
