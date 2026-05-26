#!/usr/bin/env python3
"""Selected quality-budget attack matrix for formal experiments.

These parameters were calibrated on 2026-05-27 under:
  stego-vs-attacked PSNR >= 30 dB and LPIPS <= 0.10

Keep this file as the single source of truth for formal selected-attack queues
and paper-table aggregation. Exploratory grids should use separate scripts.
"""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_FORMAL_COUNTS = {
    "cross": 100,
    "gsd_cifar10": 500,
    "mas_grdh": 500,
    "mddm_128_pilot": 50,
    "pulsar": 500,
}


@dataclass(frozen=True)
class SelectedAttack:
    method: str
    attack: str
    factor: str
    label: str
    metric: str
    provenance: str
    note: str = ""

    @property
    def safe_factor(self) -> str:
        return self.factor.replace(".", "_").replace("-", "_")

    @property
    def name_part(self) -> str:
        return f"{self.attack}_{self.safe_factor}"


SELECTED_ATTACKS: tuple[SelectedAttack, ...] = (
    SelectedAttack("cross", "resize", "1.5", "resize_1_5", "recovery_psnr", "native_official"),
    SelectedAttack("cross", "jpeg", "50", "jpeg_q50", "recovery_psnr", "native_official"),
    SelectedAttack("cross", "mblur", "3", "median_blur_k3", "recovery_psnr", "native_official"),
    SelectedAttack("cross", "gblur", "3", "gaussian_blur_k3", "recovery_psnr", "native_official"),
    SelectedAttack("cross", "regen_vae", "5", "regen_vae_q5", "recovery_psnr", "adapted_attack"),
    SelectedAttack("gsd_cifar10", "resize", "1.25", "resize_1_25", "bit_accuracy", "native_official"),
    SelectedAttack("gsd_cifar10", "jpeg", "80", "jpeg_q80", "bit_accuracy", "native_official"),
    SelectedAttack("gsd_cifar10", "regen_vae", "6", "regen_vae_q6", "bit_accuracy", "adapted_attack"),
    SelectedAttack(
        "gsd_cifar10",
        "unmarker",
        "high_smoke_25",
        "unmarker_high_smoke_25",
        "bit_accuracy",
        "adapted_attack",
        "GSD-only smoke-profile UnMarker candidate.",
    ),
    SelectedAttack("mas_grdh", "resize", "1.5", "resize_1_5", "bit_accuracy", "native_official"),
    SelectedAttack("mas_grdh", "jpeg", "50", "jpeg_q50", "bit_accuracy", "native_official"),
    SelectedAttack("mas_grdh", "regen_vae", "6", "regen_vae_q6", "bit_accuracy", "adapted_attack"),
    SelectedAttack(
        "mddm_128_pilot",
        "jpeg",
        "70",
        "jpeg_q70",
        "bit_accuracy",
        "native_third_party",
        "Pilot only; not official author code.",
    ),
    SelectedAttack(
        "pulsar",
        "resize",
        "1.25",
        "resize_1_25",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures within quality budget.",
    ),
    SelectedAttack(
        "pulsar",
        "jpeg",
        "95",
        "jpeg_q95",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures within quality budget.",
    ),
    SelectedAttack(
        "pulsar",
        "mblur",
        "3",
        "median_blur_k3",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures within quality budget.",
    ),
    SelectedAttack(
        "pulsar",
        "gblur",
        "3",
        "gaussian_blur_k3",
        "bit_accuracy",
        "native_official",
        "Calibration produced native reveal failures within quality budget.",
    ),
    SelectedAttack(
        "pulsar",
        "regen_vae",
        "6",
        "regen_vae_q6",
        "bit_accuracy",
        "adapted_attack",
        "Calibration produced native reveal failures within quality budget.",
    ),
)


def selected_for_methods(methods: set[str] | None = None) -> list[SelectedAttack]:
    if methods is None:
        return list(SELECTED_ATTACKS)
    return [item for item in SELECTED_ATTACKS if item.method in methods]


def default_count_for(method: str) -> int:
    try:
        return DEFAULT_FORMAL_COUNTS[method]
    except KeyError as exc:
        raise ValueError(f"unsupported method for selected attack matrix: {method}") from exc
